import concurrent.futures
import multiprocessing

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from source.constants.harvard import HarvardConstants
from source.constants.learncafe import LearnConstants
from source.utils import Utils


class Webscraper:

    def __init__(self, harvard_accepted_categories, learncafe_accepted_categories):
        self.learncafe = LearnConstants()
        self.harvard = HarvardConstants()
        self.utils = Utils(4, 5)
        self.shared_result = multiprocessing.Manager().list()
        self.harvard_accepted_categories = harvard_accepted_categories
        self.learncafe_accepted_categories = learncafe_accepted_categories
        self.session = None
        self.driver = None
        self.TIMEOUT = 3
        print("Webscrapper class started")

    def _get_course_info_harvard(self, course):
        details = course.find(
                        "div", class_="group-details-inner")
        category_tag = course.find(
            "div", class_="field field---extra-field-pll-extra-field-subject field--name-extra-field-pll-extra-field-subject field--type- field--label-inline clearfix")

        if category_tag and category_tag.text.strip() in self.harvard_accepted_categories:
            category = category_tag.text.strip()  # Pode não ter, avaliar
        else:
            return {}

        period = details.find(
            "div", class_="field field---extra-field-pll-extra-field-duration field--name-extra-field-pll-extra-field-duration field--type- field--label-visually_hidden")

        if period:
            course_period = period.find(
                "div", class_="field__item").text
        else:
            # Vou ignorar cursos que não tem período estrito de tempo (quase sempre ainda não disponíveis)
            return {}

        price = details.find(
            "div", class_="field field---extra-field-pll-extra-field-price field--name-extra-field-pll-extra-field-price field--type- field--label-visually_hidden").find("div", class_="field__item").text
        course_title = course.find("h3")
        course_link = f"https://pll.harvard.edu{course_title.find('a')['href']}"

        course_request = self.session.get(course_link)
        course_soup = BeautifulSoup(
            course_request.content, "html.parser")
        course_details = course_soup.find(
            "div", class_="group-details cell").find("div", class_="group-details-inner").find(
                "div", class_="field field--name-field-topics field--type-entity-reference field--label-inline").find(
                    "div", class_="display-inline field__items").find_all("div", class_="topic-tag field__item")
        topics = [topic.text.strip() for topic in course_details]
        category = set([category] + topics)

        created_date = course_soup.find("div", class_="icon-calendar field field---extra-field-pll-extra-field-date field--name-extra-field-pll-extra-field-date field--type- field--label-visually_hidden").find("div", class_="field__item").text.split("-")[0]
        created_by = course_soup.find("div", class_="field field--name-field-faculty field--type-entity-reference field--label-above").find("div", class_="field field--name-title field--type-string field--label-hidden field__items").find("a").text
        
        course_dict = {
            "title": course_title.text.strip(),
            "period": self.utils.week_to_hour(course_period),
            "link": course_link,
            "price": price,
            "category": tuple(category),
            "created date": created_date,
            "created by": created_by

        }
        return course_dict


    def _get_courses_from_harvard(self, search_tags):
        all_results = []
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for tag in search_tags:
                url = f'{self.harvard.URL}{tag}'
                while True:
                    page = self.session.get(url)
                    soup = BeautifulSoup(page.content, "html.parser")
                    courses = soup.find_all("article")

                    for course in courses:
                        future = executor.submit(self._get_course_info_harvard, course)
                        futures.append(future)

                    pagination = soup.find("nav", attrs={"role": "navigation"})
                    if pagination:
                        next_page = pagination.find(
                            "li", class_="pager__item pager__item--next pagination-next")
                        if next_page:
                            url = "https://pll.harvard.edu/catalog" + \
                                next_page.find("a")['href']
                            continue
                    break
            
            for future in concurrent.futures.as_completed(futures):
                course_dict = future.result()
                all_results.append(course_dict)
                
        self.shared_result.extend(all_results)

    def _get_course_info_learn_cafe(self, course):
        category = course.find("span", class_="card-category")
        category_list = [c.text for c in category.find_all("span")]

        if not any(x in category_list for x in self.learncafe_accepted_categories):
            return {}

        hours = course.find("span", class_="card-hours")
        title = course.find("h5", class_="card-title")
        pricing = course.find("p", class_="card-price").find("b")

        if pricing.find("span"):
            pricing.find("span").decompose()

        
        course_page = self.session.get(course['href'])
        course_soup = BeautifulSoup(
            course_page.content, "html.parser")
        course_title = course_soup.find("h1").text
        course_info = course_soup.find("div", class_="row information-boxes mb-4")
        created_date = course_info.find_all("div", class_="true-center").pop(-1).find("p").text
        created_by = course_soup.find("div", class_="content-about position-relative").find("h5").text
        
        course_dict = {
            "title": course_title,
            "period": hours.text.strip(),
            "link": course['href'],
            "price": pricing.text.strip(),
            "category": tuple(category_list),
            "created date": created_date,
            "created by": created_by
        }
        return course_dict

    def _get_courses_from_learncafe(self, search_tags):
        all_results = []
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for tag in search_tags:
                url = f"{self.learncafe.URL}{tag}"
                while True:
                    page = self.session.get(url)
                    soup = BeautifulSoup(page.content, "html.parser")
                    results = soup.find(id="cursosLista")
                    courses = results.find_all("a", class_="card")

                    for course in courses:
                        future = executor.submit(self._get_course_info_learn_cafe, course)
                        futures.append(future)

                    pagination = soup.find("nav", attrs={"aria-label": "Paginação"})
                    if pagination:
                        next_page = pagination.find("li", class_="page-next")
                        if next_page:
                            url = "https://www.learncafe.com/cursos" + \
                                next_page.find("a")['href']
                            continue
                    break

            for future in concurrent.futures.as_completed(futures):
                course_dict = future.result()
                all_results.append(course_dict)
        
        self.shared_result.extend(all_results)
        
    def _get_course_info_pluralsight(self, course, search_tag):
        is_lab_label = course.find("div", class_="is-labs-label")
        if is_lab_label:
            return {}
        
        course_title = course.find("h3").find("strong").text.strip()
        created_by = course.find("h4").text.replace("by ", "").strip()
        period = course.find("div", class_="duration").text.strip()
        course_link = course.find("a", class_="browse-search-results-item-link")["href"]
        
        self.driver.get(course_link)

        wait = WebDriverWait(self.driver, self.TIMEOUT)
        try:
            wait.until(EC.presence_of_element_located((By.XPATH, "//h2[text()='Course info']")))
        except TimeoutException:
            print("TimeoutException", course_link)
            return {}
        
        soup = BeautifulSoup(self.driver.page_source, "html.parser")
        info_container = soup.find("h2", text="Course info").parent
        rows = info_container.find_all("div", class_="course-info-rows")
        
        created_date = None
        for row in rows:
            items = row.find_all("div", class_="course-info-row-item")
            if items[0].text == "Updated":
                created_date = items[1].text.strip()
                break
            
        price_info = soup.find("div", class_="cta-buttons").text.replace("Get started", " ").replace("\n", " ").strip()
        
        course_dict = {
            "title": course_title,
            "period": period,
            "link": course_link,
            "price": price_info,
            "category": tuple([search_tag.replace("+", " ").title()]), # Unir em caso de resultados repetidos
            "created date": created_date,
            "created by": created_by
        }
        

        return course_dict
        
        
    def _get_courses_from_pluralsight(self, search_tags):  
        all_results = []
             
        for tag in search_tags:
            self.driver.get(f"https://www.pluralsight.com/browse?=&q={tag}")
            wait = WebDriverWait(self.driver, 10)
            try:
                wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "browse-search-results-item")))
            except TimeoutException:
                break
            
            while True:
                soup = BeautifulSoup(self.driver.page_source, "html.parser")
                results = soup.find_all("li", class_="browse-search-results-item large-12 columns")
                
                self.driver.execute_script("window.open('about:blank', '_blank');")
                self.driver.switch_to.window(self.driver.window_handles[1])
                for course in results:
                    course_dict = self._get_course_info_pluralsight(course, tag)
                    if course_dict != {}:
                        all_results.append(course_dict)
                
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])
                                        
                try:
                    element_to_click = self.driver.find_element(By.XPATH, '//div[contains(@class, "pagination-button right") and not(contains(@class, "deactivated"))]')
                except NoSuchElementException:
                    break
                
                element_to_click.click()
                                
                wait = WebDriverWait(self.driver, self.TIMEOUT)
                try:
                    wait.until_not(EC.presence_of_element_located((By.CSS_SELECTOR, 'ul.browse-search-results-list.loading')))
                except TimeoutException:
                    print("TimeoutException trocando de página")        
        
        self.utils.save_pluralsight_results(all_results)
        
            
        

    # TODO -> now we have two functions for each step of the system processing but I think we can use one for both sites
    def run_processing_harvard(self, search_tags):
        self.session = requests.Session()
        with multiprocessing.Pool(processes=4) as pool:
            pool.map(self._get_courses_from_harvard, [(tag,) for tag in search_tags])
        self.session.close()

    def run_processing_learncafe(self, search_tags):
        self.session = requests.Session()
        with multiprocessing.Pool(processes=4) as pool:
            pool.map(self._get_courses_from_learncafe, [(tag,) for tag in search_tags])
        self.session.close()
        
    
    def run_processing_pluralsight(self, search_tags):
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options)
        self.session = requests.Session()
        
        self._get_courses_from_pluralsight(search_tags) # Não consegui com pool
        
        self.session.close()
        self.driver.quit()
        
            

    def get_results(self):
        return self.utils.save_results(list(self.shared_result))

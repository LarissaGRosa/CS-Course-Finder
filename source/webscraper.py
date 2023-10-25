import concurrent.futures
import requests
from bs4 import BeautifulSoup
from source.constants.harvard import HarvardConstants

from source.constants.learncafe import LearnConstants
from source.utils import Utils
import multiprocessing

class Webscraper:

    def __init__(self, harvard_accepted_categories, learncafe_accepted_categories):
        self.learncafe = LearnConstants()
        self.harvard = HarvardConstants()
        self.utils = Utils(4, 5)
        self.shared_result = multiprocessing.Manager().list()
        self.harvard_accepted_categories = harvard_accepted_categories
        self.learncafe_accepted_categories = learncafe_accepted_categories
        self.session = None
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


    def get_results(self):
        return self.utils.save_results(list(self.shared_result))

import json

import requests
from bs4 import BeautifulSoup


def get_courses_from_learncafe(search_tags, accepted_categories):
    all_results = []
    unique_courses = set()

    for tag in search_tags:
        url = f"https://www.learncafe.com/cursos?filter=all&q={tag}"
        while True:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")
            results = soup.find(id="cursosLista")
            courses = results.find_all("a", class_="card")

            for course in courses:
                category = course.find("span", class_="card-category")
                category_list = [c.text for c in category.find_all("span")]

                if not any(x in category_list for x in accepted_categories):
                    continue

                hours = course.find("span", class_="card-hours")
                title = course.find("h5", class_="card-title")
                pricing = course.find("p", class_="card-price").find("b")

                if pricing.find("span"):
                    pricing.find("span").decompose()

                if title.text.endswith("..."):
                    course_page = requests.get(course['href'])
                    course_soup = BeautifulSoup(
                        course_page.content, "html.parser")
                    course_title = course_soup.find("h1").text
                else:
                    course_title = title.text

                course_dict = {
                    "title": course_title,
                    "period": hours.text.strip(),
                    "link": course['href'],
                    "price": pricing.text.strip(),
                    "category": tuple(category_list)
                }

                if tuple(course_dict.values()) not in unique_courses:
                    unique_courses.add(tuple(course_dict.values()))
                    all_results.append(course_dict)

            pagination = soup.find("nav", attrs={"aria-label": "Paginação"})
            if pagination:
                next_page = pagination.find("li", class_="page-next")
                if next_page:
                    url = "https://www.learncafe.com/cursos" + \
                        next_page.find("a")['href']
                    continue
            break
    print("Cursos do LearnCafe buscados.")
    return all_results


def get_courses_from_harvard(search_tags, accepted_categories):
    all_results = []
    unique_courses = set()

    for tag in search_tags:
        url = f'https://pll.harvard.edu/catalog?keywords={tag}'
        while True:
            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")
            courses = soup.find_all("article")

            for course in courses:
                details = course.find(
                    "div", class_="group-details-inner")
                category_tag = course.find(
                    "div", class_="field field---extra-field-pll-extra-field-subject field--name-extra-field-pll-extra-field-subject field--type- field--label-inline clearfix")

                if category_tag and category_tag.text.strip() in accepted_categories:
                    category = category_tag.text.strip()  # Pode não ter, avaliar
                else:
                    continue

                period = details.find(
                    "div", class_="field field---extra-field-pll-extra-field-duration field--name-extra-field-pll-extra-field-duration field--type- field--label-visually_hidden")

                if period:
                    course_period = period.find(
                        "div", class_="field__item").text
                else:
                    # Vou ignorar cursos que não tem período estrito de tempo (quase sempre ainda não disponíveis)
                    continue

                price = details.find(
                    "div", class_="field field---extra-field-pll-extra-field-price field--name-extra-field-pll-extra-field-price field--type- field--label-visually_hidden").find("div", class_="field__item").text
                course_title = course.find("h3")
                course_link = f"https://pll.harvard.edu{course_title.find('a')['href']}"

                course_request = requests.get(course_link)
                course_soup = BeautifulSoup(
                    course_request.content, "html.parser")
                course_details = course_soup.find(
                    "div", class_="group-details cell").find("div", class_="group-details-inner").find(
                        "div", class_="field field--name-field-topics field--type-entity-reference field--label-inline").find(
                            "div", class_="display-inline field__items").find_all("div", class_="topic-tag field__item")
                topics = [topic.text.strip() for topic in course_details]
                category = set([category] + topics)

                course_dict = {
                    "title": course_title.text.strip(),
                    "period": course_period,
                    "link": course_link,
                    "price": price,
                    "category": tuple(category)
                }

                if tuple(course_dict.values()) not in unique_courses:
                    unique_courses.add(tuple(course_dict.values()))
                    all_results.append(course_dict)

            pagination = soup.find("nav", attrs={"role": "navigation"})
            if pagination:
                next_page = pagination.find(
                    "li", class_="pager__item pager__item--next pagination-next")
                if next_page:
                    url = "https://pll.harvard.edu/catalog" + \
                        next_page.find("a")['href']
                    continue
            break
    print("Cursos da Harvard buscados.")
    return all_results


def save_results(all_results):
    result_dict = {"length": len(all_results), "courses": all_results}

    with open("results.json", "w", encoding='utf-8') as f:
        json.dump(result_dict, f, indent=4, ensure_ascii=False)


def main():
    print("Processando...")

    search_tags = ["data+science", "programacao", "web",
                   "banco+de+dados", "machine+learning"]
    accepted_categories = {
        "Informática e internet", "Tecnologia da Informação"}
    learncafe = get_courses_from_learncafe(search_tags, accepted_categories)

    search_tags = ["data+science", "programming", "web",
                   "database", "machine+learning"]
    accepted_categories = {"Programming", "Data Science",
                           "Computer Science", "Machine Learning"}
    harvard = get_courses_from_harvard(search_tags, accepted_categories)

    all_courses = learncafe + harvard

    save_results(all_courses)

    print("Processo finalizado.")


if __name__ == "__main__":
    main()

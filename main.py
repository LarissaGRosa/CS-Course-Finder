import json

import requests
from bs4 import BeautifulSoup

print("Processando...")
all_results = []

# Learn Café
tags = ["data+science", "programacao", "web",
        "banco+de+dados", "machine+learning"]
accepted_categories = ["Informática e internet", "Tecnologia da Informação"]

unique_courses = set()
for i in tags:
    URL = "https://www.learncafe.com/cursos?filter=all&q="+i

    while True:
        page = requests.get(URL)
        soup = BeautifulSoup(page.content, "html.parser")

        results = soup.find(id="cursosLista")
        courses = results.find_all("a", class_="card")

        for c in courses:
            category = c.find("span", class_="card-category")
            category_list = [c.text for c in category.find_all("span")]

            if not any(x in category_list for x in accepted_categories):
                continue

            hours = c.find("span", class_="card-hours")
            title = c.find("h5", class_="card-title")

            pricing = c.find("p", class_="card-price").find("b")
            if pricing.find("span") is not None:
                pricing.find("span").decompose()

            # Pegar nome completo do curso caso esteja truncado
            if title.text.endswith("..."):
                course_page = requests.get(c['href'])
                course_soup = BeautifulSoup(course_page.content, "html.parser")
                course_title = course_soup.find("h1").text
            else:
                course_title = title.text

            course = {
                "title": course_title,
                "hours": hours.text.replace("h", "").strip(),
                "link": c['href'],
                "price": pricing.text.strip(),
                "category": tuple(category_list)
            }

            if tuple(course.values()) not in unique_courses:
                unique_courses.add(tuple(course.values()))
                all_results.append(course)

        pagination = soup.find("nav", attrs={"aria-label": "Paginação"})
        if pagination is not None:
            next_page = pagination.find("li", class_="page-next")
            if next_page is not None:
                URL = "https://www.learncafe.com/cursos" + \
                    next_page.find("a")['href']
                continue
        break

result_dict = {"length": len(all_results), "courses": all_results}

with open("results.json", "w", encoding='utf-8') as f:
    json.dump(result_dict, f, indent=4, ensure_ascii=False)

print("Processo finalizado.")

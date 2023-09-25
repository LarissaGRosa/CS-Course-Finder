import json

import requests
from bs4 import BeautifulSoup

tags = ["data+science", "programacao", "web", "banco+de+dados"]
all_results = []

for i in tags:
    URL = "https://www.learncafe.com/cursos?filter=all&q="+i
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.find(id="cursosLista")

    courses = results.find_all("a", class_="card")

    for c in courses:
        hours = c.find("span", class_="card-hours")
        title = c.find("h5", class_="card-title")
        pricing = c.find("p", class_="card-price").find("b")
        if pricing.find("span") is not None:
            pricing.find("span").decompose()

        course = {
            "title": title.text,
            "hours": hours.text.replace("h", "").strip(),
            "link": c['href'],
            "price": pricing.text.strip()
        }

        all_results.append(course)

result_dict = {"length": len(all_results), "courses": all_results}

with open("results.json", "w", encoding='utf-8') as f:
    json.dump(result_dict, f, indent=4, ensure_ascii=False)

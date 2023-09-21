import requests
from bs4 import BeautifulSoup


tags = ["data+science", "programacao", "web", "banco+de+dados"]


write_file = open("results.txt", "w")
for i in tags:
    URL = "https://www.learncafe.com/cursos?filter=all&q="+i
    page = requests.get(URL)
    
    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.find(id="cursosLista")

    courses = results.find_all("a", class_="card")


    for c in courses:
        hours = c.find("span", class_="card-hours")
        title = c.find("h5", class_="card-title")

        a = "__________________________________________________ \n"
        a =  a + "Título: "+ title.text + "\n"
        a = a + "Tempo para concluir: "+ hours.text.strip() + "\n"
        a = a + "Como acessar: " + c['href'] + "\n"
        a = a +"__________________________________________________ \n"
        
        write_file.write(a)



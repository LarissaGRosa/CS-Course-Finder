import time

from source.webscraper import Webscraper


def main():
    print("Starting...")
    start_time = time.time()

    learn_search_tags = ["data+science", "programacao", "web",
                   "banco+de+dados", "machine+learning"]
    learn_accepted_categories = {
        "Informática e internet", "Tecnologia da Informação"}
    
    harvard_search_tags = ["data+science", "programming", "web",
                   "database", "machine+learning"]
    harvard_accepted_categories = {"Programming", "Data Science",
                           "Computer Science", "Machine Learning"}
    
    pluralsight_search_tags = ["programming", "data+science", "web", "database", "machine+learning"]

    
    webscraper = Webscraper(harvard_accepted_categories, learn_accepted_categories)
    
    print("Escolha o número")
    print("[ 1 ] - Output by REQUESTS (LearnCafe, Harvard)")
    print("[ 2 ] - Output by SELENIUM (Pluralsight)")
    print("[ 3 ] - Combinar outputs")
    choice = input("Número: ")
    
    if choice == "1":
        webscraper.run_processing_harvard(harvard_search_tags)
        webscraper.run_processing_learncafe(learn_search_tags)
        webscraper.get_results()
    elif choice == "2":
        webscraper.run_processing_pluralsight(pluralsight_search_tags)
    elif choice == "3":
        webscraper.concatenate_results()

    end_time = time.time()
    print("Finished.")

    # Calculate the elapsed time
    elapsed_time = end_time - start_time

    # Print the elapsed time in seconds
    print(f"Elapsed time: {elapsed_time} seconds")


if __name__ == "__main__":
    main()

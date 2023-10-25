from source.webscraper import Webscraper
import time


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
    
    webscraper = Webscraper(harvard_accepted_categories, learn_accepted_categories)

    webscraper.run_processing_harvard(harvard_search_tags)
    webscraper.run_processing_learncafe(learn_search_tags)

    webscraper.get_results()

    end_time = time.time()
    print("Finished.")

    # Calculate the elapsed time
    elapsed_time = end_time - start_time

    # Print the elapsed time in seconds
    print(f"Elapsed time: {elapsed_time} seconds")


if __name__ == "__main__":
    main()

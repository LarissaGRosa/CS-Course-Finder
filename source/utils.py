import json

# from googletrans import Translator

class Utils:

    def __init__(self, hours_per_day, days_per_week):
        self.hours_per_day = hours_per_day
        self.days_per_week = days_per_week

    def week_to_hour(self, week_string):
        weeks = int(week_string.split()[0])
        aux = weeks * self.days_per_week * self.hours_per_day
        return str(aux) + " h"
    
    # TODO -> Fix this function
    # def english_to_portuguese(self, dict_list):
    #     translated = []

    #     translator = Translator()
    #     for d in dict_list:

    #         translated_dict = {}
    #         for key, value in d.items():
    #             translation = translator.translate(value, src='en', dest='pt')
    #             translated_dict[key] = translation.text

    #         translated.append(translated_dict)
    #     return translated
    
    def remove_duplicates(self, input_list):
        seen = set()
        output_list = []

        for d in input_list:
            # Convert each dictionary to a frozenset to make it hashable
            frozen_dict = frozenset(d.items())

            if frozen_dict not in seen:
                seen.add(frozen_dict)
                output_list.append(d)

        return output_list
    
    def remove_duplicates_adding_category(self, input_list):
        seen = set()
        output_list = []

        for d in input_list:
            unique_key = frozenset((key, value) for key, value in d.items() if key != 'category')

            if unique_key not in seen:
                seen.add(unique_key)
                output_list.append(d)
            else:
                existing_index = next(i for i, item in enumerate(output_list) if frozenset((key, value) for key, value in item.items() if key != 'category') == unique_key)
                existing_category_list = output_list[existing_index]['category']
                if d['category'] not in existing_category_list:
                    output_list[existing_index]['category'] = tuple(set(existing_category_list).union(set(d['category'])))
        
        return output_list
    
    def save_pluralsight_results(self, results):
        unique_results = self.remove_duplicates_adding_category(results)
        
        result_dict = {"length": len(unique_results), "courses": unique_results}

        with open("selenium_results.json", "w", encoding='utf-8') as f:
            json.dump(result_dict, f, indent=4, ensure_ascii=False)

    def save_results(self, all_results):
        # Convert each dictionary to a hashable frozenset
        unique_results = self.remove_duplicates(all_results)
        
        result_dict = {"length": len(unique_results), "courses": unique_results}

        with open("requests_results.json", "w", encoding='utf-8') as f:
            json.dump(result_dict, f, indent=4, ensure_ascii=False)
            
    def concatenate_outputs(self, filename_1, filename_2):
        with open(f'{filename_1}.json', 'r') as file1:
            json1 = json.load(file1)

        with open(f'{filename_2}.json', 'r') as file2:
            json2 = json.load(file2)

        courses = json1['courses'] + json2['courses']
        length =  json1['length'] + json2['length']
        output = {'length': length,'courses': courses}

        with open('results.json', 'w') as f:
            json.dump(output, f, indent=4, ensure_ascii=False) 

    
    

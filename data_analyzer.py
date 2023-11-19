import json
import matplotlib.pyplot as plt
from collections import Counter
import re

file_name = 'results.json'

with open(file_name, 'r') as f:
    data_dict = json.load(f)


##############################################

# Category analysis

##############################################
# Extract categories from each course
all_categories = [category for course in data_dict['courses'] for category in course['category']]

# Count the occurrences of each category
category_counts = Counter(all_categories)
# Exclude categories with less than 10 instances
filtered_categories = {category: count for category, count in category_counts.items() if count >= 10}

# Extract category names and counts for plotting
categories = list(filtered_categories.keys())
counts = list(filtered_categories.values())


# Plot the bar graph
plt.barh(categories, counts, color='skyblue')
plt.xlabel('Number of Courses')
plt.ylabel('Categories')
plt.title('Number of Courses in Each Category')

# Save the plot to a file (optional)
plt.savefig('course_category_plot_full.png', bbox_inches='tight')


################################

# Price Analysis

################################


durations = []
for course in data_dict['courses']:
    # Extract hours and minutes using regular expression
    match = re.match(r'(\d+)h\s*(\d+)?m?', course['period'])
    a = 0
    try:
        if match:
            hours = int(match.groups()[0])
            if not match.groups()[1]:
                minutes = 0
            else:
                minutes = int(match.groups()[1])
            total_minutes = hours * 60 + minutes
            durations.append(total_minutes)
        elif ' h' in course['period']:
            a=8
            # If only hours are present without minutes
            hours = int(re.match(r'(\d+) h', course['period']).group(1))
            total_minutes = hours * 60
            durations.append(total_minutes)
        elif 'h' in course['period']:
            a=7
            hours = int(re.match(r'(\d+)h', course['period']).group(1))
            total_minutes = hours * 60
            durations.append(total_minutes)
    except Exception as e:
        print(e)
        print(course['period'], match.groups())
        

# Calculate statistics
total_courses = len(durations)
average_duration = sum(durations) / total_courses
max_duration = max(durations)
min_duration = min(durations)

# Plot a histogram of course durations
plt.hist(durations, bins=20, color='skyblue', edgecolor='black')
plt.xlabel('Course Duration (Minutes)')
plt.ylabel('Number of Courses')
plt.title('Distribution of Course Durations')

# Save the plot to a file (optional)
plt.savefig('course_duration_histogram.png', bbox_inches='tight')

# Display statistics
print(f"Total Courses: {total_courses}")
print(f"Average Duration: {average_duration:.2f} minutes")
print(f"Maximum Duration: {max_duration} minutes")
print(f"Minimum Duration: {min_duration} minutes")




############################

# Price analysis

############################


# Extract price information from each course
prices = []
for course in data_dict['courses']:
    price_str = course.get('price', 'Unknown')
    
    # Extract numeric prices using regular expression
    match = re.search(r'\d+(\.\d+)?', price_str)
    if match:
        price = float(match.group())
        prices.append(price)
    else:
        match = re.search(r'\d+(\,\d+)?', price_str)
        if match and "R" in price_str:
            price = float(match.group().replace(",", "."))
            prices.append(price / 4.84)

# Calculate statistics
total_courses = len(prices)
average_price = sum(prices) / total_courses if prices else 0
max_price = max(prices) if prices else 0
min_price = min(prices) if prices else 0

# Display statistics
print(f"Total Courses: {total_courses}")
print(f"Average Price: ${average_price:.2f}")
print(f"Maximum Price: ${max_price:.2f}")
print(f"Minimum Price: ${min_price:.2f}")
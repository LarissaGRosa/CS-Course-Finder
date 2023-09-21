# CS Course Finder

CS Course Finder is a Python-based web scraping tool designed to help you discover online computer science-related classes from various sources on the web. This repository provides you with the necessary code and instructions to get started.

## Prerequisites

Before using CS Course Finder, make sure you have the following prerequisites installed on your system:

- Python 3.11
- pip (Python package manager): Included with Python 3.11

## Getting Started

Follow these steps to set up CS Course Finder on your local machine:

### 1. Clone the Repository

Clone this repository to your local machine using the following command:

```bash
git clone https://github.com/LarissaGRosa/CS-Course-Finder.git
```

### 2. Create a Virtual Environment (optional but recommended)

It's a good practice to use a virtual environment to isolate your project dependencies. To create and activate a virtual environment, run the following commands:

```bash
cd CS-Course-Finder
python -m venv venv
```

On macOS and Linux:

```bash
source venv/bin/activate
```

On Windows:

```bash
venv\Scripts\activate
```

### 3. Install Dependencies

Once you have the virtual environment activated (if you chose to use one), install the project's dependencies from the `requirements.txt` file:

```bash
pip install -r requirements.txt
```

### 4. Run the Web Scraper

You can now run the CS Course Finder web scraper. To do this, execute the following command:

```bash
python main.py
```

The script will start scraping online sources for computer science-related classes and display the results.

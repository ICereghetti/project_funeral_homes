# SQL Database Design using Website's data scraped with Selenium, BS4 and ChatGPT
## Project Description

Freelance Investigation work for a client that needed to understand how to design a complete SQL database from scratch for his Funeral Homes website. He needs to have a solid database that we can cut in multiple ways to have different points of views of the data. At the same time, it has to be flexbible enough to pivot in case we need to add new extra data.

## Deliverables

* [New Zealand's Funeral Homes Database](https://github.com/ICereghetti/project_funeral_homes/blob/b45ae90cea72fae99af1870f2f5ad925c75aeed4/funeral_homes_database.csv)
* [Python Code to scrape and format text data from Funeral Homes Websites using OpenAI](https://github.com/ICereghetti/project_funeral_homes/blob/1556a93cb6b031ada01dad035458566a79eef8a2/scrape_website.py)
* [Json File with samples of the data scraped from websites](https://github.com/ICereghetti/project_funeral_homes/blob/b45ae90cea72fae99af1870f2f5ad925c75aeed4/samples.json)
* [Database Schema Document with the main structure I recommend ex-post our findings](https://docs.google.com/spreadsheets/d/1YKqOfKtCx-Bx4KtMh7m7fcoXkl7wU3KPQ9LuyQzWJus/edit#gid=954638511))

## Skills used in this project
1) Data Scraping
2) Text Processing/Manipulation
4) Data Analysis
6) Data Interpretation
7) Data Modeling

## Tools used

1) Python (Selenium, Open AI, Beautiful Soup, urllib, time)
2) SQL (Bigquery)
3) Google Docs

## Highlights
#### A) Scrape Funeral Direct of New Zelaand with Selenium (https://funeraldirectors.co.nz)
1) Selenium is used to scrape and navigate through the website
2) Pandas, Time and BeautifulSoup are used to struture it.
3) Deliverable:
a) [New Zealand's Funeral Homes Database](https://github.com/ICereghetti/project_funeral_homes/blob/b45ae90cea72fae99af1870f2f5ad925c75aeed4/funeral_homes_database.csv)
#### B) Scrape relevant information from each business's Website
1) The client asked for a list of minimun columns to have in a file.
2) I read, structure and process the text using Chat GPT's API.
3) Then I structure relevant data into a JSON file for each business.
4) I create a sample of what the database might have, in order to plan and design a proper database.
5) Deliverables
a) [Code](https://github.com/ICereghetti/project_funeral_homes/blob/b45ae90cea72fae99af1870f2f5ad925c75aeed4/scrape_website.py)
b) [Data Sample](https://github.com/ICereghetti/project_funeral_homes/blob/b45ae90cea72fae99af1870f2f5ad925c75aeed4/samples.json)
#### C) We use the previous information to design the database  
1) Deliverable:
a) [Database structure](https://docs.google.com/spreadsheets/d/1YKqOfKtCx-Bx4KtMh7m7fcoXkl7wU3KPQ9LuyQzWJus/edit#gid=954638511))

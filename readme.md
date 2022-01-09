# BirthDates project
### This is BirthDates projects. It is a telegram chat-bot, which helps to choose gifts for your friends

## Key features of project:
- **Amazon parsing** - This project has database with over `20 000` 
products from amazon gifts section. Products are scrapped with captcha-solving
- **Clustering-tree recommendation algorithm** - This project has 3 modes of recommendation
The first mode is clustering-tree based mode. The products are stored in clustering-tree,
user is going from root to leaft by answering questions. When user reaches leaf cluster, 
they get the list of recommended products
- **Keywords analysis recommendation algorithm** - This project has keywords analysis algorithm.
User writes a short description about their friend and by analyzing keywords and their meaning
similarity to keywords of clusters recommends products
- **Bayesian-Gauss recommendation algorithm** - This project has Bayesian-Gauss recommendation
algorithm - each product has a normal distribution of probability of being recommended in
space of questions' answers. User is moving through this space by answering questions.
The recommended gifts are those with the most probability value in current users's
position

## This repo has some useful scripts for parsing amazon.com

- **scrap_livepages** - scraps data from pages that use Vue, React, or smth. like them and continuw loading after response has finished. This script uses selenium and chrome webdriver, without webdriver_options set it would open a chrome window and show all activity in it
- **scrap_multithreading** - scraps data using mutiple threads. Now found out grequests can be used instead
- **remove_js_from_page** - this short script clears page from js so after opening page in the browser js won't do anything and DOM won't be changed
- **create_headers** - copy headers from tab "Network" in browser debugging concole and paste it into this file. Script will generate json (or python-dict) headers
- **add_product** - called from **scrapping** and saves amazon product into json file
- **cat_prods_batch_splitter** splits any input json list into batches. Count of elements is set py property inside the file
- **requesting** - has a method that performs async requests by given url or solves amazon captcha if has problem with it. Method of solving captcha is located in **scrapping**
- **scrapping** - parses amazon products using prescrapped asins (amazon products ids), which are loadede from file (see more info in scrapping.py). Can solve captcha and parse almost infinitly. But maybe sometimes (not more than one time per day) has to update headers

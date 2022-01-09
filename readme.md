# BirthDates project

This is a BirthDates project client side.
BirthDates is an app to help people in
choosing gifts for their friends

## This repo has some useful scripts for parsing amazon.com

- **scrap_livepages** - scraps data from pages that use Vue, React, or smth. like them and continuw loading after response has finished. This script uses selenium and chrome webdriver, without webdriver_options set it would open a chrome window and show all activity in it
- **scrap_multithreading** - scraps data using mutiple threads. Now found out grequests can be used instead
- **remove_js_from_page** - this short script clears page from js so after opening page in the browser js won't do anything and DOM won't be changed
- **create_headers** - copy headers from tab "Network" in browser debugging concole and paste it into this file. Script will generate json (or python-dict) headers
- **add_product** - called from **scrapping** and saves amazon product into json file
- **cat_prods_batch_splitter** splits any input json list into batches. Count of elements is set py property inside the file
- **requesting** - has a method that performs async requests by given url or solves amazon captcha if has problem with it. Method of solving captcha is located in **scrapping**
- **scrapping** - parses amazon products using prescrapped asins (amazon products ids), which are loadede from file (see more info in scrapping.py). Can solve captcha and parse almost infinitly. But maybe sometimes (not more than one time per day) has to update headers

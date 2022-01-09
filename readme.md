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

## Hacking amazon journey (mostly by nebolax)

First of all we made some scripts scrapping data from amazon pages. We used headers copied from browser and this was enough to perform near hundred requests and receive products structure from amazon gifts section (https://www.amazon.com/gcx/Gifts-for-Everyone/gfhz/). But then we have got 23000 good amazon products ids and scrapping all 23000 pages was more tricky because there is two ways - we have to wait a lot or amazon throws captcha and if not responding captcha 503 error

Firstly we tried to use proxy. The main idea was that we didn't want to spend any money and so we tried to find some free proxies. There were only several good working proxies, which in fact weren't very stable and their performance was depending on random (using by other computers) or part of the day. And after maybe half a day of experiments we came up with idea that using proxy is too difficult and we should probably try other methods.

Then I had an idea that amazon.com is actually a DNS and it might redirect requests to different microservices. So I thought I could scan all amazon ip addresses and find which will respond in http port. To do this I've scrapped all potential http and https ports from wikipedia and took a random range of amazon ips (It's a public data). After a bit of calcualtions I understood it will take too long to scan all ips and I have to invent a bit more efficient method. (Fun fact: ips I was scanning were belongng to aws and I've found there some random websites all over the world, it was pretty interesting to explore these sites ;) ) Problem is that there is no public data where DNS routes directly. But in the network analytics in the browser we can see this address (it can vary from request to request), e.g. it can be "176.32.103.205:443" or a bit different. Interesting fact: all requests were using only 443 port (https). On all ips I've got strange error and it looks like request has to go through the DNS server. That said I thought that Amazon owns several domains and maybe I could perform requests to different domains and they will not communcate with each other and trace me as a single computer. But that didn't work - different amazon ips do different jobs.

And finally I've got a brilliant idea! To solve captcha!!)) This was the thing I wouldn't think about but finally it worked - pytesseract works okat (near 20% of success) and special library amazoncaptcha has near 60% success rate.

Just parse captcha image, hidden fields with captcha keys and perform simple GET request with answer. That's it!

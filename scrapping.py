import concurrent
from concurrent import futures
import requests
import json
from bs4 import BeautifulSoup
from add_product import add_product
from keywords import get_keywords
from tqdm import tqdm
from random import choice
import re
from requesting import get


proxies_html = requests.get('https://free-proxy-list.net/', headers={'User-Agent':'Mozilla/5.0'})
proxies_soup = BeautifulSoup(proxies_html.text,"lxml")
# print(res.text)
for item in proxies_soup.find_all("textarea"):
  proxies = item.text.split('\n')[3:]

base_url = 'https://www.amazon.com/dp/'

with open('headers.json') as hf:
    headers = json.loads(hf.read())


def get_product_data(asin: str):
    url = base_url + asin
    print(url, end='')
    # resp = requests.get(url, headers=headers, proxies={"https": "129.159.133.74:8080", "http": "129.159.133.74:8080"}).text
    resp = get(url)
    if 'To discuss automated access to Amazon data please contact' in resp:
        print("BAN!")
        # print(resp.text)
        return None

    soup = BeautifulSoup(resp, 'html.parser')

    root = soup.find(id='ppd')

    if soup.find(id='buybox') is None:
        return

    buybox = soup.find(id='buybox')

    product_price = None
    if buybox.find(id='outOfStock') is not None:
        print('out of stock')
        return
    elif buybox.find(id='price_inside_buybox') is not None:
        product_price = buybox.find(id='price_inside_buybox').text.strip()
    elif buybox.find(id='corePrice_feature_div') is not None:
        product_price = buybox.find(id='corePrice_feature_div').text.strip().split('$')[1]

    if product_price is None:
        return

    price = product_price.split('.')
    price[0] = re.sub('\D', '', price[0])
    price[1] = re.sub('\D', '', price[1])

    product_price = str(int(price[0]) * 100 + int(price[1]))

    product_title = root.find(id='productTitle').text.strip()
    product_description = root.find(id='productDescription')
    if product_description is not None:
        product_description = product_description.text.strip()
    else:
        product_description = ""
    product_ratings_count = root.find(id='acrCustomerReviewText')
    if product_ratings_count is not None:
        product_ratings_count = product_ratings_count.text.strip().split()[0].replace(',', '.')
    product_rating = root.find('span', class_='a-icon-alt')
    if product_rating is not None:
        product_rating = product_rating.text.strip().split()[0]

    product = {
        'title': product_title,
        'description': product_description,
        'price': product_price,
        'ratings_count': product_ratings_count,
        'rating': product_rating,
        'asin': asin,
        'category': None
    }

    return product


THREADS = 10

with open('links_normal.txt') as f:
    source = f.readlines()
    for i in range(0, len(source), THREADS):
        print(i, end=' ')
        with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
            future_to_data = (executor.submit(get_product_data, asin)
                             for asin in source[i:min(i + THREADS, len(source))])

            for future in concurrent.futures.as_completed(future_to_data):
                data = future.result()
                if data:
                    if data is not None:
                        keywords = get_keywords(data['title'] + '\n' + data['description'])
                        add_product(data['asin'], data['price'], data['title'], data['description'],
                                    data['ratings_count'],
                                    data['rating'], keywords)


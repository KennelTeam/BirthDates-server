import requests
import json
from bs4 import BeautifulSoup
from add_product import add_product
from keywords import get_keywords
from tqdm import tqdm
from random import choice
import re
from SessionManager import SessionManager
from requesting import get
import time
import asyncio
from pprint import pprint


base_url = 'https://www.amazon.com/dp/'

with open('headers.json') as hf:
    headers = json.loads(hf.read())

success_count = 0
bans = 0
description_fails = 0
prev_time = time.time()
file_with_products = input('Enter .json path: ')
# file_with_products = '../batches/categs-0.json'
path_scrapped = 'scrapped-' + file_with_products.split('/')[-1]


async def get_product_data(asin: str, categories_and_price, change_proxy=False):
    try:
        categories = categories_and_price['tags']
        categories = prepare_categories(categories)
        price = categories_and_price['price']
    except:
        categories = []
        price = 0
    # print('Started', asin)
    url = base_url + asin
    # resp = requests.get(url, headers=headers, proxies={"https": "129.159.133.74:8080", "http": "129.159.133.74:8080"}).text
    resp = await get(url, change_proxy)
    if 'To discuss automated access to Amazon data please contact' in resp:
        global bans
        bans += 1
        # print("Got ban! Changing proxy...")
        # print(resp.text)
        return await get_product_data(asin, categories_and_price, change_proxy=True)

    soup = BeautifulSoup(resp, 'html.parser')

    product_title = 'AZAZA'
    product_price = price  # str(int(price[0]) * 100 + int(price[1]))
    product_title = soup.find(id='productTitle')
    if product_title is not None:
        product_title = product_title.text.strip()
    else:
        try:
            product_title = soup.find(id='gc-asin-title').text.strip()
        except:
            print('Failed to get product title of', asin)
    product_description = soup.find(id='productDescription')
    if product_description is not None:
        product_description = product_description.text.strip()
    else:
        product_description = soup.find(id="feature-bullets")
        if product_description is not None:
            product_description = product_description.text.strip()
        else:
            product_description = ""
            global description_fails
            description_fails += 1
            # print("trouble!")
    product_ratings_count = soup.find(id='acrCustomerReviewText')
    if product_ratings_count is not None:
        product_ratings_count = product_ratings_count.text.strip().split()[
            0].replace(',', '.')
    product_rating = soup.find('span', class_='a-icon-alt')
    if product_rating is not None:
        product_rating = product_rating.text.strip().split()[0]

    product = {
        'title': product_title,
        'description': product_description,
        'price': product_price,
        'ratings_count': product_ratings_count,
        'rating': product_rating,
        'category': None
    }

    global success_count
    if product is not None:
        try:
            keywords = get_keywords(
                product['title'] + '\n' + product['description'])
            add_product(asin, product['price'], product['title'], product['description'], product['ratings_count'],
                        product['rating'], keywords, path_scrapped)
            success_count += 1
        except Exception as e:
            print("Exception in DB", end=': ')
            print(e)

    print('Saved ' + asin)


def prepare_categories(categories):
    new_categories = []
    for cat in categories:
        if '&' in cat:
            new_categories += cat.split(' & ')
        else:
            new_categories.append(cat)
    return new_categories


with open(file_with_products) as f:
    file = f.read()
    objects = json.loads(file)
    loop = asyncio.get_event_loop()
    asins = list(objects.keys())

    items_per_batch = 200
    batches = []
    adding = True
    while adding:
        if (len(batches)+1)*items_per_batch >= len(asins):
            batches.append(asins[len(batches)*items_per_batch:])
            adding = False
        else:
            batches.append(
                asins[len(batches)*items_per_batch:(len(batches)+1)*items_per_batch])
    # pprint(batches)

    #  categories = objects[asin_number]
    ptime = time.time()
    for batch in tqdm(batches):
        gathered = asyncio.gather(*[get_product_data(asin, objects[asin])
                                    for asin in batch])
        results = loop.run_until_complete(gathered)

        ctime = time.time()
        print('Took', ctime - ptime)
        ptime = ctime

print('Successfilly finished!')

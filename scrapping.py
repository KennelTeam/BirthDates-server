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


proxies_html = requests.get('https://free-proxy-list.net/', headers={'User-Agent':'Mozilla/5.0'})
proxies_soup = BeautifulSoup(proxies_html.text,"lxml")
# print(res.text)
for item in proxies_soup.find_all("textarea"):
  proxies = item.text.split('\n')[3:]

base_url = 'https://www.amazon.com/dp/'

with open('headers.json') as hf:
    headers = json.loads(hf.read())


def get_product_data(asin: str, price: int):
    url = base_url + asin
    print(url, end='\n')
    # resp = requests.get(url, headers=headers, proxies={"https": "129.159.133.74:8080", "http": "129.159.133.74:8080"}).text
    resp = get(url)
    if 'To discuss automated access to Amazon data please contact' in resp:
        global bans
        bans += 1
        print("BAN!")
        # print(resp.text)
        return None

    soup = BeautifulSoup(resp, 'html.parser')

    # root = soup.find(id='ppd')

    # if soup.find(id='buybox') is None:
    #     print("No price!")
    #     return
    #
    # buybox = soup.find(id='buybox')
    #
    # product_price = None
    # if buybox.find(id='outOfStock') is not None:
    #     print('out of stock')
    #     return
    # elif buybox.find(id='price_inside_buybox') is not None:
    #     product_price = buybox.find(id='price_inside_buybox').text.strip()
    # elif buybox.find(id='corePrice_feature_div') is not None:
    #     product_price = buybox.find(id='corePrice_feature_div').text.strip().split('$')[1]
    #
    # if product_price is None:
    #     print("Product price is NONE")
    #     open("test.html", 'w', encoding='utf-8').write(resp)
    #     return
    #
    # price = product_price.split('.')
    # price[0] = re.sub('\D', '', price[0])
    # price[1] = re.sub('\D', '', price[1])

    product_price = price  # str(int(price[0]) * 100 + int(price[1]))
    product_title = soup.find(id='productTitle')
    if product_title is not None:
        product_title = product_title.text.strip()
    else:
        product_title = soup.find(id='gc-asin-title').text.strip()
    product_description = soup.find(id='productDescription')
    if product_description is not None:
        product_description = product_description.text.strip()
    else:
        product_description = ""
        global description_fails
        description_fails += 1
        # print("trouble!")
    product_ratings_count = soup.find(id='acrCustomerReviewText')
    if product_ratings_count is not None:
        product_ratings_count = product_ratings_count.text.strip().split()[0].replace(',', '.')
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

    return product


success_count = 0
bans = 0
description_fails = 0

with open('unique-gifts-ids.txt') as f:
    for index, line in enumerate(f.readlines()):
        asin_number, price = line.split(' ')
        if index % 10 == 0:
            print("Done {}, {} successful, {} failed, {} banned, {} without description".format(
                index, success_count, index - success_count, bans, description_fails
            ))
        price = int(price)
        print(index, end=' ')
        try:
            data = get_product_data(asin=asin_number, price=price)
        except Exception as e:
            print(e)
            data = None
        if data is not None:
            try:
                # if data['description'] == "":
                #     print("CRIIIIINGE!")
                keywords = get_keywords(data['title'] + '\n' + data['description'])
                add_product(asin_number, data['price'], data['title'], data['description'], data['ratings_count'],
                            data['rating'], keywords)
                success_count += 1
            except Exception as e:
                print("Exception in DB", end=': ')
                print(e)
                SessionManager().session().rollback()


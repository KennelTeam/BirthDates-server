import requests
import json
from bs4 import BeautifulSoup
from add_product import add_product
from keywords import get_keywords
from tqdm import tqdm

base_url = 'https://www.amazon.com/dp/'

with open('headers.json') as hf:
    headers = json.loads(hf.read())


def get_product_data(asin: str):
    url = base_url + asin
    print(url, end='')
    resp = requests.get(url, headers=headers)

    if 'To discuss automated access to Amazon data please contact' in resp.text:
        print("BAN!")
        print(resp.text)
        return None

    soup = BeautifulSoup(resp.text, 'html.parser')

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
        'category': None
    }

    return product


with open('links_normal.txt') as f:
    for index, asin_number in enumerate(f.readlines()):
        print(index, end=' ')
        try:
            data = get_product_data(asin=asin_number)
        except:
            data = None
        if data is not None:
            keywords = get_keywords(data['title'] + '\n' + data['description'])
            add_product(asin_number, data['price'], data['title'], data['description'], data['ratings_count'],
                        data['rating'], keywords)


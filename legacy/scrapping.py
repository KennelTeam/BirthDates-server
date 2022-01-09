import json
from bs4 import BeautifulSoup
from add_product import add_product
from keywords import get_keywords
from tqdm import tqdm
import re
from requesting import get, asession
import asyncio
from io import BytesIO
import re
import progressbar
from amazoncaptcha import AmazonCaptcha
import logging

import nest_asyncio
nest_asyncio.apply()

base_url = 'https://www.amazon.com/dp/'
with open('headers.json') as hf:
    headers = json.loads(hf.read())

# Inputing parameters
# categories file should be dictionary of elements like
# |amazon id (asin)| : {"tags": [], "price": 000}
# example: "B00EIBT7JW": {"tags": ["Adult", "women", "Style & Fashion"], "price": 14004}
file_with_products = input('Categories file path: ')
start_amazon_asin = input('Start from asin (optional): ')
items_per_batch_inp = input('Items per batch (default 100): ')
if items_per_batch_inp == '':
    items_per_batch = 100
else:
    items_per_batch = int(items_per_batch_inp)
path_scrapped = 'scrapped-' + file_with_products.split('/')[-1]
pbar = progressbar.ProgressBar(0, items_per_batch)


# Solves captcha
# Requests captcha image from amazon server and process it with amazoncaptcha python library
# Firstly was using pytesseract but then found specific lib
# Also returns captcha parameters (captcha key [amzn] and url to redirect [amzn-r])
async def solve_captcha(page_text):
    soup = BeautifulSoup(page_text, 'html.parser')
    form = soup.find('form')
    params = {}
    params['amzn'] = form.find('input', attrs={'name': 'amzn'})['value']
    params['amzn-r'] = form.find('input', attrs={'name': 'amzn-r'})['value']
    img_link = form.find('img')['src']
    image_resp = await asession.get(img_link)
    captcha_res = AmazonCaptcha(BytesIO(image_resp.content)).solve()
    params['field-keywords'] = re.sub('[^a-zA-Z]+', '', captcha_res)
    return params


# Preprocess categories
# Turned doubled categories such as "Beauty & Fashion" into 2 single
def prepare_categories(categories):
    new_categories = []
    for cat in categories:
        if '&' in cat:
            new_categories += cat.split(' & ')
        else:
            new_categories.append(cat)
    return new_categories


# Main processer of a single product
async def get_product_data(asin: str, categories_and_price, captcha=None):
    # Get categories of the product and it's price
    # Price is scrapped earlier because at the details page it has
    # a lot of versions to be displayed and is hard to scrap
    try:
        categories = categories_and_price['tags']
        categories = prepare_categories(categories)
        price = categories_and_price['price']
    except:
        categories = []
        price = 0

    # Performing request. Receiving code 200 even if got captcha
    # but if code is not 200 there is an error we can't deal
    url = base_url + asin
    resp_text, resp_code = await get(url, captcha)
    if resp_code != 200:
        print(f'skipping {asin}.', 'Reason: bad status code', resp_code)
        return
    # Detecting captcha
    if 'Enter the characters you see below' in resp_text:
        # Calling recursion with updated captcha parameter
        return await get_product_data(asin, categories_and_price, captcha=(await solve_captcha(resp_text)))

    soup = BeautifulSoup(resp_text, 'html.parser')
    product_title = 'NO TITLE'
    product_price = price
    product_title = soup.find(id='productTitle')
    if product_title is not None:
        product_title = product_title.text.strip()
    else:
        try:
            product_title = soup.find(id='gc-asin-title').text.strip()
        except:
            print('Skipping', asin, 'Reason: can\'t find title')
            return

    product_description = soup.find(id='productDescription')
    if product_description is not None:
        product_description = product_description.text.strip()
    else:
        product_description = soup.find(id="feature-bullets")
        if product_description is not None:
            product_description = product_description.text.strip()
        else:
            product_description = ""
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

    if product is not None:
        try:
            keywords = get_keywords(
                product['title'] + '\n' + product['description'])
            add_product(asin, product['price'], product['title'], product['description'], product['ratings_count'],
                        product['rating'], keywords, path_scrapped)
        except Exception as e:
            print("Exception in DB", end=': ')
            print(e)

    if captcha:
        print('Successfully solved captcha! :)')

    global pbar_progress
    pbar_progress += 1
    pbar.update(pbar_progress)


# Runs all code i.e. Main :) Loads data frim file_with_products and
# gets objects (price and categories) and asins (asin - amazon product id)
# Splits data into batches and can optionally start not from the beginning (see star_amazon_asin)
# Runs batches, each coroutine in batch performs requests asynchronously
# I didn't figure out on how this fucking damn shit asyncio works and so you'll
# see warning, but otherwise await asession.get() in requesting module won't fucking work
def main():
    with open(file_with_products) as f:
        file = f.read()
        objects = json.loads(file)
        asins = list(objects.keys())
        if start_amazon_asin != '':
            asins = asins[asins.index(
                start_amazon_asin):]

        batches = []
        adding = True
        while adding:
            if (len(batches)+1)*items_per_batch >= len(asins):
                batches.append(asins[len(batches)*items_per_batch:])
                adding = False
            else:
                batches.append(
                    asins[len(batches)*items_per_batch:(len(batches)+1)*items_per_batch])

        loop = asyncio.get_event_loop()
        global pbar_progress
        for batch in tqdm(batches):
            print()
            pbar_progress = 0
            gathered = asyncio.gather(*[get_product_data(asin, objects[asin])
                                        for asin in batch])
            loop.run_until_complete(gathered)

    print('Successfilly finished!')


main()

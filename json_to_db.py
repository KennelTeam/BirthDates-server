from SessionManager import SessionManager
from images import Product, ProductKeyword, Keyword
import json
from tqdm import tqdm


with open("data\\entire.json", 'r') as f:
    product_id = 0
    keyword_id = 0
    keywords = {}
    data = json.loads(f.read())
    for product in tqdm(data):
        product = product[1]
        nprod = Product(product['amazon_id'], product['cost_cents'], product['name'], product['description'],
                        product['reviews_count'], product['avg_rating'], product_id)
        product_id += 1
        SessionManager().session().add(nprod)
    SessionManager().session().commit()

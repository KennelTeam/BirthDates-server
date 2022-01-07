from SessionManager import SessionManager
from images import Product, ProductKeyword, Keyword
import json
from tqdm import tqdm


with open("entire.json", 'r') as f:
    data = json.loads(f.read())
    for keyword in tqdm(data['keywords']):
        nword = Keyword(keyword[1], keyword[0])
        SessionManager().session().add(nword)
    for product in tqdm(data['prods']):
        nprod = Product(product[1]['amazon_id'], product[1]['cost_cents'], product[1]['name'], product[1]['description'],
                        product[1]['reviews_count'], product[1]['avg_rating'], product[0])
        SessionManager().session().add(nprod)
    for pair in tqdm(data['pairs']):
        SessionManager().session().add(ProductKeyword(pair[1]['product_id'], pair[1]['keyword_id']))
    SessionManager().session().commit()

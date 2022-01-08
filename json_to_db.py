from SessionManager import SessionManager
from images import Product, ProductKeyword, Keyword
import json
from tqdm import tqdm
from keywords import get_keywords_koe
from sqlalchemy import func
from pprint import pprint
import re

BATCH_SIZE = 1000

with open("data\\entire.json", 'r') as f:
    product_id = 1
    keyword_id = 1
    skipped = 0
    keywords = {}
    for item in SessionManager().session().query(Keyword).all():
        keywords[item.word] = item.id
        keyword_id = max(keyword_id, item.id + 1)
    print("keywords got")
    res = SessionManager().session().query(func.max(Product.id)).one()
    if res[0] is not None:
        product_id = res[0] + 1
    print("product_id: {}".format(product_id))
    data = json.loads(f.read())

    db_products = []
    db_keywords = []
    db_pairs = []

    for index, product in tqdm(enumerate(data)):
        if index > 0 and index % BATCH_SIZE == 0:
            print("{} skipped".format(skipped))
            print("saving products")
            SessionManager().session().bulk_save_objects(db_products)
            SessionManager().session().commit()
            SessionManager().session().flush()
            print("saving keywords")
            SessionManager().session().bulk_save_objects(db_keywords)
            SessionManager().session().commit()
            SessionManager().session().flush()
            print("saving pairs")
            SessionManager().session().bulk_save_objects(db_pairs)
            SessionManager().session().commit()
            SessionManager().session().flush()

            db_products = []
            db_keywords = []
            db_pairs = []
            print("saved")
        product = product[1]
        text = product['name'] + "\n" + product['description']
        cur_keywords = get_keywords_koe(text)
        if len(cur_keywords.keys()) == 0:
            skipped += 1
            continue
        nprod = Product(product['amazon_id'], product['cost_cents'], product['name'], product['description'],
                        product['reviews_count'], product['avg_rating'], product_id)

        db_products.append(nprod)

        for keyword in cur_keywords.keys():
            keyword = keyword.lower()
            if len(keyword) > 32:
                continue
            if not bool(re.match(r"[a-zA-Z\- ']+$", keyword)):
                continue
            if keyword not in keywords.keys():
                keywords[keyword] = keyword_id
                kwd = Keyword(keyword, keyword_id)
                db_keywords.append(kwd)
                keyword_id += 1
            pk = ProductKeyword(product_id, keywords[keyword], cur_keywords[keyword])
            db_pairs.append(pk)
        product_id += 1
    print("saving products")
    SessionManager().session().bulk_save_objects(db_products)
    SessionManager().session().commit()
    print("saving keywords")
    SessionManager().session().bulk_save_objects(db_keywords)
    SessionManager().session().commit()
    print("saving pairs")
    SessionManager().session().bulk_save_objects(db_pairs)
    SessionManager().session().commit()

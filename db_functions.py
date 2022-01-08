from SessionManager import SessionManager
from images import Product, ProductKeyword, Keyword


def get_product_keywords(product_id: int):
    results = SessionManager().session().query(ProductKeyword, Keyword) \
        .filter(ProductKeyword.keyword_id == Keyword.id) \
        .filter(ProductKeyword.product_id == product_id) \
        .all()
    return {keyword.word: pair.weight for pair, keyword in results}


def get_product(product_id: int):
    res = SessionManager().session().query(Product).filter_by(id=product_id).all()
    if len(res) == 0:
        return None
    else:
        return res[0].to_json()

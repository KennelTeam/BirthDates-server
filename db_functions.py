from SessionManager import SessionManager
from images import Product, ProductKeyword, Keyword


def get_product_keywords(product_id: int):
    results = SessionManager().session().query(Keyword).filter(Keyword.id.in_(
        SessionManager().session().query(ProductKeyword.keyword_id).filter_by(product_id=product_id)
    )).all()
    return [res.word for res in results]


def get_product(product_id: int):
    res = SessionManager().session().query(Product).filter_by(id=product_id).all()
    if len(res) == 0:
        return None
    else:
        return res[0].to_json()

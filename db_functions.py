from SessionManager import SessionManager
from images import Product, ProductKeyword, Keyword


def get_product_keywords(product_id: int):
    results = SessionManager().session().query(Keyword).filter(Keyword.id.in_(
        SessionManager().session().query(ProductKeyword.keyword_id).filter_by(product_id=product_id)
    )).all()
    return [res.word for res in results]

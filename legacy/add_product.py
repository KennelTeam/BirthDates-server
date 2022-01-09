from images import Keyword, ProductKeyword, Product
from SessionManager import SessionManager


# LEGACY !!!!
# Adds product to database (quite slow function)
def add_product(amazon_id: str, cost_cents: int, name: str, description: str, reviews_count: int, avg_rating: float,
                keywords: list):
    keyword_ids = []
    for keyword in keywords:
        if len(keyword) > 32:
            continue
        result = SessionManager().session().query(Keyword).filter_by(word=keyword).all()
        if len(result) == 0:
            new_keyword = Keyword(keyword)
            SessionManager().session().add(new_keyword)
            SessionManager().session().flush()
            SessionManager().session().refresh(new_keyword)
            keyword_ids.append(new_keyword.id)
        else:
            keyword_ids.append(result[0].id)

    check = SessionManager().session().query(Product).filter_by(amazon_id=amazon_id).all()
    if len(check) > 0:
        return
    new_product = Product(amazon_id, cost_cents, name, description, reviews_count, avg_rating)
    SessionManager().session().add(new_product)
    SessionManager().session().flush()
    SessionManager().session().refresh(new_product)
    for id in keyword_ids:
        new_pair = ProductKeyword(new_product.id, id)
        SessionManager().session().add(new_pair)
    SessionManager().session().commit()


def add_product_with_koe(amazon_id: str, cost_cents: int, name: str, description: str, reviews_count: int, avg_rating: float,
                keywords: dict):
    pass


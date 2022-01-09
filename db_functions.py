# copyright KennelTeam
# AndrusovN for any questions
# file with functions to work with main part of Database i.e. Products and keywords
from SessionManager import SessionManager
from images import Product, ProductKeyword, Keyword


# returns {keyword: weight} for given product
def get_product_keywords(product_id: int):
    results = SessionManager().session().query(ProductKeyword, Keyword) \
        .filter(ProductKeyword.keyword_id == Keyword.id) \
        .filter(ProductKeyword.product_id == product_id) \
        .all()
    return {keyword.word: pair.weight for pair, keyword in results}


# returns list of {keyword: weight} for given list of products
# this function is much faster than calling many get_product_keyword functions
def get_products_keywords(product_ids: list):
    data = SessionManager().session().query(ProductKeyword, Keyword)\
        .filter(ProductKeyword.keyword_id == Keyword.id)\
        .filter(ProductKeyword.product_id.in_(product_ids)).all()
    result = {id: {} for id in product_ids}
    for pair, keyword in data:
        result[pair.product_id][keyword.word] = pair.weight
    return result


# returns all data about given product (except keywords)
# {id, asin, link, cost, name, description, reviews_count, avg_rating}
def get_product(product_id: int):
    res = SessionManager().session().query(Product).filter_by(id=product_id).all()
    if len(res) == 0:
        return None
    else:
        return res[0].to_json()


# returns list of product infos as function above
# this is faster than calling many get_product
def get_products(product_ids: list):
    data = SessionManager().session().query(Product).filter(Product.id.in_(product_ids)).all()
    return {item.id: item.to_json() for item in data}


# return's keywords of all products: list of {keyword: weight} for each product
def get_all_products_keywords():
    data = SessionManager().session().query(ProductKeyword, Keyword) \
        .filter(ProductKeyword.keyword_id == Keyword.id).all()
    result = {}
    for pair, keyword in data:
        if pair.product_id not in result.keys():
            result[pair.product_id] = {}
        result[pair.product_id][keyword.word] = pair.weight
    return result
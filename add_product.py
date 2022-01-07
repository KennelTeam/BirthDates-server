import json
# from images import Keyword, ProductKeyword, Product
# from SessionManager import SessionManager

id_prod = 10000
id_keyword = 10000
id_pair = 10000

keywords = []  # [[id, word], [id, word]...]
prods = []  # [[id, prod], [id, prod]...]
pairs = []  # [[id, pair], [id, pair]...]


def add_product(amazon_id: str, cost_cents: int, name: str, description: str, reviews_count: int, avg_rating: float,
                keyw_inp: list, path: str):
    global id_keyword, id_pair, id_prod
    keyword_ids = []
    for keyword in keyw_inp:
        if len(keyword) > 32:
            continue

        result = list(
            filter(lambda word_el: word_el[0] == keyword, keywords))
        if len(result) == 0:
            id_keyword += 1
            keywords.append([id_keyword, keyword])
            keyword_ids.append(id_keyword)
        else:
            keyword_ids.append(result[0][0])

    check = list(filter(lambda prod: prod[1]['amazon_id'] == amazon_id, prods))
    if len(check) > 0:
        return

    new_product = {
        'amazon_id': amazon_id,
        'cost_cents': cost_cents,
        'name': name,
        'description': description,
        'reviews_count': reviews_count,
        'avg_rating': avg_rating
    }
    id_prod += 1
    prods.append([id_prod, new_product])
    for id in keyword_ids:
        id_pair += 1
        pairs.append([id_pair, {'product_id': id_prod, 'keyword_id': id}])

    entire = {
        'keywords': keywords,
        'prods': prods,
        'pairs': pairs
    }
    with open(path, 'w') as f:
        f.write(json.dumps(entire))


# def add_product_database(amazon_id: str, cost_cents: int, name: str, description: str, reviews_count: int, avg_rating: float,
#                          keywords: list):
#     keyword_ids = []
#     for keyword in keywords:
#         if len(keyword) > 32:
#             continue
#         result = SessionManager().session().query(
#             Keyword).filter_by(word=keyword).all()
#         if len(result) == 0:
#             new_keyword = Keyword(keyword)
#             SessionManager().session().add(new_keyword)
#             SessionManager().session().flush()
#             SessionManager().session().refresh(new_keyword)
#             keyword_ids.append(new_keyword.id)
#         else:
#             keyword_ids.append(result[0].id)

#     check = SessionManager().session().query(
#         Product).filter_by(amazon_id=amazon_id).all()
#     if len(check) > 0:
#         return
#     new_product = Product(amazon_id, cost_cents, name,
#                           description, reviews_count, avg_rating)
#     SessionManager().session().add(new_product)
#     SessionManager().session().flush()
#     SessionManager().session().refresh(new_product)
#     for id in keyword_ids:
#         new_pair = ProductKeyword(new_product.id, id)
#         SessionManager().session().add(new_pair)
#     SessionManager().session().commit()

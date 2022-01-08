from SessionManager import SessionManager
from images import Product
from keywords import get_keywords_koe
from clustering_graph_db import ClusterToKeyword


def count_keywords_koe():
    total = SessionManager().session().query(Product).all()
    for id, product in enumerate(total):
        text = product.name + "\n" + product.description
        cur_keywords = get_keywords_koe(text)
        ...


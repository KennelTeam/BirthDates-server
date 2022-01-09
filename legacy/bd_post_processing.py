from SessionManager import SessionManager
from images import Product
from keywords import get_keywords_koe
from tqdm import tqdm
from add_product import add_product_with_koe


def count_keywords_koe():
    total = SessionManager().session().query(Product).all()
    for id, product in tqdm(enumerate(total)):
        text = product.name + "\n" + product.description
        keywords = get_keywords_koe(text)
        add_product_with_koe(product.id, product.cost, product.name, product.description, product.reviews_count,
                             product.avg_rating, keywords)


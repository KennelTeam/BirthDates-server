from Bayes import prepare_dataset
from questions_db_functions import get_all_questions

from db_functions import get_product, get_all_products_keywords
from pprint import pprint
QUESTIONS = get_all_questions()
print("all questions got")
products = get_all_products_keywords()
print("all products got")
prepare_dataset(products, QUESTIONS)

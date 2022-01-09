from SessionManager import SessionManager
from images import ProductKeyword, Product, Keyword
import re


def remove_keyword_1(word_id):
    SessionManager().session().query(ProductKeyword).filter_by(keyword_id=word_id).delete()
    # SessionManager().session().delete(data)
    SessionManager().session().query(Keyword).filter_by(id=word_id).delete()
    # SessionManager().session().delete(word)
    SessionManager().session().commit()


data = set([(word.word, word.id) for word in SessionManager().session().query(Keyword).all()])
for word in data:
    if not bool(re.match(r"([a-zA-Z][ ]*)+$", word[0])):
        try:
            remove_keyword_1(word[1])
            print(word[0])
        except Exception as e:
            print(e)

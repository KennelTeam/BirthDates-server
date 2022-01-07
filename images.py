from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import *

Base = declarative_base()


class Keyword(Base):
    __tablename__ = 'keyword'

    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(VARCHAR(32), unique=True)

    def __init__(self, word: str, id: int = 0):
        self.word = word
        if id != 0:
            self.id = id

    def to_json(self):
        return {
            "id": self.id,
            "word": self.word
        }


class Product(Base):
    __tablename__ = 'product'

    id = Column(Integer, primary_key=True, autoincrement=True)
    amazon_id = Column(String(16))
    cost = Column(Integer)
    name = Column(Text)
    description = Column(Text)
    reviews_count = Column(Integer)
    avg_rating = Column(Float)

    def __init__(self, amazon_id: str, cost_cents: int, name: str, description: str, reviews_count: int,
                 avg_rating: float, id: int = 0):
        super().__init__()
        self.amazon_id = amazon_id
        self.cost = cost_cents
        self.name = name
        self.description = description
        self.reviews_count = reviews_count
        self.avg_rating = avg_rating
        if id != 0:
            self.id = id

    def to_json(self):
        return {
            "asin": self.amazon_id,
            "link": "https://amazon.com/dp/" + self.amazon_id,
            "cost": self.cost,
            "name": self.name,
            "description": self.description,
            "reviews_count": self.reviews_count,
            "avg_rating": self.avg_rating
        }


class ProductKeyword(Base):
    __tablename__ = 'product_keyword'

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey('product.id'))
    keyword_id = Column(Integer, ForeignKey('keyword.id'))

    def __init__(self, product_id, keyword_id):
        self.product_id = product_id
        self.keyword_id = keyword_id


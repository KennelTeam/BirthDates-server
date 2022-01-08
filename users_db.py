from images import Base
from sqlalchemy import *


class User(Base):
    __tablename__ = "user"

    telegram_id = Column(Integer, primary_key=True)

    def __init__(self, telegram_id: int):
        self.telegram_id = telegram_id


class Favourite(Base):
    __tablename__ = "favourite"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.telegram_id"))
    product_id = Column(Integer, ForeignKey("product.id"))

    def __init__(self, user_id: int, product_id: int):
        self.user_id = user_id
        self.product_id = product_id
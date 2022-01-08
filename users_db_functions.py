from users_db import User, Favourite
from images import Product
from SessionManager import SessionManager


def get_users_favourite(user_id: int):
    data = SessionManager().session().query(Product).filter(Product.id.in_(SessionManager().session()\
                                                                    .query(Favourite.product_id)\
                                                                    .filter_by(user_id=user_id))
                                                     )
    return [item.to_json() for item in data]


def add_to_favourite(user_id: int, product_id: int):
    user = SessionManager().session().query(User).filter_by(user_id).all()
    if len(user) == 0:
        SessionManager().session().add(User(user_id))
        SessionManager().session().commit()
    try:
        SessionManager().session().add(Favourite(user_id, product_id))
        SessionManager().session().commit()
        return True
    except Exception:
        return False


def remove_from_favourite(user_id: int, product_id: int):
    try:
        SessionManager().session().query(Favourite).filter_by(user_id=user_id, product_id=product_id).delete()
        SessionManager().session().commit()
        return True
    except Exception:
        return False

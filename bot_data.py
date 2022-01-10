from user_questions import TreeSession
from dataclasses import dataclass
from Bayes import BayesSession


@dataclass
class User:
    tree_session: TreeSession
    bayes_session: BayesSession


users = {}


def get_bayes_session(user_id: int):
    if user_id not in users:
        new_user = User
        new_user.bayes_session = BayesSession()
        users[user_id] = new_user
    if users[user_id].bayes_session is None:
        users[user_id].bayes_session = BayesSession()
    return users[user_id].bayes_session


def get_tree_session(user_id: int):
    if user_id not in users:
        new_user = User
        new_user.tree_session = TreeSession()
        users[user_id] = new_user
    if users[user_id].tree_session is None:
        users[user_id].tree_session = TreeSession()
    return users[user_id].tree_session

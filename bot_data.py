from user_questions import TreeSession

users = {}


def get_tree_session(user_id: int):
    if user_id not in users:
        new_session = TreeSession()
        users[user_id] = new_session
        return new_session
    else:
        return users[user_id]

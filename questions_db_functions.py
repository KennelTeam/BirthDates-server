from questions_db import QuestionToKeyword, Question
from images import Keyword
from SessionManager import SessionManager


def add_question(text: str, keywords: list):
    question = Question(text)
    SessionManager().session().add(question)
    SessionManager().session().flush()
    SessionManager().session().refresh(question)

    for keyword in keywords:
        db_kw = SessionManager().session().query(Keyword).filter_by(word=keyword).one()
        if db_kw is None:
            db_kw = Keyword(keyword)
            SessionManager().session().add(db_kw)
            SessionManager().session().flush()
            SessionManager().session().refresh(db_kw)
        SessionManager().session().add(QuestionToKeyword(db_kw.id, question.id))
    return question.id


# returns list of tuples (keyword_id, keyword_word)
def get_keywords(question_id: int):
    result = SessionManager().session().query(Keyword).filter(Keyword.id.in_(
        SessionManager().session().query(QuestionToKeyword.keyword_id).filter_by(question_id=question_id)
    )).all()
    return [(keyword.id, keyword.word) for keyword in result]

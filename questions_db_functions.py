from questions_db import QuestionToKeyword, Question
from images import Keyword
from SessionManager import SessionManager


def add_question(text: str, keywords: list):
    question = Question(text)
    SessionManager().session().add(question)
    SessionManager().session().flush()
    SessionManager().session().refresh(question)

    for keyword in keywords:
        db_kw = SessionManager().session().query(Keyword).filter_by(word=keyword).all()
        if len(db_kw) == 0:
            db_kw = Keyword(keyword)
            SessionManager().session().add(db_kw)
            SessionManager().session().flush()
            SessionManager().session().refresh(db_kw)
        else:
            db_kw = db_kw[0]
        SessionManager().session().add(QuestionToKeyword(db_kw.id, question.id))
    return question.id


def get_all_questions():
    questions = SessionManager().session().query(Question).all()
    keywords = SessionManager().session().query(QuestionToKeyword, Keyword)\
        .filter(QuestionToKeyword.keyword_id == Keyword.id).all()

    result = []
    for item in questions:
        q = {'text': item.text, 'keywords': []}
        for kw, word in keywords:
            if kw.question_id == item.id:
                q['keywords'].append(word.word)
        result.append(q)
    return result


# returns list of tuples (keyword_id, keyword_word)
def get_keywords(question_id: int):
    result = SessionManager().session().query(Keyword).filter(Keyword.id.in_(
        SessionManager().session().query(QuestionToKeyword.keyword_id).filter_by(question_id=question_id)
    )).all()
    return [(keyword.id, keyword.word) for keyword in result]

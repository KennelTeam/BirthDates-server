# copyright KennelTeam
# AndrusovN for any questions
# File with questions DB schema
from images import Base
from sqlalchemy import *


# Question ORM class
class Question(Base):
    __tablename__ = "question"

    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(Text)

    def __init__(self, text: str):
        self.text = text


# Relations between questions and keywords
class QuestionToKeyword(Base):
    __tablename__ = "question_to_text"

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword_id = Column(Integer, ForeignKey("keyword.id"))
    question_id = Column(Integer, ForeignKey("question.id"))

    def __init__(self, keyword_id: int, quesion_id: int):
        self.keyword_id = keyword_id
        self.question_id = quesion_id

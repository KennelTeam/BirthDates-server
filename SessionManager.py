# copyright KennelTeam
# AndrusovN for any questions
# File with Database Session management
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dotenv import dotenv_values
from images import Base
from clustering_graph_db import Cluster, ClusterParentToChild, ClusterProductToCluster, ClusterToKeyword
from questions_db import Question, QuestionToKeyword
from users_db import User, Favourite
from singleton import singleton


# Main singleton class for session management
@singleton
class SessionManager:
    __engine = None
    __session = None

    def __init__(self):
        # load env values
        data = dotenv_values(".env")
        # connect to DB
        self.__engine = create_engine("{engine}://{username}:{password}@{db_address}/{db_name}?charset=utf8mb4"
                                      .format(engine=data['DATABASE_ENGINE'], username=data['DATABASE_USERNAME'],
                                              password=data['DATABASE_PASSWORD'], db_address=data['DATABASE_URL'],
                                              db_name=data['DATABASE_NAME']))

        # create session
        Base.metadata.create_all(self.__engine)
        self.__session = Session(self.__engine)

    # close session
    def __del__(self):
        self.__session.close()

    # return session
    def session(self):
        return self.__session

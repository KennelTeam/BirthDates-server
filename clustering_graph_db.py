from images import Base
from sqlalchemy import *


class Cluster(Base):
    __tablename__ = "cluster"

    id = Column(Integer, primary_key=True, autoincrement=True)

    def __init__(self):
        super().__init__()


class ClusterKeyword(Base):
    __tablename__ = "cluster_keyword"

    id = Column(Integer, primary_key=True, autoincrement=True)
    word = Column(VARCHAR(64), unique=True)

    def __init__(self, word: str):
        self.word = word


class ClusterToKeyword(Base):
    __tablename__ = "cluster_to_keyword"

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword_id = Column(Integer, ForeignKey("cluster_keyword.id"))
    cluster_id = Column(Integer, ForeignKey("cluster.id"))
    weight = Column(Float)

    def __init__(self, keyword_id: int, cluster_id: int, weight: float):
        self.cluster_id = cluster_id
        self.keyword_id = keyword_id
        self.weight = weight


class ClusterParentToChild(Base):
    __tablename__ = "cluster_parent_to_child"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("cluster.id"))
    child_id = Column(Integer, ForeignKey("cluster.id"))

    def __init__(self, parent_id: int, children_id: int):
        self.parent_id = parent_id
        self.child_id = children_id


class ClusterProductToCluster(Base):
    __tablename__ = "cluster_product_to_cluster"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cluster_id = Column(Integer, ForeignKey("cluster.id"))
    product_id = Column(Integer, ForeignKey("product.id"))

    def __init__(self, cluster_id: int, product_id: int):
        self.cluster_id = cluster_id
        self.product_id = product_id

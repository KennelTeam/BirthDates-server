# copyright KennelTeam
# AndrusovN for any questions
# File with database schema for clustering processes
from images import Base
from sqlalchemy import *


# Table with cluster ids
# All data about clusters is stored in other dbs. So Cluster has only ID
class Cluster(Base):
    __tablename__ = "cluster"

    id = Column(Integer, primary_key=True, autoincrement=True)

    def __init__(self, id: int = 0):
        super().__init__()
        if id != 0:
            self.id = id


# Relations between cluster and keywords
# pairs of type cluster_id, keyword_id, weight which mean that cluster has keyword with weight
class ClusterToKeyword(Base):
    __tablename__ = "cluster_to_keyword"

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword_id = Column(Integer, ForeignKey("keyword.id"))
    cluster_id = Column(Integer, ForeignKey("cluster.id"))
    weight = Column(Float)

    def __init__(self, keyword_id: int, cluster_id: int, weight: float):
        self.cluster_id = cluster_id
        self.keyword_id = keyword_id
        self.weight = weight


# Cluster tree parent to child relation - list of pairs of parent clusters and child clusters
class ClusterParentToChild(Base):
    __tablename__ = "cluster_parent_to_child"

    id = Column(Integer, primary_key=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("cluster.id"))
    child_id = Column(Integer, ForeignKey("cluster.id"))

    def __init__(self, parent_id: int, children_id: int):
        self.parent_id = parent_id
        self.child_id = children_id


# Relations between clusters and their child products
# Only leaf clusters have product childs
class ClusterProductToCluster(Base):
    __tablename__ = "cluster_product_to_cluster"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cluster_id = Column(Integer, ForeignKey("cluster.id"))
    product_id = Column(Integer, ForeignKey("product.id"))

    def __init__(self, cluster_id: int, product_id: int):
        self.cluster_id = cluster_id
        self.product_id = product_id

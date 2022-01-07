from SessionManager import SessionManager
from clustering_graph_db import ClusterProductToCluster, ClusterParentToChild, ClusterToKeyword, ClusterKeyword, Cluster
from sqlalchemy.sql import exists


def get_root_clusters():
    roots = SessionManager().session().query(Cluster).filter(Cluster.id.not_in(
        SessionManager().session().query(exists().where(ClusterParentToChild.child_id == Cluster.id))
    )).all()
    return [(cluster.id, get_cluster_keywords(cluster.id)) for cluster in roots]


def get_child_clusters(cluster_id: int):
    child = SessionManager().session().query(ClusterParentToChild).filter_by(parent_id=cluster_id).all()
    return [(cluster.id, get_cluster_keywords(cluster.id)) for cluster in child]


def get_cluster_keywords(cluster_id: int):
    data = SessionManager().session().query(ClusterToKeyword, ClusterKeyword)\
        .filter(ClusterToKeyword.keyword_id == ClusterKeyword.id)\
        .filter(ClusterToKeyword.cluster_id == cluster_id)\
        .all()
    return {keyword.word: item.weight for item, keyword in data}


def get_cluster_products(cluster_id: int):
    data = SessionManager().session().query(ClusterProductToCluster).filter_by(cluster_id=cluster_id).all()
    return [product.id for product in data]

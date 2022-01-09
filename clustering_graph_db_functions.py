from SessionManager import SessionManager
from clustering_graph_db import ClusterProductToCluster, ClusterParentToChild, ClusterToKeyword, Cluster
from images import Keyword
from sqlalchemy.sql import exists


def get_root_clusters():
    roots = SessionManager().session().query(Cluster).filter(~exists().where(ClusterParentToChild.child_id == Cluster.id)
    ).all()
    return [(cluster.id, get_cluster_keywords(cluster.id)) for cluster in roots]


def get_leaf_clusters():
    leafs = SessionManager().session().query(Cluster).filter(~exists().where(ClusterParentToChild.parent_id == Cluster.id)
    ).all()
    return get_clusters_keywords([leaf.id for leaf in leafs]).items()


def get_child_clusters(cluster_id: int):
    child = SessionManager().session().query(ClusterParentToChild).filter_by(parent_id=cluster_id).all()
    return [(cluster.id, get_cluster_keywords(cluster.id)) for cluster in child]


def get_cluster_keywords(cluster_id: int):
    data = SessionManager().session().query(ClusterToKeyword, Keyword)\
        .filter(ClusterToKeyword.keyword_id == Keyword.id)\
        .filter(ClusterToKeyword.cluster_id == cluster_id)\
        .all()
    return {keyword.word: item.weight for item, keyword in data}


def get_clusters_keywords(cluster_ids: list):
    data = SessionManager().session().query(ClusterToKeyword, Keyword)\
        .filter(ClusterToKeyword.keyword_id == Keyword.id)\
        .filter(ClusterToKeyword.cluster_id.in_(cluster_ids)).all()
    result = {}
    for pair, keyword in data:
        if pair.cluster_id not in result.keys():
            result[pair.cluster_id] = {}
        result[pair.cluster_id][keyword.word] = pair.weight
    return result


def get_cluster_products(cluster_id: int):
    data = SessionManager().session().query(ClusterProductToCluster).filter_by(cluster_id=cluster_id).all()
    return [product.id for product in data]

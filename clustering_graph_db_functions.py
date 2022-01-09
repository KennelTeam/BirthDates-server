# copyright KennelTeam
# AndrusovN for any questions
# file with main functions to work with clustering database part
from SessionManager import SessionManager
from clustering_graph_db import ClusterProductToCluster, ClusterParentToChild, ClusterToKeyword, Cluster
from images import Keyword
from sqlalchemy.sql import exists


# returns list of tuple id, {keyword: weight} for all root clusters
def get_root_clusters():
    roots = SessionManager().session().query(Cluster).filter(~exists().where(ClusterParentToChild.child_id == Cluster.id)
                                                             ).all()
    return [(cluster.id, get_cluster_keywords(cluster.id)) for cluster in roots]


# returns the list of tuple id, {keyword: weight} for all leaf clusters
def get_leaf_clusters():
    leafs = SessionManager().session().query(Cluster).filter(~exists().where(ClusterParentToChild.parent_id == Cluster.id)
                                                             ).all()
    return get_clusters_keywords([leaf.id for leaf in leafs]).items()


# returns list of (id, {keyword: weight}) for child clusters for given
def get_child_clusters(cluster_id: int):
    child = SessionManager().session().query(
        ClusterParentToChild).filter_by(parent_id=cluster_id).all()
    print([c.child_id for c in child])
    return list(get_clusters_keywords([c.child_id for c in child]).items())


# returns {keyword: weight} for given cluster
def get_cluster_keywords(cluster_id: int):
    data = SessionManager().session().query(ClusterToKeyword, Keyword)\
        .filter(ClusterToKeyword.keyword_id == Keyword.id)\
        .filter(ClusterToKeyword.cluster_id == cluster_id)\
        .all()
    return {keyword.word: item.weight for item, keyword in data}


# returns list of {keyword: weight} for given list of clusters
# this function is much faster than calling many get_cluster_keywords functions
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


# returns list of product_id's for given cluster (if cluster is not leaf, returns empty list)
def get_cluster_products(cluster_id: int):
    data = SessionManager().session().query(
        ClusterProductToCluster).filter_by(cluster_id=cluster_id).all()
    return [product.product_id for product in data]

"""copyright  KennelTeam
Yveega & AndrusovN for any questions
File with realizations of clustering-tree product recommendation algorithm
Products are stored in a clustering-tree, each cluster has it's own keywords
User is asked to choose keywords about their friend
By answering these questions user is going down by the tree
When user comes out in a leaf cluster, we show him gifts from this cluster
Clusterization part of algorithm is realized in clustering.py"""
import statistics
from clustering_graph_db_functions import get_root_clusters, get_child_clusters, get_cluster_products
from db_functions import get_product, get_products
from pprint import pprint


# Determine keywords to show to user by given lists of keywords in clusters
def words_to_ask(clusters_list):
    """Gets list of tuples of cluster id and dict of cluster keywords and it's coefficients
    Returns words, that most important to ask"""
    words_weight = dict()
    for cl_idx, (cl_id, cl) in enumerate(clusters_list):
        for word, weight in cl.items():
            if word in words_weight:
                words_weight[word][cl_idx] = weight
            else:
                words_weight[word] = [0] * len(clusters_list)
                words_weight[word][cl_idx] = weight

    sd_weights = list()
    for word in words_weight:
        sd_weights.append((statistics.stdev(words_weight[word]), word))
    sd_weights.sort(reverse=True)
    k_ask_words = min(15, len(sd_weights))
    words = [word for _, word in sd_weights[:k_ask_words]]
    pprint(words)
    return words


def choose_cluster(choosed_words, cluster_list):
    """Gets list of words, that was choosed by user and list of clusters in the same format that words_to_ask() gets
    Returns id of cluster that choosed user, basing on words, that he choose"""
    cluster_points = [0] * len(cluster_list)
    for idx, (cl_idx, cl) in enumerate(cluster_list):
        for word in choosed_words:
            cluster_points[idx] += cl.get(word, 0)
    max_cl = max(cluster_points)
    max_cl_idx = cluster_points.index(max_cl)
    # print("cluster_id: {}".format(max_cl_idx))
    return max_cl_idx


def user_choose(clusters_list):
    words = words_to_ask(clusters_list)
    print("Choose words, that describes your friend better then others (write numbers dividing with space):")
    for idx, w in enumerate(words):
        print(str(idx + 1) + ') ' + w, end='\n')
    ans = [words[int(i) - 1] for i in input().split()]
    return choose_cluster(ans, clusters_list)


class TreeSession:
    """Class for interaction between bot and algorithm functions"""
    def __init__(self):
        self.clusters = get_root_clusters()
        self.words = words_to_ask(self.clusters)
        self.products = []

    def new_answer(self, answers):
        """Gets list of words that choosed user
        Returns list of products if user has replied enough questions and [] if he hasn't"""
        pprint(self.clusters)
        new_cluster_id = self.clusters[choose_cluster(
            answers, self.clusters)][0]
        self.clusters = get_child_clusters(new_cluster_id)
        pprint(self.clusters)
        print("clusters")
        while len(self.clusters) == 1:
            self.clusters = get_child_clusters(self.clusters[0])
        if len(self.clusters) == 0:
            product_ids = get_cluster_products(new_cluster_id)
            pprint(product_ids)
            self.products = list(get_products(product_ids).values())
            pprint(self.products)
            print("products")
        else:
            self.words = words_to_ask(self.clusters)
        return self.products

    def get_question(self):
        """Returns list of words needed to ask"""
        return self.words

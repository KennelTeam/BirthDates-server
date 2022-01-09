# copyright Kennel Team
# AndrusovN or Yveega for any questions
# File with clustering algorithms
# All products are stored in a cluster's tree
# Every cluster has it's own keywords
# Cluster's keywords are generalized keywords of it's child keywords
# Generalization is a process of finding the best hyperonims for keywords:
# (computer, headphones) -> (electronic, device)
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from nltk.corpus import wordnet as wn
from images import Product, Keyword
from nltk.stem import PorterStemmer
import db_functions
from sklearn.feature_extraction.text import TfidfVectorizer
from SessionManager import SessionManager
from clustering_graph_db import Cluster, ClusterToKeyword, ClusterParentToChild, ClusterProductToCluster
from tqdm import tqdm
from pprint import pprint
import json

# porter to get the initial form of words
porter = PorterStemmer()
# Number of child cluster for each cluster
CLUSTER_DENSITY = 4
# maximum id of cluster currently stored in db (for saving to db)
cluster_id = 1
# maximum id of keyword currently stored in db
keyword_id = 1
# list of db objects to use session.bulk_save_objects()
db_clusters = []
db_keywords = []
db_pairs = []
db_parent_children = []
db_product_cluster = []
# dictionary of keywords and their ids
all_keywords = {}


# parse initial data from db to initialize system variables
def prepare_initials():
    global cluster_id, keyword_id, db_clusters, db_keywords, db_product_cluster, db_parent_children, db_pairs, \
        all_keywords
    cluster_id = 1
    keyword_id = 1
    db_clusters = []
    db_keywords = []
    db_pairs = []
    db_parent_children = []
    db_product_cluster = []
    all_keywords = {}
    keywords_labels = SessionManager().session().query(Keyword).all()
    all_keywords = {keyword.word: keyword.id for keyword in keywords_labels}
    keyword_id = max(all_keywords.values()) + 1


# load data about products from json
def prepare_data_json():
    return json.loads(open('product_keywords.json', 'r').read())


# load data about products from db
def prepare_data():
    total = SessionManager().session().query(Product).all()
    keywords = {}
    for product in tqdm(total):
        cur_keywords = db_functions.get_product_keywords(product.id)
        keywords[product.id] = cur_keywords
    return keywords


# LEGACY !!!
# generalization of wordset
def generalize_item(keywords: dict):
    keywords_sorted = sorted([(keywords[word], word) for word in keywords if len(wn.synsets(word)) > 0], reverse=True)
    k_main = min(20, len(keywords_sorted))
    keywords_sorted = keywords_sorted[:k_main]
    new_synsets = dict()
    # generate hyperonims for each word
    for k, word in keywords_sorted:
        # create synset
        synset = wn.synsets(word)[0]
        if synset in new_synsets:
            new_synsets[synset] += k
        else:
            new_synsets[synset] = k
        # generate hyperonims
        hypers = list(synset.closure(lambda s:s.hypernyms()))
        for idx, hyper in enumerate(hypers):
            # give each hyperonim weight based on similarity to the initial word
            if hyper in new_synsets:
                new_synsets[hyper] += k / (idx + 1)**0.5
            else:
                new_synsets[hyper] = k / (idx + 1)**0.5
    # order new synsets
    synsets_sorted = sorted([(new_synsets[syn], syn) for syn in new_synsets], reverse=True)
    # choose 15 the most
    k_synsets = min(15, len(synsets_sorted))
    # print(synsets_sorted[:k_synsets])
    synsets_sorted = synsets_sorted[:k_synsets]
    max_k = synsets_sorted[0][0]
    # return words from synsets
    for i in range(len(synsets_sorted)):
        synsets_sorted[i] = synsets_sorted[i][0] / max_k, synsets_sorted[i][1]
    synsets_dict = {syn.name().split('.')[0]: k for k, syn in synsets_sorted}
    return synsets_dict


# !!! LEGACY
# another way to generalize wordset
# iterate over every pair and add their hyperonim to the new wordset with weight of product of
# similarities to both initial words
def generalize_item_pairs(keywords: dict):
    # generate synsets
    keywords_sorted = sorted([(keywords[word], word) for word in keywords if len(wn.synsets(word)) > 0], reverse=True)
    k_main = min(20, len(keywords_sorted))
    keywords_sorted = keywords_sorted[:k_main]
    new_synsets = dict()
    # iterate over words
    for idx, (k1, word1) in enumerate(keywords_sorted):
        synset1 = wn.synsets(word1)[0]
        if synset1 in new_synsets:
            new_synsets[synset1] += k1
        else:
            new_synsets[synset1] = k1
        # for every pair of word
        for k2, word2 in keywords_sorted[idx + 1:]:
            # get lowest common hyperonim
            synset2 = wn.synsets(word2)[0]
            variants = synset1.lowest_common_hypernyms(synset2)
            if len(variants) == 0:
                continue
            hyper = variants[0]
            # print(">>", word1, word2, synset1, synset2, hyper)
            sim1 = synset1.path_similarity(hyper)
            if sim1 is None:
                sim1 = 0
            sim2 = synset2.path_similarity(hyper)
            if sim2 is None:
                sim2 = 0
            # multiply weight by the product of similarities
            k_new = (k1 + k2) * sim1 * sim2 * 8
            if hyper in new_synsets:
                new_synsets[hyper] += k_new
            else:
                new_synsets[hyper] = k_new
    # sort and get most good options
    synsets_sorted = sorted([(new_synsets[syn], syn) for syn in new_synsets], reverse=True)
    k_synsets = min(15, len(synsets_sorted))
    # print(synsets_sorted[:k_synsets])
    synsets_sorted = synsets_sorted[:k_synsets]
    max_k = synsets_sorted[0][0]
    # normalize the result
    for i in range(len(synsets_sorted)):
        synsets_sorted[i] = synsets_sorted[i][0] / max_k, synsets_sorted[i][1]
    synsets_dict = {syn.name().split('.')[0]: k for k, syn in synsets_sorted}
    return synsets_dict


# The actual working method of generalizing wordsets
def generalize_item_v3(keywords: dict):
    keywords_sorted = sorted([(keywords[word], word) for word in keywords if len(wn.synsets(word)) > 0], reverse=True)
    # print(keywords_sorted)
    k_main = min(20, len(keywords_sorted))
    keywords_sorted = keywords_sorted[:k_main]
    new_synsets = dict()
    # iterate over every pair of keywords and generate their LCH
    for idx, (k1, word1) in enumerate(keywords_sorted):
        synset1 = wn.synsets(word1)[0]
        new_synsets[synset1] = 0
        for k2, word2 in keywords_sorted[idx + 1:]:
            synset2 = wn.synsets(word2)[0]
            hyper = synset1.lowest_common_hypernyms(synset2)
            if len(hyper) > 0:
                new_synsets[hyper[0]] = 0
    # iterate over result LCHs and give them weights as a sum of similarities multiplied by initial word weights
    for k, word in keywords_sorted:
        synset_w = wn.synsets(word)[0]
        for synset in new_synsets:
            try:
                sim = synset_w.wup_similarity(synset)
            except Exception:
                sim = 0
            if sim is None:
                sim = 0
            new_synsets[synset] += k * sim**2
    # normalizing result
    for synset in new_synsets:
        new_synsets[synset] /= k_main
    # sorting and returning the best options
    synsets_sorted = sorted([(new_synsets[syn], syn) for syn in new_synsets], reverse=True)
    k_synsets = min(15, len(synsets_sorted))
    # print(synsets_sorted[:k_synsets])
    synsets_sorted = synsets_sorted[:k_synsets]
    max_k = synsets_sorted[0][0]
    for i in range(len(synsets_sorted)):
        synsets_sorted[i] = synsets_sorted[i][0] / max_k, synsets_sorted[i][1]
    synsets_dict = {syn.name().split('.')[0]: k for k, syn in synsets_sorted}
    return synsets_dict


# function to prepare dataset (matrix) by given keywords with weights
def prepare_dataset(items, parameters_count=200):
    texts = []
    all_words = set()
    ids_order = []
    # make texts
    for id in items.keys():
        item = items[id]
        ids_order.append(id)
        sm = 0
        for word in item.keys():
            sm += item[word]

        text = ""
        for word in item.keys():
            all_words.add(word)
            text += (word + " ") * int(item[word] / sm * 1000)
        texts.append(text)
    # use TfidfVectorizer
    vectorizer = TfidfVectorizer(max_features=parameters_count)
    vectors = vectorizer.fit_transform(texts)
    keywords = [""] * parameters_count
    # save keywords order to interpretate the results
    for word in all_words:
        if word in vectorizer.vocabulary_.keys():
            if vectorizer.vocabulary_[word] < parameters_count:
                keywords[vectorizer.vocabulary_[word]] = word
    vectors = StandardScaler().fit_transform(vectors.toarray())
    # return matrix, list of keywords corresponding to matrix columns and order of product id's corresponding to rows
    return vectors, keywords, ids_order


# clusterizing of matrix X into clusters_count clusters
def clusterize(X, clusters_count):
    clusters = KMeans(n_clusters=clusters_count, random_state=1).fit(X)
    # returns matrix with centers and list with parent clusters' ids
    return clusters.cluster_centers_, clusters.labels_


# one step of clusterization (small clusters into bigger ones) or products into the leaf clusters
# items - keywords with weights, clusters_count - number of clusters, generalize_func - function of generalizations
# of wordset
def clustering_step(items, clusters_count, generalize_func=generalize_item_v3):
    # prepare keywords
    prep_items = {}
    for id, item in enumerate(items):
        count = 0
        for word in item.keys():
            count += item[word]
        prep_items[id] = ({word: item[word] / count for word in item.keys()})
    items = prep_items
    # convert keywords into matrix
    X, keywords, ids_order = prepare_dataset(items)
    # clusterize
    centers, labels = clusterize(X, clusters_count)
    new_items = []
    # get the new keywords of result clusters
    for center_id in range(len(centers)):
        cur_keywords = {}
        for item_index in range(len(items)):
            if labels[item_index] == center_id:
                for word in items[item_index].keys():
                    if word not in cur_keywords.keys():
                        cur_keywords[word] = 0
                    cur_keywords[word] += items[item_index][word]
        new_items.append(generalize_func(cur_keywords))

    return new_items, labels


# process of saving clusters into db (when db objects are generated and stored in corresponding db_ lists)
def save_to_db():
    pprint(db_keywords)
    print("saving clusters")
    SessionManager().session().bulk_save_objects(db_clusters)
    SessionManager().session().commit()
    print("saving keywords")
    SessionManager().session().bulk_save_objects(db_keywords)
    SessionManager().session().commit()
    print("saving parent-child relations")
    SessionManager().session().bulk_save_objects(db_parent_children)
    SessionManager().session().commit()
    print("saving cluster-keyword relations")
    SessionManager().session().bulk_save_objects(db_pairs)
    SessionManager().session().commit()
    print("saving cluster-product relations")
    SessionManager().session().bulk_save_objects(db_product_cluster)
    SessionManager().session().commit()


# function to save one cluster to db (should be saved from roots to leafs)
def save_cluster(keywords, parent_id: int = 0):
    global cluster_id
    global keyword_id
    global all_keywords
    global db_pairs, db_clusters, db_keywords, db_parent_children

    # create db object
    cluster = Cluster(cluster_id)
    db_clusters.append(cluster)
    cluster_id += 1
    # SessionManager().session().add(cluster)

    # iterate over keywords to save they and the relations
    keyword_ids = []
    for keyword in keywords.keys():
        if len(keyword) > 32:
            continue
        # kw = SessionManager().session().query(ClusterKeyword).filter_by(word=keyword).all()
        if keyword not in all_keywords.keys():
            new_keyword = Keyword(keyword, keyword_id)
            all_keywords[keyword] = keyword_id
            keyword_id += 1
            # SessionManager().session().add(new_keyword)
            # SessionManager().session().commit()
            # SessionManager().session().refresh(new_keyword)
            db_keywords.append(new_keyword)
            keyword_ids.append((new_keyword.id, keywords[keyword]))
        else:
            keyword_ids.append((all_keywords[keyword], keywords[keyword]))

    for id, weight in keyword_ids:
        new_pair = ClusterToKeyword(id, cluster.id, weight)
        db_pairs.append(new_pair)
        # SessionManager().session().add(new_pair)

    if parent_id != 0:
        parentToChild = ClusterParentToChild(parent_id, cluster.id)
        db_parent_children.append(parentToChild)
        # SessionManager().session().add(parentToChild)

    # SessionManager().session().commit()
    return cluster.id


# saving a product in the cluster (adding relation to db)
def add_product_to_cluster(cluster_id: int, product_id: int):
    db_product_cluster.append(ClusterProductToCluster(cluster_id, product_id))


# the clearing db process before saving new clustering data
def clear_db():
    SessionManager().session().query(ClusterToKeyword).delete()
    SessionManager().session().query(ClusterParentToChild).delete()
    SessionManager().session().query(ClusterProductToCluster).delete()
    SessionManager().session().query(Cluster).delete()
    SessionManager().session().commit()


# saving all clustering data
def save_all(steps: int, cluster_words, cluster_children, product_ids):
    print("saving base clusters")
    prev_ids = []
    for cluster in cluster_words[-1]:
        id = save_cluster(cluster)
        prev_ids.append(id)

    print("base clusters saved")
    # remember ids of previous clusters to know parents of current layes of tree
    for i in range(steps - 1):
        print("saving clusters. step {} of {}".format(i + 1, steps - 1))
        nprev_ids = []
        for index, parent in enumerate(cluster_children[steps - i]):
            parent_id = prev_ids[parent]
            id = save_cluster(cluster_words[steps - i - 1][index], parent_id)
            nprev_ids.append(id)
        prev_ids = nprev_ids

    print("saving products relations")
    for id, parent in enumerate(cluster_children[1]):
        parent_id = prev_ids[parent]
        add_product_to_cluster(parent_id, product_ids[id])
    print("saving to db")
    save_to_db()


# function of clustering if initial data is already loaded
def make_clustering_predata(steps: int, initial_data):
    prep_data = []
    ids_order = []
    # prepare data
    for id in initial_data.keys():
        ids_order.append(id)
        prep_data.append(initial_data[id])

    print("data prepared")
    # list of dicts with keywords of each cluster (one list item is keywords for all clusters of one layer of tree)
    cluster_words = [prep_data]
    # list of list of children relations of the previous layer
    cluster_children = [[]]
    product_ids = ids_order
    for i in range(steps):
        print("{} steps done".format(i))
        new_data, new_labels = clustering_step(cluster_words[-1], CLUSTER_DENSITY ** (steps - i), generalize_item_v3)

        cluster_words.append(new_data)
        cluster_children.append([int(item) for item in new_labels])

    # save results into json to never lose them
    with open('clustering_info.json', 'w') as output:
        output.write(json.dumps(
            {
                'words': cluster_words,
                'children': cluster_children,
                'product_ids': product_ids
             }
        ))
    # save results to db
    clear_db()
    save_all(steps, cluster_words, cluster_children, product_ids)


# the whole process of clustering
def make_clustering(steps: int):
    prepare_initials()
    initial_data = prepare_data_json()
    make_clustering_predata(steps, initial_data)

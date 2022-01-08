from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import nltk
from nltk.corpus import wordnet as wn
from images import Product
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from string import punctuation
from nltk.stem import PorterStemmer
import db_functions
from sklearn.feature_extraction.text import TfidfVectorizer
from SessionManager import SessionManager
from clustering_graph_db import Cluster, ClusterKeyword, ClusterToKeyword, ClusterParentToChild, ClusterProductToCluster

porter = PorterStemmer()
KEYWORD_WEIGHT = 1
nltk.download('wordnet')


def prepare_data():
    total = SessionManager().session().query(Product).all()
    keywords = {}
    for id, product in enumerate(total):
        # text = product.name + "\n" + product.description
        # words = word_tokenize(text)
        cur_keywords = {}
        # for word in words:
        #     if word not in stopwords.words("english") and word not in punctuation:
        #         word = porter.stem(word).lower()
        #         if word not in cur_keywords.keys():
        #             cur_keywords[word] = 0
        #         cur_keywords[word] += 1
        product_keywords = db_functions.get_product_keywords(product.id)
        for word in product_keywords:
            if word not in cur_keywords.keys():
                cur_keywords[word] = 0
            cur_keywords[word] += KEYWORD_WEIGHT
        keywords[product.id] = cur_keywords
    return keywords


def generalize_item(keywords: dict):
    keywords_sorted = sorted([(keywords[word], word) for word in keywords if len(wn.synsets(word)) > 0], reverse=True)
    # print(keywords_sorted)
    k_main = min(20, len(keywords_sorted))
    keywords_sorted = keywords_sorted[:k_main]
    new_synsets = dict()
    for k, word in keywords_sorted:
        synset = wn.synsets(word)[0]
        if synset in new_synsets:
            new_synsets[synset] += k
        else:
            new_synsets[synset] = k
        hypers = list(synset.closure(lambda s:s.hypernyms()))
        for idx, hyper in enumerate(hypers):
            if hyper in new_synsets:
                new_synsets[hyper] += k / (idx + 1)**0.5
            else:
                new_synsets[hyper] = k / (idx + 1)**0.5
    synsets_sorted = sorted([(new_synsets[syn], syn) for syn in new_synsets], reverse=True)
    k_synsets = min(15, len(synsets_sorted))
    # print(synsets_sorted[:k_synsets])
    synsets_sorted = synsets_sorted[:k_synsets]
    max_k = synsets_sorted[0][0]
    for i in range(len(synsets_sorted)):
        synsets_sorted[i] = synsets_sorted[i][0] / max_k, synsets_sorted[i][1]
    synsets_dict = {syn.name().split('.')[0]: k for k, syn in synsets_sorted}
    return synsets_dict


def generalize_item_pairs(keywords: dict):
    keywords_sorted = sorted([(keywords[word], word) for word in keywords if len(wn.synsets(word)) > 0], reverse=True)
    # print(keywords_sorted)
    k_main = min(20, len(keywords_sorted))
    keywords_sorted = keywords_sorted[:k_main]
    new_synsets = dict()
    for idx, (k1, word1) in enumerate(keywords_sorted):
        synset1 = wn.synsets(word1)[0]
        if synset1 in new_synsets:
            new_synsets[synset1] += k1
        else:
            new_synsets[synset1] = k1
        for k2, word2 in keywords_sorted[idx + 1:]:
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
            k_new = (k1 + k2) * sim1 * sim2 * 8
            if hyper in new_synsets:
                new_synsets[hyper] += k_new
            else:
                new_synsets[hyper] = k_new
    synsets_sorted = sorted([(new_synsets[syn], syn) for syn in new_synsets], reverse=True)
    k_synsets = min(15, len(synsets_sorted))
    # print(synsets_sorted[:k_synsets])
    synsets_sorted = synsets_sorted[:k_synsets]
    max_k = synsets_sorted[0][0]
    for i in range(len(synsets_sorted)):
        synsets_sorted[i] = synsets_sorted[i][0] / max_k, synsets_sorted[i][1]
    synsets_dict = {syn.name().split('.')[0]: k for k, syn in synsets_sorted}
    return synsets_dict


def generalize_item_v3(keywords: dict):
    keywords_sorted = sorted([(keywords[word], word) for word in keywords if len(wn.synsets(word)) > 0], reverse=True)
    # print(keywords_sorted)
    k_main = min(20, len(keywords_sorted))
    keywords_sorted = keywords_sorted[:k_main]
    new_synsets = dict()
    for idx, (k1, word1) in enumerate(keywords_sorted):
        synset1 = wn.synsets(word1)[0]
        new_synsets[synset1] = 0
        for k2, word2 in keywords_sorted[idx + 1:]:
            synset2 = wn.synsets(word2)[0]
            hyper = synset1.lowest_common_hypernyms(synset2)
            if len(hyper) > 0:
                new_synsets[hyper[0]] = 0

    for k, word in keywords_sorted:
        synset_w = wn.synsets(word)[0]
        for synset in new_synsets:
            sim = synset_w.path_similarity(synset)
            if sim is None:
                sim = 0
            new_synsets[synset] += k * sim

    for synset in new_synsets:
        new_synsets[synset] /= k_main

    synsets_sorted = sorted([(new_synsets[syn], syn) for syn in new_synsets], reverse=True)
    k_synsets = min(15, len(synsets_sorted))
    # print(synsets_sorted[:k_synsets])
    synsets_sorted = synsets_sorted[:k_synsets]
    max_k = synsets_sorted[0][0]
    for i in range(len(synsets_sorted)):
        synsets_sorted[i] = synsets_sorted[i][0] / max_k, synsets_sorted[i][1]
    synsets_dict = {syn.name().split('.')[0]: k for k, syn in synsets_sorted}
    return synsets_dict


# d = {"phone": 0.3, "computer": 0.3, "pc": 0.26, "headphones": 0.25, "wireless": 0.05, "tech": 0.23, "sound": 0.18, "speaker": 0.2}
#
# print(generalize_item_v3(d))

def prepare_dataset(items, parameters_count=200):
    texts = []
    all_words = set()
    ids_order = []
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
    vectorizer = TfidfVectorizer(max_features=parameters_count)
    vectors = vectorizer.fit_transform(texts)
    keywords = [""] * parameters_count
    for word in all_words:
        if word in vectorizer.vocabulary_.keys():
            if vectorizer.vocabulary_[word] < parameters_count:
                keywords[vectorizer.vocabulary_[word]] = word
    vectors = StandardScaler().fit_transform(vectors.toarray())
    return vectors, keywords, ids_order


def clusterize(X, clusters_count):
    clusters = KMeans(n_clusters=clusters_count, random_state=1).fit(X)
    return clusters.cluster_centers_, clusters.labels_


def clustering_step(items, clusters_count, generalize_func=generalize_item_v3):
    prep_items = {}
    for id in items.keys():
        item = items[id]
        count = 0
        for word in item.keys():
            count += item[word]
        prep_items[id] = ({word: item[word] / count for word in item.keys()})
    items = prep_items

    X, keywords, ids_order = prepare_dataset(items)
    centers, labels = clusterize(X, clusters_count)
    new_items = []

    for center_id in range(len(centers)):
        cur_keywords = {}
        for item_index in range(len(items)):
            if labels[item_index] == center_id:
                for word in items[item_index].keys():
                    if word not in cur_keywords.keys():
                        cur_keywords[word] = 0
                    cur_keywords[word] += items[item_index][word]
        new_items.append(generalize_func(cur_keywords))

    return new_items, labels, ids_order


CLUSTER_DENSITY = 4


def save_cluster(keywords, parent_id: int = 0):
    cluster = Cluster()
    SessionManager().session().add(cluster)
    SessionManager().session().commit()
    SessionManager().session().refresh(cluster)

    keyword_ids = []
    for keyword in keywords.keys():
        kw = SessionManager().session().query(ClusterKeyword).filter_by(word=keyword).all()
        if len(kw) == 0:
            new_keyword = ClusterKeyword(keyword)
            SessionManager().session().add(new_keyword)
            SessionManager().session().commit()
            SessionManager().session().refresh(new_keyword)
            keyword_ids.append((new_keyword.id, keywords[keyword]))
        else:
            keyword_ids.append((kw[0].id, keywords[keyword]))

    for id, weight in keyword_ids:
        new_pair = ClusterToKeyword(id, cluster.id, weight)
        SessionManager().session().add(new_pair)

    if parent_id != 0:
        parentToChild = ClusterParentToChild(parent_id, cluster.id)
        SessionManager().session().add(parentToChild)

    SessionManager().session().commit()
    return cluster.id


def add_product_to_cluster(cluster_id: int, product_id: int):
    SessionManager().session().add(ClusterProductToCluster(cluster_id, product_id))
    SessionManager().session().commit()


def clear_db():
    SessionManager().session().query(ClusterToKeyword).delete()
    SessionManager().session().query(ClusterParentToChild).delete()
    SessionManager().session().query(ClusterProductToCluster).delete()
    SessionManager().session().query(ClusterKeyword).delete()
    SessionManager().session().query(Cluster).delete()
    SessionManager().session().commit()


def make_clustering(steps: int):
    clear_db()
    initial_data = prepare_data()
    print("data prepared")
    cluster_words = [initial_data]
    cluster_children = [[]]
    product_ids = []
    for i in range(steps):
        print("{} steps done".format(i))
        new_data, new_labels, ids_order = clustering_step(cluster_words[-1], CLUSTER_DENSITY**(steps - i), generalize_item_v3)
        if i == 0:
            product_ids = ids_order
        cluster_words.append(new_data)
        cluster_children.append(new_labels)

    print("saving base clusters")
    prev_ids = []
    for cluster in cluster_words[-1]:
        id = save_cluster(cluster)
        prev_ids.append(id)

    print("base clusters saved")
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

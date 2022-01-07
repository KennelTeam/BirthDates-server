from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import nltk
import random
from nltk.corpus import wordnet as wn
from SessionManager import SessionManager
from images import Product
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from string import punctuation
from nltk.stem import PorterStemmer
import db_functions
from sklearn.feature_extraction.text import TfidfVectorizer

porter = PorterStemmer()
KEYWORD_WEIGHT = 6
nltk.download('wordnet')


def prepare_data():
    keywords = []
    for product in SessionManager().session().query(Product).all():
        text = product.name + "\n" + product.description
        words = word_tokenize(text)
        cur_keywords = {}
        for word in words:
            if word not in stopwords.words("english") and word not in punctuation:
                word = porter.stem(word).lower()
                if word not in cur_keywords.keys():
                    cur_keywords[word] = 0
                cur_keywords[word] += 1
        product_keywords = db_functions.get_product_keywords(product.id)
        for word in product_keywords:
            if word not in cur_keywords.keys():
                cur_keywords[word] = 0
            cur_keywords[word] += KEYWORD_WEIGHT
        keywords.append(cur_keywords)
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
    synsets_dict = {syn.name().split('.')[0]: k for k, syn in synsets_sorted[:k_synsets]}
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
            hyper = synset1.lowest_common_hypernyms(synset2)[0]
            print(">>", word1, word2, synset1, synset2, hyper)
            k_new = (k1 + k2) * synset1.path_similarity(hyper) * synset2.path_similarity(hyper) * 8
            if hyper in new_synsets:
                new_synsets[hyper] += k_new
            else:
                new_synsets[hyper] = k_new
    synsets_sorted = sorted([(new_synsets[syn], syn) for syn in new_synsets], reverse=True)
    k_synsets = min(15, len(synsets_sorted))
    # print(synsets_sorted[:k_synsets])
    synsets_dict = {syn.name().split('.')[0]: k for k, syn in synsets_sorted[:k_synsets]}
    return synsets_dict


# d = {"phone": 0.3, "computer": 0.3, "pc": 0.26, "headphones": 0.25, "wireless": 0.05, "tech": 0.23, "sound": 0.18, "speaker": 0.2}
#
# print(generalize_item_pairs(d))

def prepare_dataset(items, parameters_count=200):
    texts = []
    all_words = set()
    for item in items:
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
    return vectors, keywords


def clusterize(X, clusters_count):
    clusters = KMeans(n_clusters=clusters_count, random_state=1).fit(X)
    return clusters.cluster_centers_, clusters.labels_


def clustering_step(items, clusters_count):
    prep_items = []
    for item in items:
        count = 0
        for word in item.keys():
            count += item[word]
        prep_items.append({word: item[word] / count for word in item.keys()})
    items = prep_items

    X, keywords = prepare_dataset(items)
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
        new_items.append(generalize_item(cur_keywords))

    return new_items, labels


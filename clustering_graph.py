from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

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


def generalize_item(keywords):
    return keywords


def prepare_dataset(items, parameters_count=200):
    texts = []
    all_words = set()
    for item in items:
        text = ""
        for word in item.keys():
            all_words.add(word)
            text += (word + " ") * item[word]
        texts.append(text)
    vectorizer = TfidfVectorizer(max_features=parameters_count)
    vectors = vectorizer.fit_transform(texts)
    keywords = [""] * parameters_count
    for word in all_words:
        if word in vectorizer.vocabulary_.keys():
            if vectorizer.vocabulary_[word] < parameters_count:
                keywords[vectorizer.vocabulary_[word]] = word
    vectors = StandardScaler().fit_transform(vectors)
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


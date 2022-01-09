from SessionManager import SessionManager
from images import Product, ProductKeyword
import numpy as np
import sklearn
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk import word_tokenize
from sklearn.cluster import DBSCAN
from sklearn import metrics
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.cluster import AffinityPropagation
import collections
from sklearn.decomposition import PCA
from pprint import pprint
from nltk.corpus import stopwords
nltk.download("stopwords")
CLUSTERS = 10


def clusterize(products):
    pass


def clusterize():
    data = []
    products = []
    for product in SessionManager().session().query(Product).all():
        products.append(product.to_json())
        words = nltk.word_tokenize(product.name + "\n" + product.description)
        words = [word for word in words if word.isalpha(
        ) and word not in stopwords.words("english")]
        data.append(' '.join(words))
        print(data[-1])
    vectorizer = TfidfVectorizer(max_features=50)
    vectors = vectorizer.fit_transform(data)
    print(vectors.shape)
    result_data = []
    for i in range(len(products)):
        test = vectors[i].A
        arr = np.array([[float(products[i]["cost"]), float(products[i]["reviews_count"]),
                        float(products[i]["avg_rating"])]])
        test = np.concatenate((test, arr), axis=1)
        # print(test)
        result_data.append(test.flatten())
    result_data = StandardScaler().fit_transform(np.array(result_data))
    print(result_data[1])
    # result_data = np.array(result_data)
    print(result_data.shape)
    # print(result_data)
    db = KMeans(n_clusters=CLUSTERS, random_state=1).fit(result_data)
    # pca = PCA(n_features=2)
    # pca.fit(result_data)
    # db = AffinityPropagation(random_state=5).fit(result_data)
    for i in db.cluster_centers_:
        print(i)

    links = {}
    words = {}
    all_words = set()
    for d in data:
        all_words = all_words.union(set(d.split()))
    for word in all_words:
        if word.lower() in vectorizer.vocabulary_.keys():
            words[vectorizer.vocabulary_[word.lower()]] = word.lower()
    keywords = {}
    pprint(vectorizer.vocabulary_)
    pprint(all_words)
    pprint(words)
    for i in range(CLUSTERS):
        links[i] = []
        arr = db.cluster_centers_[i]
        top = sorted(list(range(len(arr[:-3]))),
                     key=lambda x: arr[x], reverse=True)
        keywords[i] = []
        for j in range(15):
            keywords[i].append((words[top[j]], arr[top[j]]))
        for j in range(len(products)):
            if db.labels_[j] == i:
                links[i].append(
                    "https://amazon.com/dp/{}".format(products[j]["asin"][:-1]))
    pprint(links)
    pprint(keywords)
    return db.labels_


result = clusterize()
counter = collections.Counter(list(result))
print(counter)

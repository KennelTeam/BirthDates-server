# import nltk
import concurrent
import json

from nltk.corpus import wordnet as wn
from keywords import get_keywords_koe
from clustering_graph_db_functions import get_leaf_clusters, get_cluster_products  # commented for testing
from db_functions import get_product_keywords, get_product, get_products_keywords, get_products  # commented for testing
from tqdm import tqdm
import concurrent.futures
from pprint import pprint
from nltk.corpus import sentiwordnet as swn
from SessionManager import SessionManager
from images import Keyword, Product, ProductKeyword
from questions_db import Question, QuestionToKeyword
from threading import Lock
synset_lock = Lock()

MAX_THREADS_COUNT = 10
WORDS_COMPARISON = {}


def get_unique_question_keywords():
    query = SessionManager().session().query(Keyword.word).filter(Keyword.id.in_(
        SessionManager().session().query(QuestionToKeyword.keyword_id)
    )).distinct()
    return [item[0] for item in query]


def get_unique_product_keywords():
    query = SessionManager().session().query(Keyword.word).filter(Keyword.id.in_(
        SessionManager().session().query(ProductKeyword.keyword_id)
    )).distinct()
    return [item[0] for item in query]


def load_calcs():
    global WORDS_COMPARISON
    WORDS_COMPARISON = json.loads(open("precalced-synsets.json", 'r').read())


def prepare_calcs():
    global WORDS_COMPARISON
    product_words = get_unique_product_keywords()
    question_words = get_unique_question_keywords()
    question_syns = {}
    product_syns = {}
    for word in tqdm(question_words):
        synsets = wn.synsets(word)
        if len(synsets) > 0:
            question_syns[word] = synsets[0]
        else:
            question_syns[word] = None
    for word in tqdm(product_words):
        synsets = wn.synsets(word)
        if len(synsets) > 0:
            product_syns[word] = synsets[0]
        else:
            product_syns[word] = None

    for p_word in tqdm(product_words):
        for q_word in question_words:
            if product_syns[p_word] is not None and question_syns[q_word] is not None:
                if p_word not in WORDS_COMPARISON.keys():
                    WORDS_COMPARISON[p_word] = {}
                WORDS_COMPARISON[p_word][q_word] = wn.wup_similarity(product_syns[p_word], question_syns[q_word])

    with open('precalced-synsets.json', 'w') as output:
        output.write(json.dumps(WORDS_COMPARISON))


def get_words_similarity(product_word, question_word):
    if product_word not in WORDS_COMPARISON.keys():
        return 0
    if question_word not in WORDS_COMPARISON[product_word].keys():
        return 0
    return WORDS_COMPARISON[product_word][question_word]


def compare_word_lists(word_weights1, word_weights2):
    return compare_word_lists_threaded(word_weights1, word_weights2, 0, 0)[0]


def compare_word_list_precalced(product_word_weights, question_word_weights):
    similarity = 0
    for p_word, k1 in product_word_weights.items():
        for q_word, k2 in question_word_weights.items():
            similarity += k1 * k2 * get_words_similarity(p_word, q_word)
    similarity /= len(product_word_weights) * len(question_word_weights)
    return similarity


def compare_word_lists_threaded(word_weights1, word_weights2, index, id):
    synsets1 = []
    for word, k in word_weights1.items():
        synsets = wn.synsets(word)
        if len(synsets) == 0:
            continue
        synsets1.append((synsets[0], k))
    synsets2 = []
    for word, k in word_weights2.items():
        synsets = wn.synsets(word)
        if len(synsets) == 0:
            continue
        synsets2.append((synsets[0], k))
    similarity = 0
    for syn1, k1 in synsets1:
        for syn2, k2 in synsets2:
            sim = syn1.path_similarity(syn2)
            if sim is None:
                sim = 0
            similarity += sim * k1 * k2
    similarity /= len(word_weights1) * len(word_weights2)
    return similarity, index, id


def calc_similarities(batch, user_text):
    out = [None] * len(batch)
    for index, item in enumerate(batch):
        out[index] = item[0], compare_word_lists(user_text, item[1])
    return out


def calc_similarities_threaded(batch, user_text):
    out = [None] * len(batch)
    # for item in batch:
    #     pprint(item)

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(batch)) as executor:
        future_to_similarity = (executor.submit(compare_word_lists_threaded, user_text, batch[i][1], i, batch[i][0])
                                for i in range(len(batch)))
        for future in concurrent.futures.as_completed(future_to_similarity):
            similarity_and_index = future.result()
            if similarity_and_index:
                similarity, index, id = similarity_and_index
                out[index] = id, similarity
    return out


def choose_gifts(information: str):
    print("choosing gift")
    # print("Write something about your friend:")
    # information = input('>>')
    user_keywords = get_keywords_koe(information)
    # while len(user_keywords) < 3:
    #     print("Write more, please")
    #     information += input('>>')
    #     user_keywords = get_keywords_koe(information)
    # print("User keywords", user_keywords)
    max_similarity = 0
    max_cluster_id = -1
    print("getting clusters")
    clusters = list(get_leaf_clusters())
    print("clusters received")
    similarities = []
    for i in tqdm(range(len(clusters) // MAX_THREADS_COUNT)):
        begin_index, end_index = i * MAX_THREADS_COUNT, min(len(clusters), (i + 1)*MAX_THREADS_COUNT)
        current_batch = clusters[begin_index:end_index]
        # similarities += calc_similarities_threaded(current_batch, user_keywords)
        similarities += calc_similarities(current_batch, user_keywords)

    max_cluster_id = max(similarities, key=lambda x: x[1])[0]

    print("getting products")
    product_ids = get_cluster_products(max_cluster_id)
    products_list = []
    products_keywords = get_products_keywords(product_ids)
    for product_id in product_ids:
        product_keywords = products_keywords[product_id]
        if len(product_keywords) == 0:
            continue
        # print("Product keywords", product_keywords)
        similarity = compare_word_lists(user_keywords, product_keywords)
        products_list.append((similarity, product_id))
    products_list.sort(reverse=True)
    print("preparing answers")
    products = get_products(product_ids)
    return [products[p[1]] for p in products_list]
    # for _, product_id in products_list:
    #     print(get_product(product_id))


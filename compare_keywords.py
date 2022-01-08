import nltk
from nltk.corpus import wordnet as wn
from clustering_graph import prepare_data, clustering_step, generalize_item_v3

nltk.download('wordnet')


def compare_word_lists(words1, word_weights2):
    synsets1 = []
    for word in words1:
        synsets1.append(wn.synsets(word)[0])
    synsets2 = []
    for word, k in word_weights2.items():
        synsets2.append((wn.synsets(word)[0], k))
    similarity = 0
    for syn1 in synsets1:
        for syn2, k in synsets2:
            similarity += syn1.path_similarity(syn2) * k
    similarity /= len(words1) * len(word_weights2)
    return similarity


def prepare_clusters():
    items = prepare_data()

    clusters, labels, ids_order = clustering_step(items, 50, generalize_item_v3)


def choose_presents():
    pass
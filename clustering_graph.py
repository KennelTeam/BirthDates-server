import nltk
import random
nltk.download('wordnet')
from nltk.corpus import wordnet as wn

# initial preparation of products
def prepare_data():
    pass


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
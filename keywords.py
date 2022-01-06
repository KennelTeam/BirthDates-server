import spacy
from string import punctuation
from collections import Counter

nlp = spacy.load('en_core_web_trf')


def get_keywords(text):
    text = text.lower()
    result = []
    pos_tag = ['PROPN', 'ADJ', 'NOUN']
    doc = nlp(text)
    for token in doc.ents:
        # if token in nlp.Defaults.stop_words or token in punctuation:
        #     continue
        if len(token.text) < 64:
            result.append(token.text)
    return result

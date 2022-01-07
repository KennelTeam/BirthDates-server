import spacy
from string import punctuation
from collections import Counter
import re

nlp = spacy.load('en_core_web_sm')


def get_keywords(text):
    text = text.lower()
    result = []
    # pos_tag = ['PROPN', 'ADJ', 'NOUN']
    doc = nlp(text)
    for token in doc.ents:
        if len(token.text) < 32 and bool(re.match(r"([a-zA-Z][ ]*)+$", token.text)):
            result.append(token.text)
    return list(set(result))

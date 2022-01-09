from nltk.corpus import wordnet as wn
from questions_db_functions import add_question
from tqdm import tqdm
from SessionManager import SessionManager


def load_questions():
    with open('questions.txt') as f:
        inp = f.readlines()

    res = []
    for line in inp:
        question, inp_keywords = line.split('[')
        inp_keywords = inp_keywords[:inp_keywords.index(']')]
        keywords = inp_keywords.split(', ')
        keywords_filtered = [word for word in keywords if len(wn.synsets(word)) > 0]
        if len(keywords_filtered) < 5:
            print("CRINGE:", question, keywords, "->", keywords_filtered)
        res.append({
            'question': question,
            'keywords': keywords})

    for item in tqdm(res):
        add_question(item['question'], item['keywords'])

    SessionManager().session().commit()


load_questions()

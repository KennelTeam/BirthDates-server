# copyright KennelTeam
# AndrusovN or Yveega for any questions
# File with realization of Bayesian product reccommendation algorithm.
# Each product has it's own probability normal distribution in the question-answer space
# User is moving through this space by answering questions
# When user asks for product to recommend, we get for him list of products with most probabilities
# To prelearn this model, we generate set of answers like this: how would user answer all questions if they
# would want to get right current product recommended? So for each product we generate such set of answers
# and train sklearn.naive_bayes.MultinomialNB on that data
# Then save it to Bayes-model.model file and use
# It is planned to add training based on user's answers

from compare_keywords import compare_word_lists, compare_word_list_precalced, prepare_calcs, load_calcs
from keywords import get_keywords_koe
from sklearn.naive_bayes import MultinomialNB
from db_functions import get_product, get_all_products_keywords
import random
import pickle
import numpy as np
from questions_db_functions import get_all_questions
from tqdm import tqdm
import multiprocessing as mp
import threading as tr
import json
from math import ceil
from nltk.corpus import wordnet as wn


# Number of products to show after choosing
K_PRODUCTS = 15
# Presaved questions list. Pulled from DB on start, to save time later
QUESTIONS = None


# Function to train Bayesian model on automatically generated data from product info
def train_all():
    # The first step is to precalculate synset.wup_similarities for each pair of keywords from question and
    # from product. This step is needed to speed up computations
    print("precalcing synsets")
    # prepare_calcs()
    # or load precalcs from json
    load_calcs()
    # The second step is pulling all questions from DataBase
    print("getting all questions")
    global QUESTIONS
    QUESTIONS = get_all_questions()
    print("all questions got")
    # The third step is pulling all products from database
    products = get_all_products_keywords()
    print("all products got")
    # The fourth step is preparing dataset i.e. generating vectors of answers given by imaginary users
    answers, product_ids = prepare_dataset(products, QUESTIONS)
    print("dataset prepared")
    # The last step is training
    train_nn(answers, product_ids)
    print("network saved")


# A function to make prediction - what would answer user to get this product
# q_keywords - keywords for questions
# product_keywords - keywords of product
def predict_user_answer(q_keywords: list, product_keywords: dict):
    q_keywords_dict = {word: 1 for word in q_keywords}
    # calculate similarity between two word sets to find out how near are they
    similarity = compare_word_list_precalced(product_keywords, q_keywords_dict)
    result = 1 if similarity > 0.06 else 0
    # q.put(result)
    return result


# Function to prepare dataset to prelearn Bayesian NN
def prepare_dataset(products_keywords: dict, question_keywords: list):
    q_keywords = [q['keywords'] for q in question_keywords]

    answers = list()
    product_keyword_list = list(products_keywords.items())
    # product_ids, products = zip(*product_keyword_list)
    product_ids = []
    # make the matrix with hypothetical user's answers for each product
    for product_id, product in tqdm(product_keyword_list):
        product_ids.append(product_id)
        result = []
        # for each question predict user's answers
        for q in q_keywords:
            result.append(predict_user_answer(q, product))
        answers.append(result)
    return answers, product_ids


# train sklearn model on data
# answers - matrix with user's answers
# products - the right products to recommend after <answers> answers given
def train_nn(answers, products):
    clf = MultinomialNB()
    clf.fit(answers, products)
    data = pickle.dumps(clf)
    with open('Bayes_model_bytes.model', 'wb') as model_file:
        model_file.write(data)


# function to choose gifts based on user's answers
def choose_gifts(user_answers):
    with open('Bayes_model_bytes.model', 'rb') as model_file:
        clf = pickle.loads(model_file.read())
    ans = clf.predict_proba(user_answers)
    product_ids = clf.classes_[np.flip(np.argsort(ans))][:K_PRODUCTS]
    return [get_product(id) for id in product_ids]


# class to communicate with bot and store user's game session
class BayesSession:
    def __init__(self):
        # answers - vector of answers to all questions
        self.answers = [0.5] * len(QUESTIONS)
        # the queue of ids of unanswered questions (shuffled)
        self.unanswered_ids = list(range(len(QUESTIONS)))
        # id of last asked question
        print(self.unanswered_ids)
        self.last_q_id = None
        random.shuffle(self.unanswered_ids)

    # when answer is given
    def new_answer(self, answer):
        self.answers[self.last_q_id] = answer

    # getting the next question
    def get_question(self):
        print("get question")
        if len(self.unanswered_ids) == 0:
            return None
        self.last_q_id = self.unanswered_ids.pop()
        return QUESTIONS[self.last_q_id]

    # get the set of recommended gifts
    def get_presents(self):
        return choose_gifts(self.answers)

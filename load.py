from nltk.corpus import wordnet as wn

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

    return res

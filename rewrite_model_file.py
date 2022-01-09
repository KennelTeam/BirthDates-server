
with open('Bayes_model.model', 'r') as fi:
    data = fi.read()

with open('Bayes_model_bytes.model', 'wb') as fo:
    print(str.encode(data), file=fo)

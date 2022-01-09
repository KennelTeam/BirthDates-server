
with open('Bayes_model-string.model', 'r') as fi:
    data = fi.read()

data = data[2:-2]
new_data = ""
i = 0
whole = len(data) // 100000
while i < len(data):
    if i % 100000 < 2:
        print(i // 100000, "//", whole)
    if data[i] == '\\' and data[i + 1] == 'x':
        new_data += eval('"\\x' + data[i + 2:i + 4] + '"')
        i += 4
    else:
        new_data += data[i]
        i += 1


b_data = bytes(new_data, 'utf-8')

with open('Bayes_model.model', 'wb') as fo:
    fo.write(b_data)

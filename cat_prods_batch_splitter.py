import json

with open('BirthDates-server/gifts_&_categories_prices.json') as f:
    inp = json.loads(f.read())

data = [[key, value] for key, value in inp.items()]

print('Total is', len(data))

items_per_batch = 8000
batches = []
adding = True
while adding:
    if (len(batches)+1)*items_per_batch >= len(data):
        batches.append(data[len(batches)*items_per_batch:])
        adding = False
    else:
        batches.append(
            data[len(batches)*items_per_batch:(len(batches)+1)*items_per_batch])

for i, batch in enumerate(batches):
    batch_dict = {}
    for key, value in batch:
        batch_dict[key] = value

    with open(f'batches/categs-{i}.json', 'w') as f:
        f.write(json.dumps(batch_dict))

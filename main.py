from user_questions import user_choose
from clustering_graph_db_functions import *
from db_functions import get_product

initial = get_root_clusters()
prev = 0
current = initial
print([a[0] for a in current])

while len(current) > 0:
    index = user_choose([x[1] for x in current])
    id = current[index][0]
    prev = id
    print(id)
    current = get_child_clusters(id)
    print([a[0] for a in current])

print(get_cluster_keywords(prev))

products = get_cluster_products(prev)

print(products)

for product in products:
    print(get_product(product))

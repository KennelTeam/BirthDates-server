import concurrent.futures
import requests
import time
from tqdm import tqdm
import json

CONNECTIONS = 100
TIMEOUT = 5

with open('headers.json') as hf:
    headers = json.loads(hf.read())

def load_url(url, timeout):
    ans = requests.get(url, headers=headers, timeout=timeout)
    print(ans.status_code)
    return ans.text

def scrap_batch(urls: list):
    res = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=CONNECTIONS) as executor:
        future_to_url = (executor.submit(load_url, url, TIMEOUT)
                            for url in urls)
        time1 = time.time()
        for future in concurrent.futures.as_completed(future_to_url):
            resp = future.result()
            if resp:
                res.append(resp)
                with open('pages/plast.html', 'w') as fo:
                    fo.write(resp)

        time2 = time.time()
    print(f'Took {time2-time1:.2f} s')
    return res

with open('full-urls.txt') as f:
    urls = f.readlines()

with open('ul2.txt', 'w') as ulf:
    for url in urls[:300]:
        ulf.write("'" + url[:-1] + "'\n")

batch_count = 1000
items_in_batch = len(urls) // batch_count
print(items_in_batch)
for batch_index in tqdm(range(batch_count-1)):
    scrap_batch(urls[batch_index*items_in_batch:(batch_index+1)*items_in_batch])
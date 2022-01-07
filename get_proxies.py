import requests
import json
from bs4 import BeautifulSoup

proxies_html = requests.get(
    'https://free-proxy-list.net/', headers={'User-Agent': 'Mozilla/5.0'})
proxies_soup = BeautifulSoup(proxies_html.text, "lxml")
# print(res.text)
for item in proxies_soup.find_all("textarea"):
    proxies = item.text.split('\n')[3:]

with open('proxies.json', 'w') as f:
    f.write(json.dumps(proxies))

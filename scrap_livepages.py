import json
from lxml import html
from selenium import webdriver
import time
import lxml
from lxml.html.clean import Cleaner
import base64
import bs4
from tqdm import tqdm


def get_page_items(s_gen: str) -> list:
    driver.get(
        "https://www.amazon.com/gcx/Gifts-for-Everyone/gfhz/?scrollState=" + s_gen)
    time.sleep(0.5)

    page_text = driver.page_source

    cleaner = Cleaner()
    cleaner.javascript = True
    cleaner.style = True

    page_cleaned = lxml.html.tostring(cleaner.clean_html(
        lxml.html.fromstring(page_text))).decode()

    with open('pages/later-e.html', 'w') as f:
        f.write(page_cleaned)

    soup = bs4.BeautifulSoup(page_cleaned, 'html.parser')
    scroll_block = soup.find(
        id="data-infinite-scroll").find(attrs={"class": "sc-1koy58b-0 jChBdP"})

    products_indexes = []
    for product_block in scroll_block.children:
        product_block = product_block.findChild().findChild().find('a')
        product_id = product_block['href'].split('/')[2]
        product_price = int(float(product_block.find(
            attrs={'class': 'sc-167fkr-0 XmvAr'}).text.split()[0][1:].replace(',', ''))*100)
        products_indexes.append((product_id, product_price))

    return products_indexes


if __name__ == '__main__':

    with open('headers.json') as hf:
        headers = json.loads(hf.read())

    service_url = 'http://localhost:43873'

    driver_options = webdriver.ChromeOptions()
    driver_options.add_argument('headless')
    driver_options.add_argument('disable-gpu')
    driver = webdriver.Remote(service_url, options=driver_options)

    get_page_items(s_gen=base64.urlsafe_b64encode(
        json.dumps({'itemIndex': 620, 'scrollOffset': 0}).encode()).decode().strip())

    fsave = 'amazon-gifts-ids.txt'
    with open(fsave, 'w') as f:
        f.truncate()

    for page_progress in tqdm(range(101, 200)):  # change to start from 0
        gen = {'itemIndex': page_progress, 'scrollOffset': 0}
        s_gen = base64.urlsafe_b64encode(
            json.dumps(gen).encode()).decode().strip()

        cur_items = get_page_items(s_gen)
        cur_ids = list(zip(*cur_items))[0]
        while cur_ids[-1] == 'B0749N1XBN' and page_progress != 0:
            cur_items = get_page_items(s_gen)
            cur_ids = list(zip(*cur_items))

        with open(fsave, 'a') as f:
            f.write(
                '\n'.join(map(lambda el: el[0]+' '+str(el[1]), cur_items))+'\n')

        if 'B013G6DG28' in cur_ids:
            print(f'Finished on index {page_progress}')
            break

    driver.quit()

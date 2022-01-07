from requests_html import HTMLSession
from urllib3.exceptions import ProxyError
import json
import pyppdf.patch_pyppeteer
from random import ran
url = "https://www.amazon.com/s?i=specialty-aps&bbn=16225007011&rh=n%3A16225007011%2Cn%3A3012292011&ref=nav_em__nav_desktop_sa_intl_external_components_0_2_6_6"
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "referer": "https://www.amazon.com/?ref_=nav_signin&",
    "cookie": "aws-ubid-main=414-1248863-0832855; ubid-main=132-8285642-4018813; aws_lang=en; s_cc=true; at-main=Atza|IwEBINW115IbH0Bjk_iykYr4Sh-C46e1YN-omDQn7vPWOF2W6MjTl1HBsxSGotOwIdqY1MON03LKUsZtTOEeLxPcjELze3JtICmLeeqfjTwx72vELGMhor9e2FKmwUR2IL9UPEeoxh4gScgDJ-d3h5MdwGoD-HjXzimU8b1h2hg1VomXax0qF0C6cWn2GxTgVkdQJgU46Uy7L1FVkWUxAadv5oAS; sess-at-main=\"EdB4ec+bJGgH2Att+dObeFfjBdzhk77BmyiH+F2FLzw=\"; sst-main=Sst1|PQHNW2dfVmNyv8C-5P94PE3uCSC7qVSK7iTfWLw2Qi7rwBgEhCOua61P11BtSa9mAPAx_Rla0nXDuMc2-rIGAsBJl6NxhZlERKGZ4NF432d8Fnnu51_6KV37hpNpMjxV4AfvFtavTgQfLH5l030l1jFtyQhfnEQDGeKlTD2CUe1WJrpRyLZX_m9hWmYRT_P6SveaVhccKX9MO56u-KoUM_6lPJXuXPqOHV5UGxakGj5gS7K__QYX3c3NFb0XBtqt1MyG9G38zNR3M2pk1DjEJDCKLuKNUL06ZIMWFdYTLUf749c; lc-main=en_US; i18n-prefs=USD; session-id-time=2082787201l; session-token=\"D3+cFAHVk6QUDlZwH8so81/x/CIA2xR527ngYHLi/3NL3HMI/EDZwc7LB2u5SVJBuNzYuwh3DFuXgG8HWI+bkwbGPca2ocOv2xEccLlNu1ExTPsFx1fhvW8gKA3agmIWPJ6rPNgySPr+vsqyaNLSil1tlYR6bLHd7kTJtA+jgHwA3u57V8Ce74i5Vi063ZUuqCxy5vg3w7vKyOmgsZVuSw==\"; sp-cdn=\"L5Z9:CA\"; csm-hit=adb:adblk_no&t:1641461292169&tb:098KFM1017542Q06NNZP+s-JGRCYYTWEKTP1MRY66TJ|1641461292169",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "sec-gpc": "1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
}
data = ""

good_proxies = []


def good_proxy(proxy: str):
    if proxy in good_proxies:
        return
    good_proxies.add(proxy)
    print(f'New good proxy: {proxy}')
    with open('good-proxies.json', 'w') as f:
        f.write(json.dumps(good_proxies))


session = HTMLSession()

with open('proxies.json') as f:
    proxies = json.loads(f.read())


proxy_ind = 0
cur_proxy_attempt = 0
max_proxy_attempts = 3


def get(url, change_proxy=False):
    global proxy_ind, cur_proxy_attempt
    if change_proxy:
        proxy_ind += 1
    cur_proxy = proxies[proxy_ind]

    try:
        r = session.get(url, headers=headers, proxies={
                        'http': cur_proxy, 'https': cur_proxy}, timeout=3)
        good_proxy(cur_proxy)
    except Exception as err:
        cur_proxy_attempt += 1
        if cur_proxy_attempt >= max_proxy_attempts:
            print('Bad proxy: ', cur_proxy)
            proxy_ind += 1
            cur_proxy_attempt = 0
            if proxy_ind >= len(proxies):
                print('Out of proxies')
        else:
            print(
                f'Proxy {cur_proxy}, attempt {cur_proxy_attempt} of {max_proxy_attempts} failed')
        return get(url)
    # r.html.render()
    page_html = r.html.html

    with open('last_proxy_req.html', 'w') as f:
        f.write(page_html)

    return page_html

import asyncio
from pprint import pprint
from requests_html import AsyncHTMLSession
from urllib3.exceptions import ProxyError
import json
import pyppdf.patch_pyppeteer
from random import randint
import random
import time

url = "https://www.amazon.com/s?i=specialty-aps&bbn=16225007011&rh=n%3A16225007011%2Cn%3A3012292011&ref=nav_em__nav_desktop_sa_intl_external_components_0_2_6_6"
headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "cache-control": "max-age=0",
    "cookie": "session-id=131-3904953-1807823; aws-ubid-main=414-1248863-0832855; ubid-main=132-8285642-4018813; skin=noskin; aws_lang=en; AMCVS_7742037254C95E840A4C98A6%40AdobeOrg=1; s_campaign=ps%7Cacquisition_RU%7CGoogle%7CACQ-P%7CPS-GO%7CBrand%7CDesktop%7CSU%7CDatabase%7CSolution%7CRU%7CEN%7CSitelink%7C%7Badgroup%7D%7Camazon%20rds%20pricing%7C549003025586%7CDatabase%7Cacq%7Ce%7CRU%7CEMEA; s_cc=true; aws-target-visitor-id=1641380797441-300817; aws-target-data=%7B%22support%22%3A%221%22%7D; aws-mkto-trk=id%3A112-TZM-766%26token%3A_mch-aws.amazon.com-1641380798958-66617; s_fid=235B40E273DC8826-28F502F060B9A138; _rails-root_session=RkxqOTN5SzRYSUlPamgzY0tFK09wK2thck94UUpIV3ZKdVB6WHVIUGhTMTA1WkpXd3ZFenJQRWZHdEp0VzZKdTdJRDB4TUNvWWpoVWJEdGtrcHJxaEJzS1BtT3U3WVE1bE1iK1ZLblc4RE1YcENVQ0R5SFVpWnd5ZWdFY1ZxNTJKL3VMVHJ2cXBiRk1pWGw0N2ZiMUdCcThjcCtjcUNBSHFVSmZpc1pqVWliVmpJRzNnTmNoQlM2SERteUxKa2VPLS0wdGFrTTVNYXlxOEQ2Q1cwVkdlZThnPT0%3D--931f293069b3f7561f43f93fee6ed3e0c6081904; x-main=\"i6ldjv2OCHtjoXYZ3aFLTga??RTiZXSdlA9vpye9eziFGGnQLjuNWYERSshVhU6m\"; at-main=Atza|IwEBINW115IbH0Bjk_iykYr4Sh-C46e1YN-omDQn7vPWOF2W6MjTl1HBsxSGotOwIdqY1MON03LKUsZtTOEeLxPcjELze3JtICmLeeqfjTwx72vELGMhor9e2FKmwUR2IL9UPEeoxh4gScgDJ-d3h5MdwGoD-HjXzimU8b1h2hg1VomXax0qF0C6cWn2GxTgVkdQJgU46Uy7L1FVkWUxAadv5oAS; sess-at-main=\"EdB4ec+bJGgH2Att+dObeFfjBdzhk77BmyiH+F2FLzw=\"; sst-main=Sst1|PQHNW2dfVmNyv8C-5P94PE3uCSC7qVSK7iTfWLw2Qi7rwBgEhCOua61P11BtSa9mAPAx_Rla0nXDuMc2-rIGAsBJl6NxhZlERKGZ4NF432d8Fnnu51_6KV37hpNpMjxV4AfvFtavTgQfLH5l030l1jFtyQhfnEQDGeKlTD2CUe1WJrpRyLZX_m9hWmYRT_P6SveaVhccKX9MO56u-KoUM_6lPJXuXPqOHV5UGxakGj5gS7K__QYX3c3NFb0XBtqt1MyG9G38zNR3M2pk1DjEJDCKLuKNUL06ZIMWFdYTLUf749c; lc-main=en_US; i18n-prefs=USD; sp-cdn=\"L5Z9:RU\"; session-id-time=2082787201l; aws-userInfo-signed=eyJ0eXAiOiJKV1MiLCJrZXlSZWdpb24iOiJ1cy1lYXN0LTEiLCJhbGciOiJFUzM4NCIsImtpZCI6IjUyMTNlNjJlLTc3MjctNGZjYi1hZjhmLTI5OWY4NjIzNWZiZSJ9.eyJzdWIiOiIiLCJzaWduaW5UeXBlIjoiUFVCTElDIiwiaXNzIjoiaHR0cDpcL1wvc2lnbmluLmF3cy5hbWF6b24uY29tXC9zaWduaW4iLCJrZXliYXNlIjoiZTJsQTZoYmZWOWJ5QTExV3FVUklPODBMaHMwbW9FOEZqTGZZTTlqQVwveGM9IiwiYXJuIjoiYXJuOmF3czppYW06Ojk1NzYyNTE5OTQ5NTpyb290IiwidXNlcm5hbWUiOiJuZWJvbGF4In0.OS2s6VnFeAmJyI7bTCLnwN8pPOBjWg0y1FQtSiO_8KTBq97UVK2y6DGpfGV5FcAWd3stwOLq_QEJ410lJCnKcxQXBlqLdVzOhYmJVF0n9egb3GxHxaEdJ4idKrAeaaxo; aws-userInfo=%7B%22arn%22%3A%22arn%3Aaws%3Aiam%3A%3A957625199495%3Aroot%22%2C%22alias%22%3A%22%22%2C%22username%22%3A%22nebolax%22%2C%22keybase%22%3A%22e2lA6hbfV9byA11WqURIO80Lhs0moE8FjLfYM9jA%2Fxc%5Cu003d%22%2C%22issuer%22%3A%22http%3A%2F%2Fsignin.aws.amazon.com%2Fsignin%22%2C%22signinType%22%3A%22PUBLIC%22%7D; regStatus=registered; s_sq=%5B%5BB%5D%5D; AMCV_7742037254C95E840A4C98A6%40AdobeOrg=1585540135%7CMCIDTS%7C19000%7CMCMID%7C02010279803875053243044122474309283600%7CMCAID%7CNONE%7CMCOPTOUT-1641554648s%7CNONE%7CvVersion%7C4.4.0; session-token=\"qMDjeX8PKsfPZC/MdjzGHCKChq2JtUWsHYJUScbK+ngj3GU8wQFQNL793K6eLsGVdW/QkTv3/gCWGrJtREVngkKZTdnwuNFGxsRNZhEQJFkoUdg7bxXGSSEvPRvK+IHzpvH39TXrwH9WOX+Z0wk606jn6K7PpeY0+vGAsG8HNgO7So31dgkdGr4IY5bou1SbvJgInB08Sragy7jRkBnO0A==\"; csm-hit=adb:adblk_no&t:1641548985244&tb:s-EGYG7BKY9M2WHMMAP0KJ|1641548982530",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "none",
    "sec-fetch-user": "?1",
    "sec-gpc": "1",
    "upgrade-insecure-requests": "1",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"
}
data = ""

# good_proxies = []


# def good_proxy(proxy: str):
#     if proxy in good_proxies:
#         return
#     good_proxies.append(proxy)
#     print(f'New good proxy: {proxy}')
#     with open('good-proxies.json', 'w') as f:
#         f.write(json.dumps(good_proxies))


asession = AsyncHTMLSession()

# with open('proxies-alter.json') as f:
#     proxies = json.loads(f.read())

# proxy_weights = []
# for _ in range(len(proxies)):
#     proxy_weights.append(1)

with open('proxies_weights-t.json') as f:
    inp_w_prox = json.loads(f.read())

(proxies, proxy_weights) = zip(*inp_w_prox.items())


proxy_ind = 0
cur_proxy_attempt = 0
max_proxy_attempts = 3
use_proxy = False
dl, dr = 0, 5

use_proxy = ''

# Returns proxy id in the list


async def get(url, change_proxy=False):
    # await asyncio.sleep(randint(dl, dr))
    global proxy_ind, cur_proxy_attempt, use_proxy
    if change_proxy:
        global use_proxy
        use_proxy = True
        proxy_ind += 1

    # cur_proxy = use_proxy
    cur_proxy_ind = random.choices(
        list(range(len(proxies))), map(lambda x: 1/x, proxy_weights))[0]
    cur_proxy = proxies[cur_proxy_ind]
    req_proxies = {'http': cur_proxy,
                   'https': cur_proxy}
    try:
        r = await asession.get(url, headers=headers, timeout=3, proxies=req_proxies)
        # if use_proxy:
        #     good_proxy(cur_proxy)
    except Exception as err:
        proxy_weights[cur_proxy_ind] += 1
        # cur_proxy_attempt += 1
        # if cur_proxy_attempt >= max_proxy_attempts:
        # print('Bad proxy: ', cur_proxy)
        # if cur_proxy == use_proxy:
        #     proxy_ind += 1
        # if proxy_ind >= len(proxies):
        #     proxy_ind = 0
        # use_proxy = proxies[proxy_ind]
        # cur_proxy_attempt = 0
        # else:
        #     print(
        #         f'Proxy {cur_proxy}, attempt {cur_proxy_attempt} of {max_proxy_attempts} failed')
        return await get(url)
    # r.html.render()
    page_html = r.html.html

    with open('last_proxy_req.html', 'w') as f:
        f.write(page_html)

    with open('proxies_weights-t.json', 'w') as f:
        f.write(json.dumps(dict(zip(proxies, proxy_weights))))

    return page_html

from tqdm import tqdm
import json
import bs4
import requests
import grequests

hacker_headers = {"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", "accept-encoding": "gzip, deflate, br", "accept-language": "en-US,en;q=0.9", "cache-control": "no-cache", "cookie": "session-id=131-3904953-1807823; aws-ubid-main=414-1248863-0832855; regStatus=registered; aws-userInfo=%7B%22arn%22%3A%22arn%3Aaws%3Aiam%3A%3A957625199495%3Aroot%22%2C%22alias%22%3A%22%22%2C%22username%22%3A%22nebolax%22%2C%22keybase%22%3A%22%22%2C%22issuer%22%3A%22http%3A%2F%2Fsignin.aws.amazon.com%2Fsignin%22%2C%22signinType%22%3A%22PUBLIC%22%7D; ubid-main=132-8285642-4018813; sp-cdn=\"L5Z9:RU\"; skin=noskin; aws_lang=en; AMCVS_7742037254C95E840A4C98A6%40AdobeOrg=1; s_campaign=ps%7Cacquisition_RU%7CGoogle%7CACQ-P%7CPS-GO%7CBrand%7CDesktop%7CSU%7CDatabase%7CSolution%7CRU%7CEN%7CSitelink%7C%7Badgroup%7D%7Camazon%20rds%20pricing%7C549003025586%7CDatabase%7Cacq%7Ce%7CRU%7CEMEA; s_cc=true; aws-target-visitor-id=1641380797441-300817; aws-target-data=%7B%22support%22%3A%221%22%7D; aws-mkto-trk=id%3A112-TZM-766%26token%3A_mch-aws.amazon.com-1641380798958-66617; s_fid=235B40E273DC8826-28F502F060B9A138; x-main=\"g82jX7ojavQlCsImEoACEoeB?fQTnl3wNeJ2R3mLF51nsLlEw2CPf1379rdYhWXf\"; at-main=Atza|IwEBIFgzV-emFIKRzGN80wHqHO7S4ibawbJdz_uTAlXmOXTWdab-0PgbvV0P_ycosmrTu_CQXTVXoQWrhmLG1fS4dCD2PKZMugSYCZbMI4cPSvaMvzJGoqtohWvpEN-yBuBoIsWXbrrAV_f6TNM7dFtWz1zQWTvebHUUilZHeN1OvcJoEJsWvEVACi8Ddz9GbE_fHFILdrRetVoS7Jtvwrd_4upRF43Qm7Y3-xMGgTG6Ax2dDh0e_kqYgwNFjxTgSHQlWoc; sess-at-main=\"ic/IFGVDz719Q71xoVQno15ehb5wylb3y+GHqj5g0p0=\"; sst-main=Sst1|PQFAX4t1lKX9sccwxns0ClyqCce3m5yV9aYuwf9SyCTOSeSo5JP-8OBoTu2VmKRdw26jRd7FRLvJMlsWenpxqFzKxHqtn5P6DDcN9RIFmfJWlUjz4WLOP8O75zJC9_ouuDLOJkM_kq0dhd5klI5ZmUp9XnFP7NHAHGkyiFI4Zs8iWjXrC_Oe6vMffj0l4URF7G0YQlKgYN1tDoaAkYgAFchy-_Y7OuoJTLv-BNqwkCuZvXwZFWrxObH6nUjZjchaM2R1eIenIywn9sZUqMweVqY82vd6BhPzRlgyjZ9ugJg7_Pg; s_sq=%5B%5BB%5D%5D; _rails-root_session=RkxqOTN5SzRYSUlPamgzY0tFK09wK2thck94UUpIV3ZKdVB6WHVIUGhTMTA1WkpXd3ZFenJQRWZHdEp0VzZKdTdJRDB4TUNvWWpoVWJEdGtrcHJxaEJzS1BtT3U3WVE1bE1iK1ZLblc4RE1YcENVQ0R5SFVpWnd5ZWdFY1ZxNTJKL3VMVHJ2cXBiRk1pWGw0N2ZiMUdCcThjcCtjcUNBSHFVSmZpc1pqVWliVmpJRzNnTmNoQlM2SERteUxKa2VPLS0wdGFrTTVNYXlxOEQ2Q1cwVkdlZThnPT0%3D--931f293069b3f7561f43f93fee6ed3e0c6081904; lc-main=en_US; i18n-prefs=USD; AMCV_7742037254C95E840A4C98A6%40AdobeOrg=1585540135%7CMCIDTS%7C18998%7CMCMID%7C02010279803875053243044122474309283600%7CMCAID%7CNONE%7CMCOPTOUT-1641398043s%7CNONE%7CvVersion%7C4.4.0; session-id-time=2082787201l; session-token=\"BFnZuJMrGJrn91jLlZXzp/gLnRrjT95mbKDafWPy1FRPa9MeAyQvz94jq4pt2M9N3luyCcf8mqBGNNvJ+LQGXJNk8I2sCttqCWarLRhj4GkmmA/93YFoJreY2mOlSQxVrgOlOvTCna43F1ivCdnF8O6/dx6HQJBKfvI/UkwALZNJGvISU3E83vfv3EfSsLhPELgOZli0gClWEXbcaQAB0A==\"; csm-hit=adb:adblk_no&t:1641393926758&tb:s-P1NYVX74VF8JWMY7PFN3|1641393924982",
                  "pragma": "no-cache", "referer": "https://www.amazon.com/b?node=16225007011&pf_rd_r=TRP79HB5XNCCCJAGDN7D&pf_rd_p=ca7cc8fd-a737-48a1-91c5-4219cfa25ccb&pd_rd_r=8cbc0715-8c02-46b3-8517-b37968cb57a1&pd_rd_w=Ixc1v&pd_rd_wg=7ePyI&ref_=pd_gw_unk", "sec-fetch-dest": "document", "sec-fetch-mode": "navigate", "sec-fetch-site": "same-origin", "sec-fetch-user": "?1", "sec-gpc": "1", "upgrade-insecure-requests": "1", "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"}

page = requests.get("https://www.amazon.com/b?node=17938598011&pf_rd_r=27JNFC868P41ZH3QF3HM&pf_rd_p=e5b0c85f-569c-4c90-a58f-0c0a260e45a0&pd_rd_r=f44cbaf9-8531-44cd-9094-478db061380f&pd_rd_w=fHRjO&pd_rd_wg=gS6Jy&ref_=pd_gw_unk", headers=hacker_headers)

success_parse = []


def parse_subcategories(href):
    global success_parse
    list_subcats = []
    page = grequests.get(href, headers=hacker_headers)
    
    bs = bs4.BeautifulSoup(page.text)
    try:
        subcategories = bs.find_all("div", id="filter-n")
        for subcat_1 in subcategories:
            bs = bs4.BeautifulSoup(str(subcat_1))
            subcat_list = bs.find_all(
                "a", class_="a-link-normal sf-filter-floatbox aok-inline-block aok-align-bottom s-no-hover s-no-underline")
            print(">> subcats:", len(subcat_list))
            counter = 1
            for subcat in subcat_list:
                name = subcat.text.strip()
                if name == "All":
                    continue
                sub_link = "https://www.amazon.com" + \
                    subcat["href"].split("&dc&qid")[0]
                print("sub", counter, ":", name, sub_link)
                subsubcats = parse_subcategories(sub_link)
                list_subcats.append({"name": name,
                                     "link": sub_link,
                                     "subcategories": subsubcats})
                success_parse.append(href)
        print("<<")
        return list_subcats
    except IndexError:
        # print("INDEX ERROR!!! FUCK AMAZON!!!")
        # print(page.text)
        pass


# print(page.status_code)
html = page.text
soup = bs4.BeautifulSoup(html, "html.parser")

left_column = soup.find_all(
    "div", class_="a-column a-span12 apb-browse-left-nav apb-browse-col-pad-right a-span-last")[0]

bs = bs4.BeautifulSoup(str(left_column))
lists = bs.find_all(
    "ul", class_="a-unordered-list a-nostyle a-vertical a-spacing-medium")
categories = lists[1]

bs = bs4.BeautifulSoup(str(categories))
categories_list = bs.find_all("li", class_="a-spacing-micro")
# print("k categories =", len(categories_list))

categories_json = []
for cat in tqdm(categories_list):
    try:
        bs = bs4.BeautifulSoup(str(cat))
        name = bs.find_all("span", dir="auto")[1].text
        link = bs.find_all("a", class_="a-color-base a-link-normal")[0]["href"]
        link = "https://www.amazon.com" + link.split("&bbn")[0]
        print("MAIN CATEGORY!", name, link)
        # print(parse_subcategories(link))
        subcats = parse_subcategories(link)
        if subcats == None:
            subcats = []
        print()
        categories_json.append(
            {"name": name, "link": link, "subcategories": subcats})
    except Exception:
        pass

print(len(success_parse))

with open('category_tree.json', 'w') as f:
    f.write(json.dumps(categories_json, ensure_ascii=False, indent=4))

# print(parse_subcategories("https://www.amazon.com/s?i=garden&srs=17938598011&bbn=1063498&rh=n%3A1055398%2Cn%3A3206325011"))
# print(parse_subcategories("https://www.amazon.com/s?i=garden&srs=17938598011&bbn=1063498&rh=n%3A1055398%2Cn%3A3206325011&dc&qid=1641408178&rnid=1063498&ref=sr_nr_n_1"))

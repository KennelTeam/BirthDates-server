from requests.models import Response
from requests_html import AsyncHTMLSession

# Headers to pass in requests so host thinks we are calling from browser
# cookies may expire so this parameters has to be refreshed some times
# Found out that sometimes in response headers there is parameter "set-cookie"
# which can be useful but I didn't implement it
headers = {"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", "accept-encoding": "gzip, deflate, br", "accept-language": "en-US,en;q=0.9", "sec-fetch-dest": "document",
           "sec-fetch-mode": "navigate", "sec-fetch-site": "none", "sec-fetch-user": "?1", "sec-gpc": "1", "upgrade-insecure-requests": "1", "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36", "cookie": "session-id=133-0709990-4189060; Domain=.amazon.com; Expires=Mon, 09-Jan-2023 09:42:36 GMT; Path=/; Secure, session-id-time=2082787201l; Domain=.amazon.com; Expires=Mon, 09-Jan-2023 09:42:36 GMT; Path=/; Secure, i18n-prefs=USD; Domain=.amazon.com; Expires=Mon, 09-Jan-2023 09:42:36 GMT; Path=/"}

# Using AsyncHTMLSession instead of HTMLSession to do job faster
asession = AsyncHTMLSession()


# Method to get by url
# If captcha parameter is passed, trying to solve url
# I failed to implement with fully asession async methods
# So using mix of AsyncHTMLSession and pure asyncio
# this may lead to some problems with developing in the future :)
async def get(url, captcha=None):
    resp: Response
    if captcha is None:
        resp = await asession.get(url, headers=headers)
    else:
        resp = await asession.get('https: // www.amazon.com/errors/validateCaptcha?', params=captcha, headers=headers)

    # Saving last response
    # So if we have any fail later in the program we can see the page where it failed
    with open('last_response.html', 'w') as f:
        f.write(resp.text)

    return resp.text, resp.status_code

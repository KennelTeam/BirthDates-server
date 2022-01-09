import lxml
from lxml.html.clean import Cleaner

page_path = 'last_proxy_req.html'

cleaner = Cleaner()
cleaner.javascript = True

with open('pages/later_wojs.html', 'wb') as f:
    f.write(lxml.html.tostring(cleaner.clean_html(
        lxml.html.parse(page_path))))

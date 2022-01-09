import json

raw_headers = '''accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
accept-encoding: gzip, deflate, br
accept-language: en-US,en;q=0.9
sec-fetch-dest: document
sec-fetch-mode: navigate
sec-fetch-site: none
sec-fetch-user: ?1
sec-gpc: 1
upgrade-insecure-requests: 1
user-agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36'''

dict_headers = dict()
for line in raw_headers.split('\n'):
    sp = line.split(':')
    dict_headers[sp[0]] = ':'.join(sp[1:])[1:]

with open('headers.json', 'w') as f:
    f.write(json.dumps(dict_headers))

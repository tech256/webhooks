#!/usr/bin/env python3

import requests
from lxml import html

try:
    from urllib.parse import urljoin
    from urllib.parse import urlencode
    import urllib.request as urlrequest
except ImportError:
    from urlparse import urljoin
    from urllib import urlencode
    import urllib2 as urlrequest
import json

import yaml
config = yaml.safe_load(open("config.yml"))

r = requests.get('http://underdogpickem.com/login/')
login = dict(username=config["ud_user"],
             password=config["ud_pass"],
             next='/group/default/' + config["ud_group"],
             csrfmiddlewaretoken=r.cookies['csrftoken'])
cookies = dict(csrftoken=r.cookies['csrftoken'])
resp = requests.post('http://underdogpickem.com/login/', data=login, cookies=cookies)

scores = []
hh = html.fromstring(resp.content)
table = hh.xpath('//*[@id="standings_table"]')
trs = table[0].getchildren()
for tr in trs:
    tds = tr.getchildren()
    if len(tds) < 3:
        continue
    if tds[0].text.strip() == 'Rank':
        continue
    scores.append((tds[0].text.strip(), tds[1].text.strip(), tds[2].text.strip()))

scores_clean = []
rank = 0
for score in scores:
    if score[0]:
        # if there's a value in the first column, that's the rank.
        # Otherwise, reuse the last one we've seen
        rank = int(score[0])

    scores_clean.append([rank, score[1], int(score[2])])

out = []
# this will use alphabetical order as the tiebreak, which is good enough
for rank, user_name, score in sorted(scores_clean):
    out.append('({rank}) {user_name}: {score}'.format(
        rank=rank, user_name=user_name, score=score))

payload_json = {"text": "\n*Current Pick'em Standings*\n" + "\n".join(out)}

if not config["dryrun"]:
    data = urlencode({"payload": payload_json})
    req = urlrequest.Request('https://hooks.slack.com/services/' + config["slack_url"])
    response = urlrequest.build_opener(urlrequest.HTTPHandler()).open(req, data.encode('utf-8')).read()
    print(response.decode('utf-8'))
else:
    print(payload_json)

#!/usr/bin/env python3

import json
import sys

import requests

import yaml

try:
    from urllib.parse import urljoin
    from urllib.parse import urlencode
    import urllib.request as urlrequest
except ImportError:
    from urlparse import urljoin
    from urllib import urlencode
    import urllib2 as urlrequest

if len(sys.argv) == 2:
    config_file = sys.argv[1]
else:
    config_file = 'config.yml'

config = yaml.safe_load(open(config_file))

group_id = config['advent_group_id']
session = config['advent_session']

url = 'https://adventofcode.com/2018/leaderboard/private/view/{}.json'
url = url.format(group_id.split('-')[0])
cookies = {'session': session}

r = requests.get(url, cookies=cookies)
content = json.loads(r.content)

members = content['members'].values()
try:
    # .casefold() is the preferred method for case-insensitive comparisons,
    # per unicode
    members = sorted(members, key=lambda entry: (
        # sort order:
        # local score (descending)
        # stars (descending)
        # display name (ascending)
        -entry['local_score'], -entry['stars'], entry['name'].casefold(),
    ))
except AttributeError:
    # on Py <3.3. Lame.
    members = sorted(members, key=lambda entry: (
        # sort order:
        # local score (descending)
        # stars (descending)
        # display name (ascending)
        -entry['local_score'], -entry['stars'], entry['name'].lower(),
    ))
table = []
table.append('{:<30}{:<15}{:<15}'.format('Member', 'Stars', 'Score'))
for member in members:
    table.append('{:<30}{:<15}{:<15}'.format(
        member['name'], member['stars'], member['local_score']))

text = """
*2018 Advent of Code Standings for group: {}*
```
{}
```
""".format(group_id, '\n'.join(table))

if config['dryrun']:
    print(text)
else:
    data = urlencode({'payload': {'text': text}})
    req = urlrequest.Request(
            'https://hooks.slack.com/services/' + config['slack_url'])
    response = urlrequest.build_opener(urlrequest.HTTPHandler()).open(
            req, data.encode('utf-8')).read()
    print(response.decode('utf-8'))

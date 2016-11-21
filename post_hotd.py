import slack_functions as sf
import random
import requests
import json
import time
import datetime

day=datetime.datetime.today().weekday()
if day in [0,1,2,3,4]:
    WEBHOOK_URL = 'https://hooks.slack.com/services/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'
    WIKI_SUBMISSIONS_FILE = '/home/pricecomstock/slash-selfie/wiki_submissions.json'

    with open(WIKI_SUBMISSIONS_FILE,'r') as ws_file:
        ws_json = json.load(ws_file)

    ws_json['meta'].setdefault('last_user','')
    ws_json['meta'].setdefault('second_last_user','')
    last_user = ws_json['meta']['last_user']
    second_last_user = ws_json['meta']['second_last_user']

    available_users = ws_json['submissions'].keys()

    if len(available_users) > 0:
        today_user = random.choice(available_users)
        today = time.strftime("%m-%d-%Y")
        while (today_user == last_user or today_user == second_last_user) and len(available_users) > 2:
            today_user = random.choice(available_users)

        ws_json['meta']['second_last_user'] = last_user
        ws_json['meta']['last_user'] = today_user
        hotd=random.choice(ws_json['submissions'][today_user]['subs'])
        del ws_json['submissions'][today_user]['subs'][ws_json['submissions'][today_user]['subs'].index(hotd)]
        print "DELETING " + str(hotd)

        ws_json['meta']['post_count'] += 1
        ws_json['chosen'].setdefault(today_user,{'name':sf.findname(today_user),'subs':[]})
        if len(ws_json['submissions'][today_user]['subs']) == 0:
            del ws_json['submissions'][today_user]
        hotd.update({'date':today})
        ws_json['chosen'][today_user]['subs'].append(hotd)

        with open(WIKI_SUBMISSIONS_FILE,'w') as ws_file:
            ws_file.write(json.dumps(ws_json,sort_keys=True, indent=4))

        payload =  {
          "response_type": "in_channel",
          "attachments": [
            {
              "fallback": hotd['title'],
              "color": "#AA6622",
              "title": hotd['title'],
              "title_link": hotd['link'],
              "fields": [
                {
                  "title": hotd['type'],
                  "value":  hotd['pitch'] + '\nSubmitted by ' + sf.findname(today_user)
                }
              ]
            }
          ]
        }

    else:
        payload = 'No submissions in the pool.'

    requests.post(WEBHOOK_URL,data=json.dumps(payload))
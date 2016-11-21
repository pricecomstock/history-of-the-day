import slack_functions as sl
from flask import Flask, request, jsonify, json
import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG,format=' %(asctime)s - %(levelname)s - %(message)s')
sb_log=logging.getLogger('slackbots')

hist_log=sb_log.getChild('hist')
hist_log.setLevel(logging.DEBUG)

@app.route('/hotd', methods=['POST'])
def submit_hotd():
    full_command = '/hotd ' + request.form['text']
    hist_log.debug('request received: ' + request.form['text'])
    WIKI_SUBMISSIONS_FILE = '/home/pricecomstock/slash-selfie/wiki_submissions.json'
    response_type = 'ephemeral'
    uid = request.form['user_id']
    uname = sl.findname(uid)
    hist_log.debug('from user ' + uname + ':' + uid)

    # These are currently not checked due to SOMEONE not being able to get the syntax right
    valid_types = ['unspecified','person','place','event','war','battle','policy']
    with open(WIKI_SUBMISSIONS_FILE,'r') as ws_file:
        ws_json = json.load(ws_file)

    # Set some stuff up in case the file was new and dict is empty
    ws_json.setdefault('submissions',{})
    ws_json.setdefault('chosen',{})
    ws_json.setdefault('meta',{'sub_count':0,'post_count':0})

    #Pipe delimited args
    args=[]
    args_line = request.form['text']
    for x in args_line.split('|'):
        args.append(x.strip())

    try:
        command=args[0].lower().strip()
    except:
        command = 'help'

    response = 'Invalid command. try `/hotd help`'

    if command == 'help' or command == '':
        hist_log.debug('Sending help.')
        response = "Usage: /hotd command | argument | [optional argument] | ... \n/hotd *submit* | title | type | link | [pitch (why is this interesting?)]\n/hotd *wiki* | link | [pitch]\n/hotd *list* _or_ *listpub* _or_ *listdetail* | [user]\n/hotd *hist* _or_ *histpub* _or_ *histdetail* | [user]\n/hotd *remove* | id\n\n*Valid types:* " + str(valid_types)
    elif command == 'submit' or command == 'add':
        hist_log.debug('Submitting!')
        try:
            ws_json['submissions'].setdefault(uid,{'name':uname,'subs':[]}) #Add user to the submission file if they aren't in there
            title = args[1]
            ptype = args[2].title()
            link = args[3]
            pitch = ''
            if len(args) > 4:
                pitch = args[4]
            sub_id = ws_json['meta']['sub_count'] + 1 #this is a separate step in case of failure
            # if ptype.lower() not in valid_types:
            #     raise ValueError('invalid type!')
            item={'title':title,'type':ptype,'link':link,'pitch':pitch,'id':sub_id}
            ws_json['submissions'][uid]['subs'].append(item)
            ws_json['meta']['sub_count'] += 1
            hist_log.debug("Submission: " + str(item))

            with open(WIKI_SUBMISSIONS_FILE,'w') as ws_file:
                ws_file.write(json.dumps(ws_json,sort_keys=True, indent=4))
            response = sl.bold(item['title']) + ' ' + 'successfully submitted by ' + sl.bold(uname) + '!\n*Type*: ' + item['type'] + '\n*Link*: ' + item['link'] + '\n*Pitch*: ' + item['pitch'] + '\n*Submission ID*: ' + str(item['id'])
        except ValueError:
            response = 'Type not valid. See /hotd help for a list of valid types.\n' + full_command
        except:
            hist_log.error('Format wrong. Sending help.')
            response_type = 'in_channel'
            response="Something is wrong with your format. Try `/hotd help`.\n" + full_command

    elif command == 'wiki':
        hist_log.debug('Auto adding from wiki!')
        try:
            ws_json['submissions'].setdefault(uid,{'name':uname,'subs':[]}) #Add user to the submission file if they aren't in there
            link = args[1]
            ptype = 'Unspecified'
            title = link.split('/wiki/')[1].replace('_',' ').title()
            pitch = ''
            if len(args) > 2:
                pitch = args[2]
            sub_id = ws_json['meta']['sub_count'] + 1 #this is a separate step in case of failure
            item={'title':title,'type':ptype,'link':link,'pitch':pitch,'id':sub_id}
            ws_json['submissions'][uid]['subs'].append(item)
            ws_json['meta']['sub_count'] += 1
            hist_log.debug("Submission: " + str(item))

            with open(WIKI_SUBMISSIONS_FILE,'w') as ws_file:
                ws_file.write(json.dumps(ws_json,sort_keys=True, indent=4))
            response = sl.bold(item['title']) + ' ' + 'successfully submitted by ' + sl.bold(uname) + '!\n*Type*: ' + item['type'] + '\n*Link*: ' + item['link'] + '\n*Pitch*: ' + item['pitch'] + '\n*Submission ID*: ' + str(item['id'])
        except ValueError:
            response = 'Type not valid. See /hotd help for a list of valid types.\n' + full_command
        except:
            hist_log.error('Format wrong. Sending help.')
            response="Something is wrong with your format. Try `/hotd help`.\n" + full_command

    elif command in ['list','listpub','hist','histpub','listdetail','listpubdetail','histdetail','histpubdetail']:
        response=''

        if 'detail' in command:
            detail = True
        else:
            detail = False

        if 'hist' in command:
            timeframe = 'past'
            user_entries_list=ws_json['chosen']
        else:
            timeframe = 'future'
            user_entries_list=ws_json['submissions']

        if len(args) > 1:
            l_user=sl.finduid(args[1],failrandom=False)
            if l_user != None:
                try:
                    user_entries_list={l_user:user_entries_list[l_user]} #make a new dictionary containing only that users list
                except:
                    response = 'That user has no entries in selected time period.\n'

        response += 'Submissions:\n'
        for x in user_entries_list:
            response += sl.bold(user_entries_list[x]['name']) + '\n'
            for y in user_entries_list[x]['subs']:
                entry = ''
                if timeframe == 'past':
                    entry += y['date'] + ': '
                entry = '`' + str(y['id']).rjust(3) + '` ' + sl.italic(y['type']) + ' - ' + sl.bold(y['title'])
                if detail:
                    entry += ' : ' + y['pitch']
                entry += '\n'
                response += entry

        if 'pub' in command:
            response_type = 'in_channel'

    elif command == 'remove':
        target=int(args[1])
        found=False
        hist_log.debug('Attempting to remove item with id ' + str(target))
        try:
            for x in ws_json['submissions'][uid]['subs']:
                hist_log.debug('Checking ' + str(x))
                if x['id'] == target:
                    del ws_json['submissions'][uid]['subs'][ws_json['submissions'][uid]['subs'].index(x)]
                    found = True
                    hist_log.debug('item with id ' + str(target) + ' removed')
            if found:
                response='Removed!'
                with open(WIKI_SUBMISSIONS_FILE,'w') as ws_file:
                    ws_file.write(json.dumps(ws_json,sort_keys=True, indent=4))

            else:
                response='That ID either does not exist or is not your submission.\n' + full_command
        except:
            response = 'That did not go correctly. Try `/hotd help`'

    return jsonify({'response_type':response_type,'text':response})
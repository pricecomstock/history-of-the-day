import json
import random

def bold(txt):
    return '*' + str(txt) + '*'
def italic(txt):
    return '_' + str(txt) + '_'
def code(txt):
    return '`' + str(txt) + '`'

def finduid(name,failrandom=True):
    with open('/home/pricecomstock/slash-selfie/markov/niceuserlist.json') as user_list_json:
        userlist=json.load(user_list_json)
        for x in userlist:
            if name.lower() in userlist[x]['names']:
                print 'found ' + name + ':' + x
                return x
    if failrandom:
        return random.choice(userlist.keys())
    else:
        return None

def findname(uid,fullname=False):
    with open('/home/pricecomstock/slash-selfie/markov/niceuserlist.json') as user_list_json:
        userlist=json.load(user_list_json)
    if fullname:
        return userlist[uid]['fullname']
    else:
        return userlist[uid]['names'][0]

def string_search_list(chats, term):
    matches=[]
    for x in chats:
        if term.lower() in x.lower():
            matches.append(x)
    if len(matches) > 0:
        return random.choice(matches)
    else:
        return random.choice(chats)
    pass

def get_random_chat(userid=None,random_by_user=True,search_term=None):
    with open('/home/pricecomstock/slash-selfie/markov/newfullhistory.json','r') as history_json:
        history = json.load(history_json)
        if userid == None or userid=='':
            if random_by_user:
                if search_term == None:
                    chat=random.choice(history[random.choice(history.keys())])
                else:
                    chat=string_search_list(history[random.choice(history.keys())], search_term)
            else:
                chat = 'THIS METHOD OF CHAT SELECTION NOT YET IMPLEMENTED'
        else:
            if search_term == None:
                chat=random.choice(history[userid])
            else:
                chat=string_search_list(history[userid], search_term)
    return chat
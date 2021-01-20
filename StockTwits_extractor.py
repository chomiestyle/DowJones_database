import time
from http_request_randomizer.requests.proxy.requestProxy import RequestProxy

import json
import requests
import pandas as pd
import random


def get_twits(ticker):
    url = "https://api.stocktwits.com/api/2/streams/symbol/{0}.json".format(ticker)
    response = requests.get(url).json()
    return response



def convert_proxies(filename):
    f = open(filename, "r")
    proxies_array=[]
    for line in f.readlines():
        line=line.split('\n')
        proxies_array.append(line[0])
    f.close()
    return proxies_array

def generate_proxies():
    filename= 'http_proxies.txt'
    https_ip_addresses = convert_proxies(filename)
    return https_ip_addresses[random.randint(0,len(https_ip_addresses))]


def extractor(old_messages_id,SYMBOL):
    #print('entrego los id')
    if len(old_messages_id) == 0:
        max_message_id= 0
        min_message_id=None
        print('No hay twits previos')
    else:
        max_message_id = max(old_messages_id)
        min_message_id=min(old_messages_id)
    # req_proxy = RequestProxy()
    last_message_id=None
    #since_begin=False
    #last_message_id=None
    access_token = ['', 'access_token=32a3552d31b92be5d2a3d282ca3a864f96e95818&',
                    'access_token=44ae93a5279092f7804a0ee04753252cbf2ddfee&',
                    'access_token=990183ef04060336a46a80aa287f774a9d604f9c&']

    token = 0
    stocktwit_url = "https://api.stocktwits.com/api/2/streams/symbol/" + SYMBOL + ".json?" + access_token[token]
    if last_message_id is not None:
        stocktwit_url += "max=" + str(last_message_id)

    api_hits = 0

    extracted_messages=pd.DataFrame(columns=['user','datetime','message','message_id','sentiment'])
    user,datetime,messages,messages_id,sentiments=[],[],[],[],[]
    Time_ex = None
    while True:
        # response = req_proxy.generate_proxied_request(stocktwit_url)
        try:
            #response = req_proxy.generate_proxied_request(stocktwit_url)
            response = requests.get(stocktwit_url )
        except Exception as ex:
            print(ex)
            response = None
        print(response)
        if response is not None:
            print('La respuesta es not none')

            if response.status_code == 429:
                # Break loop
                #break
                print("###############")
                time_out=int(response.headers['X-RateLimit-Reset']) - int(time.time())
                print("REQUEST IP RATE LIMITED FOR {} seconds !!!".format(time_out))
                Time_ex=time_out
                break
                #time.sleep(time_out)

            if not response.status_code == 200:
                if last_message_id==None:
                    stocktwit_url="https://api.stocktwits.com/api/2/streams/symbol/" + SYMBOL + ".json?" + access_token[token]

                else:
                    stocktwit_url = "https://api.stocktwits.com/api/2/streams/symbol/" + SYMBOL + ".json?" + \
                                access_token[token] + "max=" + str(last_message_id)
                token = (token + 1) % (len(access_token))
                continue

            api_hits += 1
            response = json.loads(response.text)
            last_message_id = response['cursor']['max']
            if last_message_id<=max_message_id:
                print('salio porque se acabaron los nuevos')
                break

            # WRITE DATA TO CSV FILE
            for message in response['messages']:
                if int(message['id']) not in old_messages_id:
                    temp=message['entities']['sentiment']
                    if temp is not None and temp['basic']:
                        sentiment = temp['basic']
                        print(sentiment)
                    else:
                        sentiment=None
                    messages.append(message['body'])
                    datetime.append(message['created_at'])
                    user.append(message['user']['id'])
                    messages_id.append(message['id'])
                    sentiments.append(sentiment)
            print("API HITS TILL NOW = {}".format(api_hits))

            # NO MORE MESSAGES
            if not response['messages']:
                #since_begin=True
                #stocktwit_url = "https://api.stocktwits.com/api/2/streams/symbol/" + SYMBOL + ".json?" + access_token[token]
                #last_message_id=None
                print('completo hasta el principio')
                #continue
                break
        elif response==None:
            print('la respuesta es None')

        # ADD MAX ARGUMENT TO GET OLDER MESSAGES
        stocktwit_url = "https://api.stocktwits.com/api/2/streams/symbol/" + SYMBOL + ".json?" + access_token[token] + "max=" + str(last_message_id)
        token = (token + 1) % (len(access_token))
    extracted_messages['user']=user
    extracted_messages['message']=messages
    extracted_messages['message_id']=messages_id
    extracted_messages['datetime']=datetime
    extracted_messages['sentiment']=sentiments

    return extracted_messages,Time_ex


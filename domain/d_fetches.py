import pandas as pd
import requests
from requests.structures import CaseInsensitiveDict
import time
import configparser
import sys
import os

def d_fetches(domain, lang, API_KEY, data=[""]):
    a = 0
    data_list = []
    url = "https://www.babbar.tech/api/domain/fetches/list?api_token=" + API_KEY
    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    while True:
        data = {
            "domain": domain,
            "status": -1,
            "lang": lang,
            "offset": a,
            "n": 499
        }
        resp = requests.post(url, headers=headers, json=data)
        if resp.status_code != 200:
            print("STATUS CODE INVALID")
            print(resp.status_code)
            break
        else:
            try:
                aList = resp.json()
                if isinstance(aList, list):
                    if not aList:  
                        print("No more data.")
                        break
                    remain = int(resp.headers.get('X-RateLimit-Remaining'))
                    if remain == 0:
                        time.sleep(60)
                    for entry in aList:
                        updated_entry = {
                            'domain': domain,
                            'url': entry['url'],
                            'lang': entry['lang'],
                            'http': entry['http']
                        }
                        data_list.append(updated_entry)
                    a += 1
                else:
                    print("Invalid JSON response:", aList)
                    break
            except ValueError:
                print("Invalid JSON response")
                break
    return data_list

def d_fetches_to_csv(domains_file, lang, API):
    data_list = []
    with open(domains_file, 'r') as f:
        domains = [line.strip() for line in f]
        for domain in domains:
            data_list.extend(d_fetches(domain, lang, API))
    df = pd.DataFrame(data_list, columns=['domain', 'url', 'lang', 'http'])
    df.to_csv('domains_data.csv', index=False)

def get_api_key():
    config = configparser.ConfigParser()
    if not os.path.exists('config.ini') or not config.read('config.ini') or not 'API' in config or not 'api_key' in config['API']:
        api_key = input("Entrez votre clé API: ")
        config['API'] = {'api_key': api_key}
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        return api_key
    else:
        return config['API']['api_key']

def main():
    api_key = get_api_key()
    domains_file = sys.argv[1] if len(sys.argv) > 1 else 'default_domains.txt'
    if domains_file == 'default_domains.txt':
        with open('default_domains.txt', 'w') as fichier:
            fichier.write('babbar.tech')
    d_fetches_to_csv(domains_file, 'all', api_key)

if __name__ == "__main__":
    main()

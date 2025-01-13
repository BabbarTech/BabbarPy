"""
MIT License

Copyright (c) 2023 BabbarTech

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import datetime
import pandas as pd
import requests
from requests.structures import CaseInsensitiveDict
import time
import configparser
import sys
import os

def get_api_key():
    config = configparser.ConfigParser()
    if not os.path.exists('config.ini') or not config.read('config.ini') or 'API' not in config or 'api_key' not in config['API']:
        api_key = input("Entrez votre clé API: ")
        config['API'] = {'api_key': api_key}
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        return api_key
    else:
        return config['API']['api_key']

def h_keywords(host, lang, country, start_date, end_date, api_key, max_retries=5):
    """Récupère les mots-clés pour un host donné, en gérant les éventuelles erreurs 429 (rate limit)."""

    # Convert start/end dates to datetime
    start_datetime = datetime.date(*map(int, start_date.split("-")))
    end_datetime = datetime.date(*map(int, end_date.split("-")))
    duration = end_datetime - start_datetime

    url = "https://www.babbar.tech/api/host/keywords"
    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    headers["Content-Type"] = "application/json"

    # DataFrame final
    kws = pd.DataFrame()

    current_datetime = start_datetime
    periods = duration.days + 1  # Nombre de jours à boucler

    for _ in range(periods):
        date_str = current_datetime.strftime("%Y-%m-%d")
        
        offset = 0
        # On va stocker ici les résultats journaliers
        kws_bydate = pd.DataFrame()

        while True:
            data = {
                'host': host,
                'lang': lang,
                'country': country,
                'date': date_str,
                'offset': offset,
                'n': 500,
                'min': 1,
                'max': 100
            }

            attempts = 0
            while attempts < max_retries:
                resp = requests.post(url, headers=headers, params={'api_token': api_key}, json=data)

                if resp.status_code == 200:
                    # Succès
                    aDict = resp.json()
                    if 'entries' not in aDict or not aDict['entries']:
                        # Plus de data, on sort de la boucle "while True"
                        break

                    print(f"Fetching {host} on {date_str}, offset={offset}")
                    # On récupère le remain pour surveiller le quota
                    remain = resp.headers.get('X-RateLimit-Remaining')
                    if remain is not None:
                        remain = int(remain)
                        if remain <= 0:
                            print("[INFO] Rate limit atteint, pause de 60s...")
                            time.sleep(60)

                    kws_fetch = pd.DataFrame(
                        aDict['entries'],
                        columns=[
                            'feature', 'rank', 'subRank', 'keywords', 'url',
                            'numberOfWordsInKeyword','bks'
                        ]
                    )
                    kws_fetch['date'] = date_str
                    kws_bydate = pd.concat([kws_bydate, kws_fetch], ignore_index=True)
                    
                    offset += 1
                    # Petites pauses pour éviter la rafale
                    time.sleep(0.2)
                    break  # on quitte la boucle de retry
                else:
                    # Cas d'erreur
                    if resp.status_code == 429:
                        # Tentative d'extraire Retry-After
                        retry_after = resp.headers.get("Retry-After")
                        if retry_after is not None:
                            wait_time = int(retry_after) + 1
                        else:
                            wait_time = 60
                        print(f"[{host}] Error 429, pause {wait_time}s avant retry.")
                        time.sleep(wait_time)
                        attempts += 1
                    else:
                        # Autres erreurs (4XX, 5XX)
                        print(f"STATUS CODE INVALID: {resp.status_code}")
                        # On peut sortir directement
                        attempts = max_retries
                # Fin if/else

            # Fin while attempts

            if attempts >= max_retries:
                # On n'a pas réussi à récupérer plus
                print(f"Abandon pour {host} sur {date_str} après trop d'erreurs.")
                break

            # Si on a break du bloc 'resp.status_code == 200' => on check si plus de data
            if resp.status_code != 200 or 'entries' not in resp.json():
                break

        # Fin while True => on a terminé le jour "date_str"
        kws = pd.concat([kws, kws_bydate], ignore_index=True)
        current_datetime += datetime.timedelta(days=1)

    return kws

def babbar_keywords_to_csv(host, lang, country, start_date, end_date, api_key):
    df = h_keywords(host, lang, country, start_date, end_date, api_key)
    df.to_csv(f'{host}_keywords.csv', index=False)

def main():
    api_key = get_api_key()
    hosts_file = sys.argv[1] if len(sys.argv) > 1 else 'default_hosts.txt'
    date_start = datetime.date.today() - datetime.timedelta(weeks=2)
    date_formatted = date_start.strftime("%Y-%m-%d")

    if hosts_file == 'default_hosts.txt':
        with open('default_hosts.txt', 'w') as fichier:
            fichier.write('www.babbar.tech')

    with open(hosts_file, 'r') as f:
        hosts = [line.strip() for line in f]
        for host in hosts:
            babbar_keywords_to_csv(host, 'fr', 'FR', date_formatted, date_formatted, api_key)

if __name__ == "__main__":
    main()

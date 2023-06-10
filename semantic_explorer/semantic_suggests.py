"""
MIT License

Copyright (c) 2023 BabbarTech & PierreFECalvet

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
import csv
import requests
import sys
import configparser
import os
import time

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

def semantic_suggests(query, api_key, lang="fr"):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    params = {
        'api_token': api_key
    }
    url_api = 'https://www.babbar.tech/api/semantic-explorer/suggests'
    data = {
        'q': query,
        'lang':lang
    }
    response = requests.post(url_api, headers=headers, params=params, json=data)
    remain = int(response.headers.get('X-RateLimit-Remaining', 1))
    if remain == 0:
        time.sleep(60)
    response_data = response.json()
    return response_data

def main():
    api_key = get_api_key()
    keywords_file = sys.argv[1] if len(sys.argv) > 1 else 'default_keywords.txt'
    if keywords_file == 'default_keywords.txt':
        with open('default_keywords.txt', 'w') as fichier:
            fichier.write('choucroute')
    with open(keywords_file, 'r') as f:
        keywords = [line.strip() for line in f]
    with open('semantic_explorer_suggests.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['query', 'intentions', 'questions'])
    for query in keywords:
        semantic_suggests_tocsv(query, api_key, 'fr')
        
def semantic_suggests_tocsv(query, api_key, lang):
    data = semantic_suggests(query, api_key, lang)
    intentions = data['intentions']
    items = data['items']
    with open('semantic_explorer_suggests.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        for item in items:
            title = item['title']
            writer.writerow([query, intentions, title])

if __name__ == "__main__":
    main()
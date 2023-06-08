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
import requests
import csv
import pandas as pd
import sys
import configparser
import os
import datetime

# Définir les paramètres communs
def u_keywords(urls, api_key, start_date, end_date, min =1, max=100, lang ="fr", country="FR"):
    start_datetime = datetime.date(int(start_date.split("-")[0]),int(start_date.split("-")[1]),int(start_date.split("-")[2]))
    end_datetime = datetime.date(int(end_date.split("-")[0]),int(end_date.split("-")[1]),int(end_date.split("-")[2]))
    duration = end_datetime-start_datetime
    current_datetime = start_datetime
    periods = duration.days + 1
    api_url = "https://www.babbar.tech/api/url/keywords"
    data_to_export = []
    for i in range(periods):
        print("day "+str(i +1))
        for url in urls:
            payload = {
                "url": url,
                "lang": lang,
                "country": country,
                "date": start_date,
                "offset": 0,
                "n": 500,
                "min": min,
                "max": max,
                "api_token": api_key  # Ajouter l'API token aux paramètres
            }
            response = requests.post(api_url, json=payload)
            data = response.json()
            entries = data.get('entries', [])
            for entry in entries:
                data_to_export.append({
                    'url': entry['url'],
                    'keywords': entry['keywords'],
                    'rank': entry['rank'],
                    'subRank': entry['subRank'],
                    'feature': entry['feature'],
                    'date': current_datetime
                })
    current_datetime = current_datetime + datetime.timedelta(days=1)
    return data_to_export

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
    date_start = datetime.date.today()-datetime.timedelta(weeks=2)
    date_formated = date_start.strftime("%Y-%m-%d")
    api_key = get_api_key()
    source_file = sys.argv[1] if len(sys.argv) > 1 else 'default_1_url.txt'
    fieldnames = ['url', 'keywords', 'rank', 'subRank', 'feature', 'date']
    with open('url_keywords_out.csv', 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
    if source_file == 'default_1_url.txt':
        with open('default_1_url.txt', 'w') as fichier:
            fichier.write('https://www.babbar.tech')
    with open(source_file, 'r') as file:
        urls = file.read().splitlines()
        data_to_export = u_keywords(urls, api_key, date_formated, date_formated)
        fieldnames = ['url', 'keywords', 'rank', 'subRank', 'feature', 'date']
        with open('url_keywords_out.csv', 'w', newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(data_to_export)

if __name__ == "__main__":
    main()
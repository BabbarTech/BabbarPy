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
import datetime
import pandas as pd
import requests
from requests.structures import CaseInsensitiveDict
import time
import configparser
import sys
import os

def h_keywords(host,lang,country,start_date,end_date,API_KEY):
    start_datetime = datetime.date(int(start_date.split("-")[0]),int(start_date.split("-")[1]),int(start_date.split("-")[2]))
    end_datetime = datetime.date(int(end_date.split("-")[0]),int(end_date.split("-")[1]),int(end_date.split("-")[2]))
    duration = end_datetime-start_datetime
    current_datetime = start_datetime
    a = 0
    list01 = [" "]
    kws = pd.DataFrame()
    kws_bydate = pd.DataFrame()
    url = "https://www.babbar.tech/api/host/keywords?api_token="+API_KEY
    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    periods = duration.days + 1
    for i in range(periods):
        print("day "+str(i +1))
        date = str(current_datetime.year)+'-'+str(current_datetime.month)+'-'+str(current_datetime.day)
        while list01 != []:
            data = '{"host": "'+str(host)+'",  "lang": "'+str(lang)+'",  "country": "'+str(country)+'",  "date": "'+str(date)+'",  "offset": '+str(a)+',  "n": 500,  "min": 1,  "max": 100}'
            resp = requests.post(url, headers=headers, data=data)
            if resp.status_code != 200:
                print("STATUS CODE INVALID")
                print(resp.status_code)
                list01 = []
                break
            else:
                aDict = resp.json()
                remain = int(resp.headers.get('X-RateLimit-Remaining'))
                if remain == 0:
                    time.sleep(60)
                list01 = aDict['entries']
                kws_fetch = pd.DataFrame(list01, columns = ['feature','rank','subRank','keywords','url','numberOfWordsInKeyword','bks'])
                kws_bydate = pd.concat([kws_bydate,kws_fetch])
                kws_bydate = kws_bydate.assign(date = current_datetime)
                a = a +1
        current_datetime = current_datetime + datetime.timedelta(days=1)
        kws = pd.concat([kws,kws_bydate])
        a=0
        list01 = [" "]
    return(kws)
def babbar_keywords_to_csv(h,l,c,s,e,API):
    df = h_keywords(h,l,c,s,e,API)
    df.to_csv(f'{h}_keywords.csv')

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
    hosts_file = sys.argv[1] if len(sys.argv) > 1 else 'default_hosts.txt'
    date_start = datetime.date.today()-datetime.timedelta(weeks=2)
    date_formated = date_start.strftime("%Y-%m-%d")
    if hosts_file == 'default_hosts.txt':
        with open('default_hosts.txt', 'w') as fichier:
            fichier.write('www.babbar.tech')
    with open(hosts_file, 'r') as f:
        hosts = [line.strip() for line in f]
        for host in hosts:
            babbar_keywords_to_csv(host,'fr','FR',date_formated,date_formated,api_key)

if __name__ == "__main__":
    main()
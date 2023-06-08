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
import time
import configparser
import os
import sys
import csv

def u_overview(fetch_url, API):
    url = "https://www.babbar.tech/api/url/overview/main"
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    data = {"url": fetch_url}
    params = {"api_token": API}
    response = requests.post(url, headers=headers, params=params, json=data)
    remain = int(response.headers.get('X-RateLimit-Remaining'))
    if remain == 0:
        time.sleep(60)
    if response.status_code == 200:
        result_dict = response.json()
        return(result_dict)
    else:
        print("Request failed with status code", response.status_code)

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
    
if __name__ == "__main__":
    api_key = get_api_key()
    source_file = sys.argv[1] if len(sys.argv) > 1 else 'default_1_url.txt'
    if source_file == 'default_1_url.txt':
        with open('default_1_url.txt', 'w') as fichier:
            fichier.write('https://www.babbar.tech')
    mydictionary = {"url" : [], "pageValue" : [], "pageTrust" : [], "semanticValue" : [], "babbarAuthorityScore" : [], "backlinks" : [], "referringhosts" : []}
    with open(source_file, 'r') as file:
        for url in file:
            url_foo = url.replace("\n", "")
            temp_dict = u_overview(url_foo, api_key)
            mydictionary["url"].append(url_foo)
            if temp_dict is not None:
                if "pageValue" in temp_dict:
                    mydictionary["pageValue"].append(temp_dict["pageValue"])
                else:
                    mydictionary["pageValue"].append(None)
                if "pageTrust" in temp_dict:
                    mydictionary["pageTrust"].append(temp_dict["pageTrust"])
                else:
                    mydictionary["pageTrust"].append(None)
                if "semanticValue" in temp_dict:
                    mydictionary["semanticValue"].append(temp_dict["semanticValue"])
                else:
                    mydictionary["semanticValue"].append(None)
                if "babbarAuthorityScore" in temp_dict:
                    mydictionary["babbarAuthorityScore"].append(temp_dict["babbarAuthorityScore"])
                else:
                    mydictionary["babbarAuthorityScore"].append(None)
                if "backlinks" in temp_dict:
                    if "linkCount" in temp_dict["backlinks"]:
                        mydictionary["backlinks"].append(temp_dict["backlinks"]["linkCount"])
                    else:
                        mydictionary["backlinks"].append(None)
                    if "hostCount" in temp_dict["backlinks"]:
                        mydictionary["referringhosts"].append(temp_dict["backlinks"]["hostCount"])
                    else:
                        mydictionary["referringhosts"].append(None)
                else:
                    mydictionary["backlinks"].append(None)
                    mydictionary["referringhosts"].append(None)
            else:
                # Ajoutez des valeurs None à toutes les clés du dictionnaire en cas de temp_dict = None
                mydictionary["pageValue"].append(None)
                mydictionary["pageTrust"].append(None)
                mydictionary["semanticValue"].append(None)
                mydictionary["babbarAuthorityScore"].append(None)
                mydictionary["backlinks"].append(None)
                mydictionary["referringhosts"].append(None)
    with open("output.csv", "w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        # Write the header row
        writer.writerow(mydictionary.keys())
        # Write the data rows
        writer.writerows(zip(*mydictionary.values()))

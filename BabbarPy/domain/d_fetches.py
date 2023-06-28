import pandas as pd
import requests
from requests.structures import CaseInsensitiveDict
import time
import configparser
import sys
import os

def d_fetches(domain, api_key, lang="fr"):
    a = 0
    data_list = []
    url = "https://www.babbar.tech/api/domain/fetches/list?api_token=" + api_key
    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    # Iterate until all data is fetched
    while True:
        data = {
            "domain": domain,
            "status": -1,
            "lang": lang,
            "offset": a,
            "n": 499
        }
        resp = requests.post(url, headers=headers, json=data)
        # Check if the response status code is valid
        if resp.status_code != 200:
            print("STATUS CODE INVALID")
            print(resp.status_code)
            break
        else:
            try:
                aList = resp.json()
                # Check if the response is a list
                if isinstance(aList, list):
                    if not aList:
                        print("No more data.")
                        break
                    # Check the remaining rate limit and wait if necessary
                    remain = int(resp.headers.get('X-RateLimit-Remaining'))
                    if remain == 0:
                        time.sleep(60)
                    # Process each entry in the response list
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
    # Read the domains from the domains_file
    with open(domains_file, 'r') as f:
        domains = [line.strip() for line in f]
        # Fetch data for each domain and extend the data_list
        for domain in domains:
            data_list.extend(d_fetches(domain, API, lang))
    # Convert the data_list to a DataFrame
    df = pd.DataFrame(data_list, columns=['domain', 'url', 'lang', 'http'])
    # Write the DataFrame to a CSV file
    df.to_csv('domains_data.csv', index=False)

def get_api_key():
    config = configparser.ConfigParser()
    # Check if the 'config.ini' file does not exist or cannot be read,
    # or if the 'API' section or 'api_key' key are not present in the config
    if not os.path.exists('config.ini') or not config.read('config.ini') or not 'API' in config or not 'api_key' in config['API']:
        # Prompt the user to enter their API key
        api_key = input("Entrez votre clé API: ")
        # Update the 'config' object with the API key
        config['API'] = {'api_key': api_key}
        # Write the updated config object to the 'config.ini' file
        with open('config.ini', 'w') as configfile:
            config.write(configfile)
        # Return the API key
        return api_key
    else:
        # If the 'config.ini' file exists and contains the API key,
        # return the API key from the config
        return config['API']['api_key']

def main():
    api_key = get_api_key()
    domains_file = sys.argv[1] if len(sys.argv) > 1 else 'default_domains.txt'
    # If the domains_file is set to the default value, create the file and write a default domain
    if domains_file == 'default_domains.txt':
        with open('default_domains.txt', 'w') as fichier:
            fichier.write('babbar.tech')
    # Call the d_fetches_to_csv function to fetch and save data for the specified domains
    d_fetches_to_csv(domains_file, 'all', api_key)

if __name__ == "__main__":
    main()

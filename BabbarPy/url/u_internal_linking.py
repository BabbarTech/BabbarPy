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
#import libraries
import requests
import pandas as pd
import time
import os
import sys
import configparser
from requests.structures import CaseInsensitiveDict

def u_internal_linking(address,API_KEY, index_a = 0):
    #declare ALL the dataframes lists and variables needed
    list01 = pd.DataFrame({'similar_url', 'score', 'incomingLink', 'outboundLink'})
    #create the header data
    url = "https://www.babbar.tech/api/url/similar-links?api_token="+API_KEY
    headers = CaseInsensitiveDict()
    headers["accept"] = "application/json"
    headers["Content-Type"] = "application/json"
    data = '{  "url": "'+str(address)+'"}'
    resp = requests.post(url, headers=headers, data=data)
    print(resp.status_code)
    #handling status code different from 200
    if (resp.status_code != 200) :
        print("STATUS CODE INVALID")
    else:
        aDict = resp.json()
        #waiting when the rate is about to be exceeded
        remain = int(resp.headers.get('X-RateLimit-Remaining'))
        if remain == 1:
            time.sleep(60)
        #keeping the essentials: the known urls, the similarity score, the existing links
        list01 = pd.DataFrame({'similar_url': [x['similar'] for x in aDict], 'score': [x['score'] for x in aDict], 'incomingLink':[x['incomingLink'] for x in aDict], 'outboundLink': [x['outboundLink'] for x in aDict]})
        #add the source to allow multiple urls checks
        list01 = list01.assign(starturl = address)
        #change the score to a float to allow maths
        list01.score = [float(x) for x in list01.score]
        list01.index = (index_a*10)+list01.index
    #return to obtain the data out of the function
    return(list01)

def babbar_internal_linking_to_csv(url_txt_file,API):
    #set up the current working directory where the txt file should be found
    cwd = os.getcwd()+'\\'
    #open the file read it and close it
    with open(cwd+str(url_txt_file), "r") as file:
        url_list = file.read().split("\n")
    #set up the lists and variables
    df = pd.DataFrame()
    df_full = pd.DataFrame()
    # url_list = url_txt.readlines()
    lenlist = len(url_list)
    a = 0
    list2 = []
    #create a list to call every urls in the file
    while(a < lenlist):
        list2.append(a)
        a = a+1
    #asking for each urls and concatenate to have the full data
    for i in list2:
        url = url_list[i]
        print(url)
        df = u_internal_linking(url,API, i)
        #if(type(df)
        df_full = pd.concat([df_full, df])
    #export to csv
    df_full.to_csv('babbar_internal_linking.csv')

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
    # Check if a URLs file is provided as a command-line argument, otherwise use the default file 'default_urls.txt'
    urls_file = sys.argv[1] if len(sys.argv) > 1 else 'default_urls.txt'
    # Retrieve the API key
    api_key = get_api_key()
    # If the URLs file is the default file, create it and write a sample URL
    if urls_file == 'default_urls.txt':
        with open('default_urls.txt', 'w') as fichier:
            fichier.write('https://www.babbar.tech')
    # Extract Babbar internal linking data and save it to a CSV file
    babbar_internal_linking_to_csv(urls_file, api_key)

if __name__ == "__main__":
    main()

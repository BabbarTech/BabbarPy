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
import requests
import pandas as pd
import configparser
import os
import sys
import time

def u_semanticSimilarity(api_key, source_url, target_url):
    url = "https://www.babbar.tech/api/url/semanticSimilarity"
    headers = {"accept": "application/json", "Content-Type": "application/json"}
    params = {'api_token': api_key}
    data = {
        "source": source_url,
        "target": target_url,
    }
    response = requests.post(url, headers=headers, params=params, json=data)
    remain = int(response.headers.get('X-RateLimit-Remaining'))
    if remain == 0:
        time.sleep(60)
    if response.status_code == 200:
        result = response.json()
        df = pd.DataFrame([result])
        df['source'] = source_url
        df['target'] = target_url
        if 'lang' in result:
            df['lang'] = result['lang']
        else:
            df['lang'] = "n/a"
        df = df[['source', 'target','semanticSimilarity', 'lang']]
        return df
    else:
        print(f"Erreur lors de la requête à l'API : {response.status_code}")

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
    # Get the API key
    api_key = get_api_key()
    # Determine the source file containing the URLs
    source_file = sys.argv[1] if len(sys.argv) > 1 else 'default_2_urls.csv'
    # If the source file is the default file, create it with sample data
    if source_file == 'default_2_urls.csv':
        df = pd.DataFrame({'source': ["https://babbar.academy/blog/"],
                           'target': ['https://blog.babbar.tech/']})
        df.to_csv(source_file, index=False)
    # Read the URLs from the source file
    df = pd.read_csv(source_file)
    # Process each row (URL pair) in the DataFrame
    for index, row in df.iterrows():
        source = row['source']
        target = row['target']
        # Compute semantic similarity between the source and target URLs
        df = u_semanticSimilarity(api_key, source, target)
        # Write the similarity results to a CSV file
        with open("semantic_similarity_results.csv", 'a', newline='') as f:
            df.to_csv(f, header=f.tell() == 0, index=False)
    
if __name__ == "__main__":
    main()
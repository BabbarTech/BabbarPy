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
import csv
import requests
import sys
import configparser
import os
import time

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

def onpage_analyzis(url, api_key):
    # Set the headers for the API request
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    # Set the API token in the request parameters
    params = {
        'api_token': api_key
    }
    # Define the API URL
    url_api = 'https://www.babbar.tech/api/analyze-on-page'
    # Set the data payload for the request
    data = {
        'url': url,
    }
    # Send a POST request to the API
    response = requests.post(url_api, headers=headers, params=params, json=data)
    # Check the remaining rate limit
    remain = int(response.headers.get('X-RateLimit-Remaining', 1))
    # If the rate limit is reached, wait for 60 seconds before proceeding
    if remain == 0:
        time.sleep(60)
    # Parse the JSON response data
    response_data = response.json()
    # Return the response data
    return response_data

def main():
    # Get the API key
    api_key = get_api_key()
    # Check if a custom URLs file is provided as a command-line argument
    # Otherwise, use the default URLs file 'default_urls.txt'
    urls_file = sys.argv[1] if len(sys.argv) > 1 else 'default_urls.txt'
    # If the default URLs file is used, create it and add a default URL
    if urls_file == 'default_urls.txt':
        with open('default_urls.txt', 'w') as fichier:
            fichier.write('https://www.babbar.tech')
    # Read the URLs from the file
    with open(urls_file, 'r') as f:
        urls = [line.strip() for line in f]
    # Create a new CSV file to store the analysis results
    with open('onpage_analyzis_results.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Write the header row in the CSV file
        writer.writerow(['url', 'h1_count', 'h1_list', 'title_count', 'title_list',
                         'meta_description_count', 'meta_description_list', 'h2_count',
                         'h3_count', 'h4_count', 'h5_count', 'h6_count', 'h2_list',
                         'h3_list', 'h4_list', 'h5_list', 'h6_list', 'img_count',
                         'img_list', 'img_alt_list', 'a_count_total', 'a_count_follow',
                         'a_count_nofollow', 'a_count_sponsored', 'a_count_ugc',
                         'a_count_internals', 'a_count_externals', 'a_list_href',
                         'a_list_follow', 'a_list_internal', 'meta_robots_list',
                         'rel_canonical_list', 'relevant_text', 'text_percentage',
                         'relevant_text_percentage'])
    # Perform on-page analysis for each URL
    for url in urls:
        onpage_a_tocsv(url, api_key)
        
def onpage_a_tocsv(url, api_key):
    # Perform on-page analysis for the given URL and retrieve the data
    data = onpage_analyzis(url, api_key)
    # Open the CSV file in append mode to add the analysis results
    with open('onpage_analyzis_results.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Extract relevant data from the response data and assign them to variables
        url = data['url']
        h1_count = data['result']['balises']['h1']['count']['total']
        h1_list = '|||'.join([item['nodeValue'] for item in data['result']['balises']['h1']['list']]).replace('\n', ' ')
        title_count = data['result']['balises']['title']['count']['total']
        title_list = '|||'.join([item['nodeValue'] for item in data['result']['balises']['title']['list']]).replace('\n', ' ')
        meta_description_count = data['result']['balises']['meta_description']['count']['total']
        meta_description_list = '|||'.join([item['content'] for item in data['result']['balises']['meta_description']['list']]).replace('\n', ' ')
        h2_count = data['result']['balises']['h2']['count']['total']
        h3_count = data['result']['balises']['h3']['count']['total']
        h4_count = data['result']['balises']['h4']['count']['total']
        h5_count = data['result']['balises']['h5']['count']['total']
        h6_count = data['result']['balises']['h6']['count']['total']
        h2_list = '|||'.join([item['nodeValue'] for item in data['result']['balises']['h2']['list']]).replace('\n', ' ')
        h3_list = '|||'.join([item['nodeValue'] for item in data['result']['balises']['h3']['list']]).replace('\n', ' ')
        h4_list = '|||'.join([item['nodeValue'] for item in data['result']['balises']['h4']['list']]).replace('\n', ' ')
        h5_list = '|||'.join([item['nodeValue'] for item in data['result']['balises']['h5']['list']]).replace('\n', ' ')
        h6_list = '|||'.join([item['nodeValue'] for item in data['result']['balises']['h6']['list']]).replace('\n', ' ')
        img_count = data['result']['balises']['img']['count']['total']
        img_list = '|||'.join([item['src'] for item in data['result']['balises']['img']['list']]).replace('\n', ' ')
        img_alt_list = '|||'.join([item['alt'] for item in data['result']['balises']['img']['list']]).replace('\n', ' ')
        a_count_total = data['result']['balises']['a']['count']['total']
        a_count_follow = data['result']['balises']['a']['count']['follow']
        a_count_nofollow = data['result']['balises']['a']['count']['nofollow']
        a_count_sponsored = data['result']['balises']['a']['count']['sponsored']
        a_count_ugc = data['result']['balises']['a']['count']['ugc']
        a_count_internals = data['result']['balises']['a']['count']['internals']
        a_count_externals = data['result']['balises']['a']['count']['externals']
        a_list_href = '|||'.join([item['href'] for item in data['result']['balises']['a']['list']]).replace('\n', ' ')
        a_list_follow = '|||'.join([str(item['follow']) for item in data['result']['balises']['a']['list']]).replace('\n', ' ')
        a_list_internal = '|||'.join([str(item['internal']) for item in data['result']['balises']['a']['list']]).replace('\n', ' ')
        meta_robots_list = '|||'.join([item['content'] for item in data['result']['balises']['meta_robots']['list']]).replace('\n', ' ')
        rel_canonical_list = '|||'.join([item['href'] for item in data['result']['balises']['rel_canonical']['list']]).replace('\n', ' ')
        relevant_text = data['result']['text']['relevant_text'].replace('\n', ' ')
        text_percentage = data['result']['text']['text_percentage']
        relevant_text_percentage = data['result']['text']['relevant_text_percentage']
        # Write a row with the extracted data to the CSV file
        writer.writerow([url, h1_count, h1_list, title_count, title_list, meta_description_count,
                         meta_description_list, h2_count, h3_count, h4_count, h5_count,
                         h6_count, h2_list, h3_list, h4_list, h5_list, h6_list, img_count,
                         img_list, img_alt_list, a_count_total, a_count_follow,
                         a_count_nofollow, a_count_sponsored, a_count_ugc,
                         a_count_internals, a_count_externals, a_list_href, a_list_follow,
                         a_list_internal, meta_robots_list, rel_canonical_list, relevant_text,
                         text_percentage, relevant_text_percentage])

if __name__ == "__main__":
    main()
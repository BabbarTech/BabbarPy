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
import configparser
import csv
import requests
import os
import time
import sys

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

def d_history(domain, api_key):
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }
    params = {
        'api_token': api_key
    }
    url = 'https://www.babbar.tech/api/domain/history'
    data = {
        'domain': domain,
    }
    # Send a POST request to the API
    response = requests.post(url, headers=headers, params=params, json=data)
    response_data = response.json()
    # Convert the response to JSON format
    remain = int(response.headers.get('X-RateLimit-Remaining', 1))
    if remain == 0:
        print(f"holding at{data['offset']}")
        # Print a message if the rate limit is reached
        time.sleep(60)
        # Wait for 60 seconds
    return response_data
    # Return the JSON response data

def main():
    # Retrieve the API key using the get_api_key function.
    api_key = get_api_key()
    # Determine the domains_file based on the command-line arguments. If no argument is provided, it defaults to 'default_domains.txt'.
    domains_file = sys.argv[1] if len(sys.argv) > 1 else 'default_domains.txt'
    # If the domains_file is set to 'default_domains.txt', create and write the default domain 'babbar.tech' to the file.
    if domains_file == 'default_domains.txt':
        with open('default_domains.txt', 'w') as fichier:
            fichier.write('babbar.tech')
    # Open the domains_file and read its content, storing each line as a domain in the domains list.
    with open(domains_file, 'r') as f:
        domains = [line.strip() for line in f]
    # Define the fieldnames list that represents the headers for the CSV file.
    fieldnames = [
        "Date", "View", "Domain", "domainValue", "domainTrust", "BabbarConnect", "SemanticValue",
        "BabbarAuthorityScore", "IPs", "LastUpdate", "KnownUrls", "LinkCount", "AnchorCount",
        "HostCount", "DomainCount", "IPCount", "ASCount", "LanguageCounters", "CountryCounters",
        "Languages", "Health", "H2xx", "H3xx", "H4xx", "H5xx", "HFailed", "HRobotsDenied", "Hxxx",
        "Categories"
    ]
    # Open a new CSV file named 'domain_history.csv' for writing, specifying the encoding as UTF-8 with a BOM signature ('utf-8-sig').
    # This will ensure proper character encoding in the resulting CSV file.
    with open("domain_history.csv", "w", newline="", encoding='utf-8-sig') as csvfile:
        # Create a csv.DictWriter object named writer for writing dictionaries to the CSV file.
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # Write the header using the writer.writeheader() method.
        writer.writeheader()
    # Iterate over each domain in the domains list.
    for domain in domains:
        # Retrieve the historical data for the current domain using the d_history function and the api_key.
        data = d_history(domain, api_key)
        # Open the 'domain_history.csv' file in append mode for writing.
        with open("domain_history.csv", "a", newline="", encoding='utf-8-sig') as csvfile:
            # Create a new csv.DictWriter object named writer for writing dictionaries to the CSV file.
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # Iterate over each date and entry in the data dictionary items.
            for date, entry in data.items():
                # Extract the necessary information from the entry dictionary to populate the row dictionary.
                language_counters = entry.get("backlinks", {}).get("languageCounters")
                language_counters_str = " ||| ".join([f"{counter['language']} ({counter['count']})" for counter in language_counters])
                country_counters = entry.get("backlinks", {}).get("countryCounters")
                country_counters_str = " ||| ".join([f"{counter['country']} ({counter['count']})" for counter in country_counters])
                categories = entry.get("categories")
                categories_list = []
                for lang, topics in categories.items():
                    for topic in topics:
                        categories_list.append(f"{topic['topic']} ({lang} : {topic['score']})")
                categories_str = " ||| ".join(categories_list)
                languages = entry.get("languages")
                languages_str = " ||| ".join([f"{lang['language']} ({lang['percent']}%)" for lang in languages])
                # Create a row dictionary with all the extracted information.
                row = {
                    "Date": date,
                    "View": entry.get("view"),
                    "Domain": domain,
                    "domainValue": entry.get("domainValue"),
                    "domainTrust": entry.get("domainTrust"),
                    "BabbarConnect": entry.get("BabbarConnect"),
                    "SemanticValue": entry.get("semanticValue"),
                    "BabbarAuthorityScore": entry.get("babbarAuthorityScore"),
                    "IPs": "|||".join(entry.get("ips")),
                    "LastUpdate": entry.get("lastUpdate"),
                    "KnownUrls": entry.get("knownUrls"),
                    "LinkCount": entry.get("backlinks", {}).get("linkCount"),
                    "AnchorCount": entry.get("backlinks", {}).get("anchorCount"),
                    "HostCount": entry.get("backlinks", {}).get("hostCount"),
                    "DomainCount": entry.get("backlinks", {}).get("domainCount"),
                    "IPCount": entry.get("backlinks", {}).get("ipCount"),
                    "ASCount": entry.get("backlinks", {}).get("asCount"),
                    "LanguageCounters": language_counters_str,
                    "CountryCounters": country_counters_str,
                    "Languages": languages_str,
                    "Health": entry.get("health"),
                    "H2xx": entry.get("h2xx"),
                    "H3xx": entry.get("h3xx"),
                    "H4xx": entry.get("h4xx"),
                    "H5xx": entry.get("h5xx"),
                    "HFailed": entry.get("hfailed"),
                    "HRobotsDenied": entry.get("hRobotsDenied"),
                    "Hxxx": entry.get("hxxx"),
                    "Categories": categories_str
                }
                # Write the row dictionary as a new row in the CSV file using the writer.writerow(row) method.
                writer.writerow(row)

if __name__ == "__main__":
    main()
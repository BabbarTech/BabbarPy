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
import configparser
import csv
import requests
import os
import time
import sys

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
    response = requests.post(url, headers=headers, params=params, json=data)
    response_data = response.json()
    remain = int(response.headers.get('X-RateLimit-Remaining', 1))
    if remain == 0:
        print(f"holding at{data['offset']}")
        time.sleep(60)
    return response_data

def main():
    api_key = get_api_key()
    domains_file = sys.argv[1] if len(sys.argv) > 1 else 'default_domains.txt'
    if domains_file == 'default_domains.txt':
        with open('default_domains.txt', 'w') as fichier:
            fichier.write('babbar.tech')
    with open(domains_file, 'r') as f:
        domains = [line.strip() for line in f]
    fieldnames = [
            "Date", "View", "Domain", "domainValue", "domainTrust", "BabbarConnect", "SemanticValue",
            "BabbarAuthorityScore", "IPs", "LastUpdate", "KnownUrls", "LinkCount", "AnchorCount",
            "HostCount", "DomainCount", "IPCount", "ASCount", "LanguageCounters", "CountryCounters",
            "Languages", "Health", "H2xx", "H3xx", "H4xx", "H5xx", "HFailed", "HRobotsDenied", "Hxxx",
            "Categories"
        ]
    with open("domain_history.csv", "w", newline="", encoding='utf-8-sig') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
    for domain in domains:
        data = d_history(domain,api_key)
        with open("domain_history.csv", "a", newline="", encoding='utf-8-sig') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            for date, entry in data.items():
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
                writer.writerow(row)

if __name__ == "__main__":
    main()
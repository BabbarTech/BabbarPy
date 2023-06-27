import os
import configparser
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

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
    with open("requirements.txt", 'r') as f:
        packages = [line.strip() for line in f]
        for package in packages:
            install(package)
    get_api_key()

if __name__ == "__main__":
    main()
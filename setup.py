import os
import configparser
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
    
def main():
    with open("requirements.txt", 'r') as f:
        packages = [line.strip() for line in f]
        for package in packages:
            install(package)

if __name__ == "__main__":
    main()
# BabbarPy

This project involves the use of executable Python files as command-line interfaces (CLI) to interact with the babbar.tech API. The goal is to extract metrics using the provided tool on lists of URLs, hosts, or URL pairs.

## Prerequisites
Before running the Python scripts, make sure you have the following:

1. Python installed on your system (version 3.11.3 or higher).
2. Required Python libraries. You can install them by running the following command (running setup.py ensures this):
pip install -r requirements.txt

## Configuration
Before you can use the scripts, you need to provide certain configuration information. Here are the steps to follow:

1. Run the setup.py file.
2. You will be prompted to provide your API key in the terminal.

Alternative: Create a config.ini file:

```
[API]
api_key: YOUR_API_KEY
```

Replace 'YOUR_API_KEY' with your API key provided by babbar.tech.

## Usage

To run the scripts and obtain metrics from different lists, follow the instructions below:

1. Open a command prompt in the project directory.
2. Execute the corresponding Python scripts based on your needs, function_name.py, with the appropriate arguments. Here are some examples:

  - To process a list of URLs from a text file:
     ```
     python url/u_backlinks_url.py urls.txt
     ```
  - To process a list of hosts:
     ```
     python host/h_health.py hosts.txt
     ```
  - To process a list of URL pairs: (remember to place the sources in the 1st column and the targets in the 2nd column)
    ```
    python url/u_fi.py couples.csv
    ```

Make sure to adapt the file names and types according to your needs.
   
## Other Planned Use Cases
   
   To use the scripts as a Python library, basic functions can be imported using Python
   
   (`from BabbarPY.host import *` is now available)

## Additional Documentation

- babbar.tech API documentation: [babbar tech doc](https://www.babbar.tech/doc-api/)
- Known issues: Check the `issues.md` file, if present, for a list of known issues and workarounds.

"""
Scrape AI For People's list of educational resources from:
https://www.aiforpeople.org/educational-resources/
"""

import os.path
import requests
from bs4 import BeautifulSoup
import pandas as pd


tempFilename = "/tmp/resources.html"

if not os.path.isfile(tempFilename):
    resp = requests.get('https://www.aiforpeople.org/educational-resources/')
    with open(tempFilename, 'w') as f:
        f.write(resp.text)

with open(tempFilename) as f:
    rawHtml = f.read()

soup = BeautifulSoup(rawHtml)

table = str(soup.find('table'))

df = pd.read_html(table)

df[0].to_json("aiForPeopleResources.json")

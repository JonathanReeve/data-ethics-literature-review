import json
import requests
import sys

query = sys.argv[1]
baseURL = "https://www.wikidata.org/w/api.php"
params = {"action": "wbsearchentities",
          "search": query,
          "language": "en",
          "format": "json"} 
response = requests.get(baseURL, params=params)

if response.ok:
    decoded = json.loads(response.text)
    for item in decoded['search']:
        print(item.get('id'), item.get('label'), item.get('description'))
else:
    print("Something went wrong.")
    print(response)

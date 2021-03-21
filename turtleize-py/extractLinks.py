#!/usr/bin/env python3

import requests
import re
from bs4 import BeautifulSoup
import translate # my own module
import rdflib



def getSyllabus(url):
    resp = requests.get(url)
    if resp.ok:
        return resp.text
    else:
        exit("Response not OK.")

def getURLs(html):
    soup = BeautifulSoup(html)
    links = soup.find_all('a')
    return [link.get('href') for link in links]

html = getSyllabus('http://www.cs.cornell.edu/courses/cs4732/2017sp/')
urls = getURLs(html)

allItemIDs = []
if len(urls) > 0:
  for url in urls:
      print(f"Trying url: {url}")
      rdf = translate.url2rdf(url)
      if rdf is not None:
          matches = re.finditer('<z:UserItem rdf:about="(.*?)">', rdf)
          itemIds = [match.group(1) for match in matches if match is not None]
          for itemId in itemIds:
              allItemIDs.append(itemId)
          print(rdf)

def formatIDs(itemList):
    """
    We have lots of zotero ids, and we want to turn these into links in RDF.
    """
    return f"""
    ccso:hasLM {" , ".join(itemList)} ;
    """

print(formatIDs(allItemIDs))

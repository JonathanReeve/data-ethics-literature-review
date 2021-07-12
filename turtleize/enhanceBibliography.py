#!/usr/bin/env python3

"""
So now we have turtle files which describe readings.
But that information isn't so complete or accurate.
So we need to ask some bibliographic databases online
for better information, so that we can enhance our graph.
"""

from rdflib.namespace import DC, DCTERMS, FOAF, RDF, OWL
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib import Namespace
import rdflib
import click
import sys
import requests
import logging
import json
from nltk.metrics.distance import edit_distance


turtleFile = "../data/texts/ttl/101.ttl"

def queryCrossRef(title, author=None):
    """
    Let's look up data from CrossRef. Here's the form we'll create,
    from their documentation here: https://github.com/CrossRef/rest-api-doc#resource-components
    https://api.crossref.org/works?query.author=richard+feynman

    Returns a list of possible candidates.
    """
    logging.info(f"Querying {title} by {author}")
    url = "https://api.crossref.org/works"
    params = {"query.bibliographic": title}
    if author:
        params['query.author'] = author
    resp = requests.get(url, params=params)
    if resp.ok:
        decoded = json.loads(resp.text)
        if 'message' in decoded:
            if 'items' in decoded['message']:
                return decoded['message']['items']
            else:
                logging.error("Can't find items.")
        else:
            logging.error("Can't find the message.")
    else:
        logging.error(f"Response not ok. Response: {resp}")


def main():
    g = rdflib.Graph()
    g.load(turtleFile, format="ttl")
    # for item in g:
    #     print(item)
    g.bind('z', 'http://www.zotero.org/namespaces/export#')
    g.bind('dcterms', 'http://purl.org/dc/terms/')
    g.bind('foaf', 'http://xmlns.com/foaf/0.1/')
    # This only works if we have the title and author.
    # data = g.query("""select distinct ?id ?title ?authorFirst ?authorLast where {
    #     ?id a z:UserItem .
    #     ?id res:resource ?doc .
    #     ?doc dcterms:title ?title .
    #     ?doc dcterms:creator ?author .
    #     ?author foaf:givenName ?authorFirst .
    #     ?author foaf:surname ?authorLast .
    # }""")
    # itemID, title, authorFirst, authorLast = list(data)[0]
    # print(title, authorFirst, authorLast)
    # This will work even if we don't have an author
    data = g.query("""select distinct ?id ?title ?authorFirst ?authorLast where {
        ?id a z:UserItem .
        ?id res:resource ?doc .
        ?doc dcterms:title ?title .
        OPTIONAL {
          ?doc dcterms:creator ?author .
          ?author foaf:givenName ?authorFirst .
          ?author foaf:surname ?authorLast .
        }
    }""")
    resultsDict = {}
    for result in data:
        itemID, title, authorFirst, authorLast = result
        print(itemID, title, authorFirst, authorLast)
        if authorFirst is not None and authorLast is not None:
            author = f"{authorFirst} {authorLast}"
        else:
            author = None
        itemID = str(itemID)
        if itemID in resultsDict:
            continue # Only take the first one for each ID
        else:
            resultsDict[itemID] = (title, author)
    for itemID, titleAuthor in resultsDict.items():
        title, author = titleAuthor
        candidates = queryCrossRef(title, author)
        logging.info(f"Title: {title}")
        # Compute Levenshtein (edit) distance of titles to find the best match.
        if candidates is not None:
            for i, candidate in enumerate(candidates):
                candidateTitle = candidate['title']
                logging.info(f"Candidate {i}: {candidateTitle}")
                distance = edit_distance(title, candidateTitle)
                logging.info(f"Distance: {distance}")



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

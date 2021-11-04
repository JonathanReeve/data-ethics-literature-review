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


turtleFile = "../data/coursesAndTexts.ttl"
maxDistance = 10

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


def similarPapers(textA, textB, maxDistance=maxDistance):
    """
    Tests whether two papers' titles are similar enough.
    """
    textA = textA.lower() # Get case-insensitive
    textB = textB.lower()
    if editRatio(textA, textB) < 0.2: # 80% similar titles
        logging.info('Texts are more than 80% similar in terms of edit distance.')
        return True
    else:
        # Truncate
        if len(textA) > 10:
            aHead = textA[:10]
        else:
            aHead = textA
        if len(textB) > 10:
            bHead = textB[:10]
        else:
            bHead = textB
        if editRatio(aHead, bHead) > 0.9: # 90% similar beginnings
            logging.info('Texts have beginnings that are more than 90% similar.')
            return True
        else:
            wordsA = set(textA.split())
            wordsB = set(textB.split())
            averageLength = (len(wordsA) + len(wordsB)) / 2
            intersection = wordsA.intersection(wordsB)
            if len(intersection) / averageLength > 0.8:
                # More than 80% identical words
                logging.info('Texts contain 80% identical words.')
                return True




def editRatio(textA, textB):
    """
    Computes the ratio of edit distances between two titles,
    in order to measure title similarity.
    """
    editDistance = edit_distance(textA, textB)
    logging.debug(f"Edit distance is {editDistance}")
    averageLength = len(textA) + len(textB) / 2
    logging.debug(f"Average length is {averageLength}")
    editRatio = editDistance / averageLength
    logging.debug(f"Edit ratio is {editRatio}")
    return editRatio


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
        # print(itemID, title, authorFirst, authorLast)
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
                if 'title' not in candidate:
                    logging.error("No title.")
                    logging.debug(candidate.keys())
                    continue
                if type(title) == list:
                    title = title[0] # Donno why these can be lists, but some are
                candidateTitle = candidate['title']
                if type(candidateTitle) == list:
                    candidateTitle = candidateTitle[0]
                title = str(title) # Convert from RDFTerm
                if similarPapers(title, candidateTitle):
                    logging.info("*** Found match! ***")
                    logging.info(f"Query: {title}")
                    logging.info(f"Match {i}: {candidateTitle}")
                    # logging.info(f"Distance: {distance}")
                    # print(candidate)
                    itemIDBare = itemID.split('/')[-1]
                    f = open(f"../data/texts/json/{itemIDBare}.json", 'w')
                    json.dump(candidate, f)
                    f.close()





if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

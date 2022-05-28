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
import os
import sys
import requests
import logging
import json
from nltk.metrics.distance import edit_distance
import time
from os.path import exists
from glob import glob
from itertools import groupby

base = 'https://data-ethics.net'
ccso = Namespace('https://w3id.org/ccso/ccso/')
cito = Namespace('http://purl.org/spar/cito')
de = Namespace(base + '/')
dePerson = Namespace(f'{base}/person/')
deCourse = Namespace(f'{base}/course/')
deText = Namespace(f'{base}/text/')
deUniversity = Namespace(f'{base}/university/')
g = rdflib.Graph()
g.bind('ccso', ccso)
g.bind('cito', cito)
g.bind('de', de)
g.bind('dePerson', dePerson)
g.bind('deCourse', deCourse)
g.bind('deText', deText)
g.bind('deUniversity', deUniversity)

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

def querySemanticScholarDetails(paperID, textID, citationsOrReferences):
    """
    We got the basic details from Semantic Scholar.
    Now we need to get the full details about the citations and references.
    """
    if citationsOrReferences not in ['citations', 'references']:
        logging.error("Type of query must be either citations or references.")
        return False
    # https://api.semanticscholar.org/graph/v1/paper/cb13b1b6a37e4080d8c13c5f33694b5aae90abcf/citations?fields=title,authors
    url = f"https://api.semanticscholar.org/graph/v1/paper/{paperID}/{citationsOrReferences}"
    fields = "contexts,intents,isInfluential,paperId,externalIds,url,title,abstract" + \
      ",venue,year,referenceCount,citationCount,influentialCitationCount,isOpenAccess," \
      "fieldsOfStudy,authors"
    params = {"fields": fields}
    resp = requests.get(url, params=params)
    if resp.ok:
        data = json.loads(resp.text)
        with open(f"../data/texts/json/semanticScholar/{textID}-{citationsOrReferences}.json", 'w') as f:
            f.write(json.dumps(data))
        return True
    else:
        logging.error("Response not OK!")
        return False



def querySemanticScholar(title, author=None):
    """ Look up data from Semantic Scholar.  """
    logging.info(f"Querying {title} by {author}")
    # https://api.semanticscholar.org/graph/v1/paper/search?query=literature+graph&offset=10&limit=50&fields=title,authors
    if author is None:
        author = ""
    query = title + " " + author
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    fields = "title,authors,externalIds,url,abstract," + \
        "venue,year,referenceCount,citationCount," + \
        "influentialCitationCount,isOpenAccess,fieldsOfStudy"
    params = {"query": query, "fields": fields}
    resp = requests.get(url, params=params)
    if resp.ok:
        data = json.loads(resp.text)
        print(data)
        if 'total' in data:
            if data['total'] > 0:
                return data['data']
            else:
                logging.error('No results!')
                return None
        else:
            logging.error('No results!')
            return None
    else:
        logging.error('Response not OK!')
        return None

def queryOpenLibrary(title, author=None):
    """
    We're probably dealing with a book, at this point.
    So let's look it up on Open Library!
    """
    # http://openlibrary.org/search.json?q=the+lord+of+the+rings
    url = "http://openlibrary.org/search.json"
    if author is not None:
        params = {"title": title, "author": author}
    else:
        params = {"title": title}
    resp = requests.get(url, params=params)
    if resp.ok:
        data = json.loads(resp.text)
        print(data)
        if 'numFound' in data:
            if data['numFound'] > 0:
                if 'docs' in data:
                    return data['docs']
                else:
                    logging.error('No docs!')
                    return None
            else:
                logging.error('No results!')
                return None
        else:
            logging.error('None found!')
            return None
    else:
        logging.error('Response not OK!')
        return None






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

def parseResults(candidates, title, itemID, source):
    """ Compute Levenshtein (edit) distance of titles to find the best match. """
    if source not in ['crossRef', 'semanticScholar', 'openLibrary']:
        logging.error('Source must be either crossRef or semanticScholar or openLibrary')
        return None
    if candidates is not None:
        for i, candidate in enumerate(candidates):
            if 'title' not in candidate:
                logging.error("No title.")
                logging.debug(candidate.keys())
                continue
            candidateTitle = candidate['title']
            if type(candidateTitle) == list:
                candidateTitle = candidateTitle[0] # Donno why these can be lists, but some are
            title = str(title) # Convert from RDFTerm
            if similarPapers(title, candidateTitle):
                logging.info("*** Found match! ***")
                logging.info(f"Query: {title}")
                logging.info(f"Match {i}: {candidateTitle}")
                # logging.info(f"Distance: {distance}")
                # print(candidate)
                itemIDBare = itemID.split('/')[-1]
                f = open(f"../data/texts/json/{source}/{itemIDBare}.json", 'w')
                json.dump(candidate, f)
                f.close()
                return True
    return False

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
        # Don't double-dip
        crossRefFile, semanticScholarFile = [f"../data/texts/bib/json/{source}/{itemID}.json" for source in ["crossRef", "semanticScholar"]]
        if not exists(crossRefFile):
            logging.info(f"Title: {title}")
            title, author = titleAuthor
            candidates = queryCrossRef(title, author)
            crossRefResult = parseResults(candidates, title, itemID, "crossRef")
        if not exists(semanticScholarFile):
            candidates = querySemanticScholar(title, author)
            semanticScholarResult = parseResults(candidates, title, itemID, "semanticScholar")
        if (not crossRefResult) and (not semanticScholarResult):
            # Check whether we have metadata files already stored.
            if not exists(crossRefFile) and not exists(semanticScholarFile):
                # Then we probably have a book, or something else weird
                candidates = queryOpenLibrary(title, author)
                openLibraryResult = parseResults(candidates, title, itemID, "openLibrary")
                if not openLibraryResult:
                    # Well let's just give up then
                    with open('unknown-bibs.txt', 'a') as f:
                        f.write(str(itemID))
            time.sleep(1) # Try to be polite to the APIs

def getSemanticScholarDetails():
    """
    Go through each of our entries from SemanticScholar data, and get citation details.
    """
    filenames = glob("../data/texts/json/semanticScholar/*.json")
    # print(filenames)
    for filename in filenames:
        stub = os.path.basename(filename)[:7]
        logging.info(f"Stub: {stub}")
        if filename.endswith('-citations.json') or filename.endswith('-references.json'):
            continue
        filenamesStartingWithThis = [fn for fn in filenames if fn.startswith(stub)]
        if len(filenamesStartingWithThis) > 1:
            logging.info(f"We already have it: {filenamesStartingWithThis}")
            continue # We already got this one
        logging.info(f"Getting details for: {filename}")
        fn = os.path.basename(filename)
        if fn.endswith('.json'):
            fn = fn[:-5] # Strip suffix
        else:
            logging.error("Filename doesn't end in json!")
        jsonData = json.load(open(filename))
        if 'paperId' not in jsonData:
            logging.error('No paper id!')
            continue
        paperID = jsonData['paperId']
        querySemanticScholarDetails(paperID, fn, "citations")
        querySemanticScholarDetails(paperID, fn, "references")
        time.sleep(1)

def parseCitationsReferences():
    """
    We've downloaded lots of -citations.json and -references.json files for our papers.
    Now let's parse these out into citations in our graph format.
    """
    filenames = glob("../data/texts/json/semanticScholar/*.json")
    for filename in filenames:
        if filename.endswith('-citations.json'):
            # We have details for this one
            referencesFn = filename.replace('-citations.json', '-references.json')
            baseFn = filename.replace('-citations.json', '.json')
            baseName = os.path.basename(baseFn).replace('.json', '')
            try:
                with open(filename) as f:
                    citationsData = json.load(f)
                with open(referencesFn) as f:
                    referencesData = json.load(f)
                with open(baseFn) as f:
                    baseData = json.load(f)
            except FileNotFoundError as e:
                logging.error(f"Can't open one or more files! {e}")
                continue
            citingPapers = [paper['citingPaper']['paperId'] for paper in citationsData['data']]
            referencesPapers = [paper['citedPaper']['paperId'] for paper in referencesData['data']]
            cites = cito['cites']
            for citingPaper in citingPapers:
                g.add((deText[citingPaper], cito['cites'], deText[baseName]))
            for referencePaper in referencesPapers:
                g.add((deText[baseName], cito['cites'], deText[referencePaper]))
    out = g.serialize(format="turtle")
    print(out)
    outFn = "../data/citationsAndReferences.ttl"
    with open(outFn, 'w') as f:
        f.write(out)
    logging.info(f"Wrote to {outFn}")





if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    # main()
    # getSemanticScholarDetails()
    parseCitationsReferences()

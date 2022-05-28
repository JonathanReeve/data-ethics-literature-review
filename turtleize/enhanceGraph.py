#!/usr/bin/env python3

"""
So we've built a graph from our initial spreadsheet, and now we want to
gather additional information from the semantic web, and add it to the graph.

"""

from rdflib.namespace import DC, DCTERMS, FOAF, RDF, OWL
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib import Namespace
import logging
import rdflib
import toRDF
from os.path import exists

g = rdflib.Graph()

g.load('../data/courses.ttl', format="ttl")

base = 'https://data-ethics.net'
ccso = Namespace('https://w3id.org/ccso/ccso/')
de = Namespace(base + '/')
dePerson = Namespace(f'{base}/person/')
deCourse = Namespace(f'{base}/course/')
deText = Namespace(f'{base}/text/')
deUniversity = Namespace(f'{base}/university/')
g.bind('ccso', ccso)
g.bind('de', de)
g.bind('dePerson', dePerson)
g.bind('deCourse', deCourse)
g.bind('deText', deText)
g.bind('deUniversity', deUniversity)

# 1. Query for universities that have sameAs wikidata
# 2. Download Wikidata as TTL
# 3. Get latitude and longitude and add it to our graph
# 4. Get country of origin and add it to our graph


# 1. Find courses that have syllabi

coursesWithSyllabi = g.query("""
    select distinct ?id ?uri where {
        ?id a ccso:Course .
        ?id ccso:hasSyllabus ?uri .
    }""")
# for line in coursesWithSyllabi:
#     print(line)

# 2. Manually extract references from syllabi (see issue #23)

# 3. Now we have turtle files for each course, e.g., data/texts/ttl/101.ttl
# 4. Let's add all the texts from each of those turtle files to our main
# courses.ttl graph.

for courseID, syllabus in coursesWithSyllabi:
    logging.info(f"Course ID: {courseID}")
    logging.info(f"Syllabus URL: {syllabus}")
    courseIDStr = str(courseID).split('/')[-1]
    fn = f"../data/texts/ttl/{courseIDStr}.ttl"
    if exists(fn):
        logging.info(f"Adding texts for course {courseIDStr}")
        with open(fn, encoding='utf-8') as f:
            textRDF = f.read()
        textGraph = Graph()
        textGraph.parse(data=textRDF, format='turtle')
        zotNS = Namespace("http://www.zotero.org/namespaces/export#")
        textGraph.bind('z', zotNS)
        textIDs = textGraph.query("""select distinct ?id where { ?id a z:UserItem . }""")
        numTextsFound = len(textIDs)
        if numTextsFound == 0:
            logging.error(f"Found zero texts in file {fn}. This doesn't sound right.")
            exit()
        else:
            logging.info(f"Found {len(textIDs)} texts in file {fn}. Adding to graph.")
        for textID in textIDs:
            # Rdflib seems to automatically prepend the local location of my code
            # So we have to take it apart and put it back together again.
            logging.info(f"Text: {textID[0]}")
            textID = deText[textID[0].toPython().split('/')[-1]]
            logging.info(f"Adding text with id {textID}")
            g.add((courseID, ccso.hasLM, textID))
    else:
        logging.info(f"No bibliography found for course {courseIDStr} at path {fn}")
    newGraph = g.serialize(format="turtle").decode("utf-8")
    with open('newgraph.ttl', 'w') as f:
        f.write(newGraph)

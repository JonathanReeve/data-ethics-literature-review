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

base = 'https://data-ethics.tech'
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
for line in coursesWithSyllabi:
    print(line)

# 2. Download those syllabi
# 3. Add syllabus readings to graph

for courseID, syllabus in coursesWithSyllabi:
    logging.info(f"Course ID: {courseID}")
    logging.info(f"Syllabus URL: {syllabus}")
    courseIDStr = str(courseID).split('/')[-1]
    if exists(f"../data/texts/bib/{courseIDStr}.texts.txt.bib"):
        logging.info(f"Adding texts for course {courseIDStr}")

    else:
        logging.info(f"No bibliography found for course {courseIDStr}")
    try:
        textIDs = toRDF.processSyllabus(str(syllabus), courseIDStr)
        logging.info(f"Found texts: {textIDs}")
        # answer = input('Continue? (Y/N): ')
        # if answer in ["n", "N", "no"]:
        #     exit()
        for textID in textIDs:
            g.add((courseID, ccso.hasLM, deText[str(textID)]))
        # answer = input('Write out graph? : ')
        # if answer in ["n", "N", "no"]:
        #     exit()
    except:
        logging.error(f"Something went wrong while processing syllabus {syllabus}.")
    newGraph = g.serialize(format="turtle").decode("utf-8")
    with open('graph.ttl', 'w') as f:
        f.write(newGraph)

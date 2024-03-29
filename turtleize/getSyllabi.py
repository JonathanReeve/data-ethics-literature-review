#!/usr/bin/env python3

"""
Just download syllabi to /syllabi.

"""

from rdflib.namespace import DC, DCTERMS, FOAF, RDF, OWL
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib import Namespace
import logging
import rdflib
import toRDF

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

# 2. Download those syllabi

for courseID, syllabus in coursesWithSyllabi:
    logging.info(f"Course ID: {courseID}")
    logging.info(f"Syllabus URL: {syllabus}")
    courseIDStr = str(courseID).split('/')[-1]
    courseIDInt = int(courseIDStr)
    url = str(syllabus)
    destDir = f"../syllabi/"
    if int(courseIDInt) < 100: # My allotment
        toRDF.downloadFile(url, destDir, courseIDInt)

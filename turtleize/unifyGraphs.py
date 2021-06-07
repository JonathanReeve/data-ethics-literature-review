#!/usr/bin/env python3

"""
Ok so we have turtle files for each course, containing texts with zotero IDs.
We need to add these to our courses.ttl graph, to make one giant graph.
"""

from rdflib.namespace import DC, DCTERMS, FOAF, RDF, OWL
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib import Namespace
import rdflib
import requests
import logging
import json
from glob import glob

g = Graph()


# Namespace stuff
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



# g.load('../data/courses.ttl', format='turtle')

allTexts = Graph()
for textGraph in glob('../data/texts/ttl/*.ttl'):
    allTexts.load(textGraph,
                  publicID=URIRef(deText), # this is the magic
                  format='turtle')

allTexts.load('../data/courses.ttl', format='turtle')

allTexts.serialize('graph.ttl', format='turtle')

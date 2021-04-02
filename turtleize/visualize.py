#!/usr/bin/env python3

"""
Visualize some of the graph.

"""
import rdflib
from rdflib import Graph
from rdflib.namespace import DC, DCTERMS, FOAF, RDF, OWL
from rdflib import Namespace
from rdflib.tools.rdf2dot import rdf2dot
import dominate
from dominate.tags import div, script, style
from dominate.util import raw
import json
from pyvis.network import Network

g = Graph()
g.parse("../data/courses.ttl", format="ttl")

# Get subgraph for testing purposes

wikidata = Namespace('https://wikidata.org/wiki/')
ccso = Namespace('https://w3id.org/ccso/ccso/')
de = Namespace('https://data-ethics.org/')

g.bind("foaf", FOAF)
g.bind('ccso', ccso)
g.bind('wikidata', wikidata)
g.bind('owl', OWL)
g.bind('de', de)

def getCourseUni():
    """
    Visualize course-university pairs.
    """
    courseUniPairs = g.query("""
        select distinct ?name ?uniName where {
            ?a a ccso:Course .
            ?a ccso:csName ?name .
            ?a ccso:offeredBy ?dept .
            ?dept ccso:memberOf ?uni .
            ?uni ccso:legalName ?uniName .
        }""")

    for line in courseUniPairs:
        print(line)

    net = Network(height='750px', width='100%')

    for course, uni in courseUniPairs:
        net.add_node(course, shape='square', label=str(course))
        net.add_node(uni, shape='circle', label=str(uni))
        net.add_edge(course, uni, title="hasCourse")

    net.show('../public/graph-vis.html')

def getCountryUniCourse():
    """
    Make a country-university-course graph.
    TODO
    """
    countryUniCourse = g.query("""
        select distinct ?name ?uniName where {
            ?a a ccso:Course .
            ?a ccso:csName ?name .
            ?a ccso:offeredBy ?dept .
            ?dept ccso:memberOf ?uni .
            ?uni ccso:legalName ?uniName .
        }""")

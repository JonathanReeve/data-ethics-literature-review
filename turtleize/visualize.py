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
g.parse("../data/coursesAndTexts.ttl", format="ttl")

# Get subgraph for testing purposes

# wikidata = Namespace('https://wikidata.org/wiki/')
# ccso = Namespace('https://w3id.org/ccso/ccso/')
# de = Namespace('https://data-ethics.org/')

# g.bind("foaf", FOAF)
# g.bind('ccso', ccso)
# g.bind('wikidata', wikidata)
# g.bind('owl', OWL)
# g.bind('de', de)

def getCourseUni():
    """
    Visualize course-university pairs.
    """
    courseUniPairs = g.query("""
        select distinct ?name ?uniName where {
            ?a a ccso:Course .
            ?a ccso:csName ?name .
            ?a ccso:offeredBy ?dept .
            ?dept ccso:belongsTo ?uni .
            ?uni ccso:legalName ?uniName .
        }""")

    for line in courseUniPairs:
        print(line)

    net = Network(height='750px', width='100%')

    for course, uni in courseUniPairs:
        net.add_node(course, shape='square', label=str(course))
        net.add_node(uni, shape='circle', label=str(uni))
        net.add_edge(course, uni, title="hasCourse")

    net.show('../website/graph-vis.html')

def getCourseText():
    """
    Visualize courses and their assigned texts.
    """
    coursesAndTexts = g.query("""
        select distinct ?courseName ?textTitle ?authorLast where {
            ?a a ccso:Course .
            ?a ccso:csName ?courseName .
            ?a ccso:hasLM ?t .
            ?t res:resource ?doc .
            ?doc dcterms:title ?textTitle .
            ?doc dcterms:creator ?author .
            ?author foaf:surname ?authorLast .
        } limit 50""")

    for line in coursesAndTexts:
        print(line)

    net = Network(height='750px', width='100%')

    for courseName, textTitle, authorLast in coursesAndTexts:
        net.add_node(courseName, shape='square', title=str(courseName))
        net.add_node(textTitle, shape='circle',
                     label=str(authorLast),
                     title=str(textTitle))
        net.add_edge(courseName, textTitle, title="hasLM")

    net.save_graph('../website/graph-viz.html')
    # net.show('../website/graph-vis.html')

def getCourseText2():
    """
    Visualize courses and their assigned texts.
    """
    coursesAndTexts = g.query("""
        select distinct ?courseName ?textTitle ?authorLast where {
            ?a a ccso:Course .
            ?a ccso:csName ?courseName .
            ?a ccso:hasLM ?t .
            ?t res:resource ?doc .
            ?doc dcterms:title ?textTitle .
            ?doc dcterms:creator ?author .
            ?author foaf:surname ?authorLast .
        } limit 50""")

    for line in coursesAndTexts:
        print(line)

    net = Network(height='750px', width='100%')

    for courseName, textTitle, authorLast in coursesAndTexts:
        net.add_node(courseName, shape='square', title=str(courseName))
        net.add_node(textTitle, shape='circle',
                     label=str(authorLast),
                     title=str(textTitle))
        net.add_edge(courseName, textTitle, title="hasLM")

    out = ""
    nodesJson = json.dumps(net.nodes)

    edgesJson = json.dumps(net.edges)

    template = f"""
    nodes = new vis.DataSet({nodesJson})
    edges = new vis.DataSet({edgesJson})
    data = {{nodes: nodes, edges: edges}};
    """

    print(template)

    net.save_graph('../website/graph-viz.html')
    # net.show('../website/graph-vis.html')

getCourseText2()

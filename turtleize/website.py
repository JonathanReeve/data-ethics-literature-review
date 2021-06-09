"""
Create a website from our graph.
We use dominate: https://github.com/Knio/dominate
to quasi-manually code it.
"""
from flask import Flask

import dominate
from dominate.tags import html, head, header, div, section, link, meta, body, h2, span, li, ul, script, a
from rdflib.namespace import DC, DCTERMS, FOAF, RDF, OWL
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib import Namespace
import logging
import rdflib
import toRDF
import json
from pyvis.network import Network

g = rdflib.Graph()
g.load('../data/coursesAndTexts.ttl', format="ttl")

def getCourseText():
    """
    Make a pyvis network for our graph.
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

    return net



def formatVisualization(net):
    """
    Takes a pyvis network and formats it using our own custom template.
    """
    nodesJson = json.dumps(net.nodes)
    edgesJson = json.dumps(net.edges)

    return f"""
    nodes = new vis.DataSet({nodesJson})
    edges = new vis.DataSet({edgesJson})
    data = {{nodes: nodes, edges: edges}};
    """

def uniCourseList():
    """
    Make a dictionary of universities and their courses.
    """
    results = g.query("""
        select distinct ?courseName ?instructorFN ?instructorGN ?university where {
            ?id a ccso:Course .
            ?id ccso:csName ?courseName .
            ?id ccso:hasInstructor ?inst .
            ?inst foaf:familyName ?instructorFN .
            ?inst foaf:givenName ?instructorGN .
            ?id ccso:offeredBy ?dept .
            ?dept ccso:belongsTo ?uni .
            ?uni ccso:legalName ?university .
        }""")

    # Build up a dictionary with universities as keys,
    # and courses as a list of values
    byUniversity = {}
    for line in results:
        # print(line)
        courseName, instFN, instGN, university = line
        if university in byUniversity:
            byUniversity[university].append((courseName, instFN, instGN))
        else:
            byUniversity[university] = [(courseName, instFN, instGN)]
    return byUniversity

def courseList(data):
    """ Make an HTML course listing from the university/course dictionary
    created above."""
    uniList = ul(cls="universities")
    for uni in data:
        courses = data[uni]
        uniLi = uniList.add(li(uni, cls="university"))
        courseList = uniLi.add(ul(cls="courseList"))
        for course in courses:
            courseName, instFN, instGN = course
            name = f"{instGN} {instFN}"
            courseList.add(li(span(courseName, cls="courseName"),
                        span(", "),
                        span(name, cls="instName"),
                        cls="course"))
    return uniList

def head_(jsData):
    """ The HTML <head> contents. Inserts the jsData. """
    # framework = "https://cdn.jsdelivr.net/npm/bulma@0.9.2/css/bulma.min.css"
    framework = "https://unpkg.com/spectre.css/dist/spectre.min.css"
    return (meta(charset='UTF-8'),
            meta(name='viewport',
                 content='width=device-width',
                 initialScale=1.0),
            link(href=framework,
                 rel="stylesheet",
                 type="text/css"),
            link(rel="stylesheet",
                 href="https://cdnjs.cloudflare.com/ajax/libs/vis/4.16.1/vis.css",
                 type="text/css"),
            script(type="text/javascript",
                   src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.16.1/vis-network.min.js"),
            script(jsData))


def body_(contents):
    """ The HTML <body> contents """
    return div(div(div(topNav(),
                       h2("Courses by University"),
                       contents,
                       class_="column col-12"),
                   class_="columns"),
               class_="container", style="width: 55em; margin: 0 auto;")


def routeURL(route):
    """ Translate /about to /about/index.html """
    return route + "/index.html"


def topNav():
    """ The top navigation area of the webpage. """

    def navbarItem(cont, targ):
        """ An individual navigation item"""
        return a(cont, href=targ, _class="btn btn-link")

    out = header(section(a("Data Ethics", href="/", class_="navbar-brand"),
                         # Generate navbar items from site map
                         *[navbarItem(label, routeURL(route)) for label, route in siteMap.items()],
                         _class="navbar-section"),
                 _class="navbar")
    return out


courseListHtml = courseList(uniCourseList())

siteMap = {"About": "/about",
           "Uni-Course": "/uni-course",
           "Course-Text":  "/course-text",
           "Text-Text": "/text-text"}

doc = dominate.document(title="Courses and Texts")

visData = formatVisualization(getCourseText())

for tag in head_(visData):
    doc.head.add(tag)

doc.body.add(body_(courseListHtml))

rendered = doc.render()

fn = '../website/index.html'
with open(fn, 'w') as outfile:
    outfile.write(rendered)
    logging.info(f"Wrote to {fn}")

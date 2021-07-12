"""
Create a website from our graph.
We use dominate: https://github.com/Knio/dominate
to quasi-manually code it.
"""
from flask import Flask

import dominate
from dominate.tags import html, head, header, div, section, link, meta, body, h2, span, li, ul, script, a, base
from dominate.util import raw
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

WEBSITE_LOCATION = "../website"

visOptions = {"configure": {"enabled": False},
                "edges": {"color": {"inherit": True},
                        "smooth": {"enabled": False, "type": "continuous"}
                        },
                "interaction": {"dragNodes": True, "hideEdgesOnDrag": False, "hideNodesOnDrag": False},
                "physics": {"enabled": True, "stabilization": {
                    "enabled": True,
                    "fit": True,
                    "iterations": 1000,
                    "onlyDynamicEdges": False,
                    "updateInterval": 50}}}


def makeGraph(results):
    """ Convert results of SPARQL query to a NetworkX graph. """
    net = Network(height='750px', width='100%')

    for subj, verb, obj in results:
        net.add_node(subj, shape='square', title=str(subj))
        net.add_node(verb, shape='circle',
                     label=str(obj),
                     title=str(verb))
        net.add_edge(subj, verb, title="hasCourse")
    return net


def getCourseTextGraph():
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
        } limit 100""")

    # for line in coursesAndTexts:
    #     print(line)

    return makeGraph(net)


def formatVisData(net):
    """
    Takes a pyvis network and formats it using our own custom template.
    """
    nodesJson = json.dumps(net.nodes)
    edgesJson = json.dumps(net.edges)
    options = json.dumps(visOptions)

    return f"""
    nodes = new vis.DataSet({nodesJson})
    edges = new vis.DataSet({edgesJson})
    data = {{nodes: nodes, edges: edges}};
    options = {options}
    container = document.getElementById('mynetwork');
    """ + """
    network = new vis.Network(container, data, options);

    network.on("stabilizationProgress", function(params) {
        document.getElementById('loadingBar').removeAttribute("style");
        var maxWidth = 496;
        var minWidth = 20;
        var widthFactor = params.iterations/params.total;
        var width = Math.max(minWidth,maxWidth * widthFactor);

        document.getElementById('bar').style.width = width + 'px';
        document.getElementById('text').innerHTML = Math.round(widthFactor*100) + '%';
    });
    network.once("stabilizationIterationsDone", function() {
        document.getElementById('text').innerHTML = '100%';
        document.getElementById('bar').style.width = '496px';
        document.getElementById('loadingBar').style.opacity = 0;
        // really clean the dom element
        setTimeout(function () {document.getElementById('loadingBar').style.display = 'none';}, 500);
    });
    """

def getUniCourseGraph():
    """
    Get university-course graph.
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

    return makeGraph(results)

def uniCourseList():
    """
    Make a list of universities and their courses.
    """
    uniCourseGraph = getUniCourseGraph()

    # Build up a dictionary with universities as keys,
    # and courses as a list of values
    byUniversity = {}
    for line in uniCourseGraph:
        # print(line)
        courseName, instFN, instGN, university = line
        if university in byUniversity:
            byUniversity[university].append((courseName, instFN, instGN))
        else:
            byUniversity[university] = [(courseName, instFN, instGN)]

    uniList = ul(cls="universities")
    for uni in byUniversity:
        courses = byUniversity[uni]
        uniLi = uniList.add(li(uni, cls="university"))
        courseList = uniLi.add(ul(cls="courseList"))
        for course in courses:
            courseName, instFN, instGN = course
            name = f"{instGN} {instFN}"
            courseList.add(li(span(courseName, cls="courseName"),
                        span(", "),
                        span(name, cls="instName"),
                        cls="course"))
    return h2("Courses by University"), uniList

def uniCourseContent():
    """
    Make a list of universities and their courses.
    """
    container = div(id="mynetwork")
    loadingBar = div(div(div("0%", id="text"), div(div(id="bar"), id="border"), _class="outerBorder"), id="loadingBar")
    return (container, loadingBar, uniCourseList())

siteMap = {"About": "about",
           "Uni-Course": "uniCourse",
           "Course-Text": "courseText",
           "Text-Text": "textText"}

class WebPage():
    """ An object to make web pages, given names, slugs, and content."""
    def __init__(self, name, slug, content, scriptData, siteMap=siteMap):
        self.name = name
        self.slug = slug
        self.content = content
        self.siteMap = siteMap
        self.scriptData = scriptData
        self.makePage(label=name, slug=slug, content=content, scriptData=scriptData)

    def head_(self, jsData=""):
        """ The HTML <head> contents. Inserts the jsData. """
        framework = "https://unpkg.com/spectre.css/dist/spectre.min.css"
        visCSS = "https://cdnjs.cloudflare.com/ajax/libs/vis/4.16.1/vis.css"

        def css(href):
            return link(rel="stylesheet", href=href, type="text/css")

        stylesheets = [framework, visCSS, "/style.css"]

        return (meta(charset='UTF-8'),
                meta(name='viewport',
                     content='width=device-width',
                     initialScale=1.0),
                base(href="/"),
                *[css(url) for url in stylesheets],
                script(type="text/javascript",
                       src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.16.1/vis-network.min.js"))

    def navbarItem(self, name, slug):
        """ An individual navigation item for the top nav."""
        slugFormatted = f"/{slug}/"
        buttonClass = "btn btn-link"
        if slug == self.slug:
            buttonClass += " active"
        return a(name, href=slugFormatted, _class=buttonClass)

    def topNav(self):
        """ The top navigation area of the webpage. """
        out = header(section(a("Data Ethics", href="/", _class="navbar-brand"),
                             # Generate navbar items from site map
                             *[self.navbarItem(name, slug)
                               for name, slug in self.siteMap.items()],
                             _class="navbar-section"),
                    _class="navbar")
        return out

    def body_(self, contents, scriptData=""):
        """ The HTML <body> contents """
        return (div(self.topNav(),
                   div(div(contents,
                           _class="column col-12"),
                       _class="columns"),
                   _class="container", style="width: 55em; margin: 0 auto;"),
                script(raw(scriptData)))

    def makePage(self, label, slug, content, scriptData=""):
        doc = dominate.document(title=f"Data Ethics: {label}")
        doc.head.add(self.head_())
        doc.body.add(self.body_(content, scriptData))
        fn = f"{WEBSITE_LOCATION}/{slug}/index.html"
        rendered = doc.render()
        with open(fn, 'w') as outfile:
            outfile.write(rendered)
            logging.info(f"Wrote to {fn}")



print(type(uniCourseContent()))

uniCourse = WebPage("Uni-Course", "uniCourse", uniCourseContent(), formatVisData(getUniCourseGraph()))
uniCourse = WebPage("Course-Text", "courseText", courseTextContent(), formatVisData(getCourseText()))

"""
Create a website from our graph.
We use dominate: https://github.com/Knio/dominate
to quasi-manually code it.
"""
from flask import Flask

import dominate
from dominate.tags import html, head, header, div, section, link, meta, body, h2, h3, span, li, ul, script, a, base, p, pre
from dominate.util import raw
from rdflib.namespace import DC, DCTERMS, FOAF, RDF, OWL
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib import Namespace
import logging
import rdflib
import toRDF
import json
import os
import textwrap
from pyvis.network import Network
import networkx as nx

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



def getCourseTextGraph():
    """
    Make a pyvis network for our graph.
    """
    coursesAndTexts = g.query("""
        select distinct ?courseID ?courseName ?textTitle ?authorLast where {
            ?courseID a ccso:Course .
            ?courseID ccso:csName ?courseName .
            ?courseID ccso:hasLM ?textID .
            ?textID res:resource ?doc .
            ?doc dcterms:title ?textTitle .
            ?doc dcterms:creator ?author .
            ?author foaf:surname ?authorLast .
        } """)

    net = Network(height='750px', width='100%')
    nxGraph = nx.Graph()

    for courseID, courseName, textTitle, authorLast in coursesAndTexts:
        if len(courseName) > 10:
            courseNameTruncated = courseName[:10] + "..."
        else:
            courseNameTruncated = courseName
        textFormatted = pre('\n'.join(textwrap.wrap(f"{authorLast}, {textTitle}", width=30))).render()
        nxGraph.add_node(courseID)
        net.add_node(courseID, shape='dot', mass=3,
                     label=courseNameTruncated, title=courseName, color="#e07678")
        nxGraph.add_node(authorLast)
        net.add_node(authorLast, shape='square', mass=4, title=textFormatted)
        net.add_edge(courseID, authorLast)
        nxGraph.add_edge(courseID, authorLast)

    return nxGraph, net


def getUniCourseGraph():
    """
    Get university-course graph.
    """
    results = g.query("""
        select distinct ?courseID ?courseName ?instructorFN ?instructorGN ?university where {
            ?courseID a ccso:Course .
            ?courseID ccso:csName ?courseName .
            ?courseID ccso:hasInstructor ?inst .
            ?inst foaf:familyName ?instructorFN .
            ?inst foaf:givenName ?instructorGN .
            ?courseID ccso:offeredBy ?dept .
            ?dept ccso:belongsTo ?uni .
            ?uni ccso:legalName ?university .
        }""")


    visGraph = Network(height='750px', width='100%') # PyVis-Network, for visualization.
    nxGraph = nx.Graph() # NetworkX, for analyses

    for courseID, courseName, instLast, instFirst, uni in results:
        instName = f"{instFirst} {instLast}"
        nxGraph.add_node(uni)
        visGraph.add_node(uni, shape='circle', title=uni, mass=3)
        nxGraph.add_node(courseID)
        visGraph.add_node(courseID, shape='box', label=courseName, mass=5)
        visGraph.add_edge(uni, courseID)
        nxGraph.add_edge(uni, courseID)
    return nxGraph, visGraph




def uniCourseList():
    """
    Make a list of universities and their courses.
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
        } limit 400""")

    # Build up a dictionary with universities as keys,
    # and courses as a list of values
    byUniversity = {}
    for courseName, instLast, instFirst, uni in results:
        # print(line)
        if uni in byUniversity:
            byUniversity[uni].append((courseName, instLast, instFirst))
        else:
            byUniversity[uni] = [(courseName, instLast, instFirst)]

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


def courseTextList():
    """
    TODO: A list a courses and their assigned texts.
    """
    return ""

def uniCourseContent(analysis):
    """
    Make a list of universities and their courses.
    """
    intro = div(h2("University-Course Graph"),
                p("This graph shows courses that teach data ethics, and the universities in which those courses are taught."),
                _class="intro")
    container = div(id="mynetwork")
    loadingBar = div(div(div("0%", id="text"), div(div(id="bar"), id="border"), _class="outerBorder"), id="loadingBar")
    return (intro, container, loadingBar, analysis, uniCourseList())


def courseTextContent(analysis):
    """
    Make a list of courses and their assigned texts.
    """
    intro = div(h2("Course-Text Graph"),
                p("This graph shows courses that teach data ethics, and the required texts scraped from those courses' syllabi."),
                _class="intro")
    container = div(id="mynetwork")
    loadingBar = div(div(div("0%", id="text"), div(div(id="bar"), id="border"), _class="outerBorder"), id="loadingBar")
    return (intro, container, loadingBar, analysis, courseTextList())


def indexContent():
    """
    The content of the main index.html file.
    """
    return div(h2("Welcome to Data Ethics"),
               p("""We map the burgeoning field of data ethics, an interdisciplinary area
               of study, spanning computer science, data science, statistics,
               and humanities disciplines. """)
               )

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
        out = header(section(a("Data Ethics", href="/",
                               _class="navbar-brand"),
                             _class="navbar-section"),
                     # Generate navbar items from site map
                     section(*[self.navbarItem(name, slug)
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
        if slug == "index":
            # We handle the main index page differently.
            fn = f"{WEBSITE_LOCATION}/index.html"
        else:
            # Everything else has a pretty url,
            # i.e., data-ethics.tech/courseText
            fn = f"{WEBSITE_LOCATION}/{slug}/index.html"
        rendered = doc.render()
        if not os.path.exists(os.path.dirname(fn)):
            try:
                os.makedirs(os.path.dirname(fn))
            except OSError as exc: # Guard against race condition
                exit(f"Error while writing file: {exc}")
        with open(fn, 'w') as outfile:
            outfile.write(rendered)
            logging.info(f"Wrote to {fn}")


class GraphAnalysis():
    """
    A class for holding graph objects, analyses, and the way they're formatted.
    """
    def __init__(self, nxGraph, visGraph):
        """
        Initialize
        """
        self.nxGraph = nxGraph
        self.visGraph = visGraph
        self.pageRank = nx.pagerank(nxGraph)
        self.degreeCentrality = nx.algorithms.centrality.degree_centrality(nxGraph)
        self.computeSize()
        # We should compute the page rank and update the graph before computing the JS data.
        self.webContent = self.webpageContent()
        self.js = self.formatVisData(visGraph)
        # self.kEdges = nx.k_edge_components(nxGraph, 4)

    def computeSize(self):
        """ Compute the size of nodes according to their connectedness. """
        for node in self.nxGraph.nodes():
            if 'course' in str(node):
                # Let's not compute sizes of courses for now
                size = 20
            else:
                nEdges = self.nxGraph.edges(node)
                size = 1 + len(nEdges) * 4
            self.visGraph.get_node(node)['size'] = size

    def formatPageRank(self):
        pageRankHtml = []
        sortedRanks = sorted(self.pageRank, key=self.pageRank.get, reverse=True)
        for node in sortedRanks:
            if 'course' in str(node):
                continue # Skip courses
            rank = self.pageRank[node]
            title = self.visGraph.get_node(node)['title'].replace('<pre>', '').replace('</pre>', '')
            lineItem = li(f"{title}: {rank}")
            pageRankHtml.append(lineItem)
        return pageRankHtml[:20]

    def formatKEdges(self):
        kEdges = []
        for edge in self.kEdges:
            lineItem = li(f"{edge}")
            kEdges.append(lineItem)
        return kEdges


        
    def formatVisData(self, net):
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

    def webpageContent(self):
        """
        Make some HTML for the webpage.
        """
        return div(
                 h2("Analysis"),
                 h3(f"Pagerank"),
                 p(self.formatPageRank()),
                 # p(self.formatKEdges()),
                 id="analysis")


index = WebPage("Index", "index", indexContent(), "")


nxGraph, visGraph = getUniCourseGraph()
uniCourseAnalysis = GraphAnalysis(nxGraph, visGraph)
uniCourse = WebPage("Uni-Course", "uniCourse",
                    uniCourseContent(uniCourseAnalysis.webpageContent()), uniCourseAnalysis.js)

nxGraph, visGraph = getCourseTextGraph()
courseTextAnalysis = GraphAnalysis(nxGraph, visGraph)
courseText = WebPage("Course-Text", "courseText",
                     courseTextContent(courseTextAnalysis.webpageContent()), courseTextAnalysis.js)

textText = WebPage("Text-Text", "textText", "Nothing here yet.", "")

import dominate
from dominate.tags import *

from rdflib.namespace import DC, DCTERMS, FOAF, RDF, OWL
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib import Namespace
import logging
import rdflib
import toRDF

g = rdflib.Graph()

g.load('../data/courses.ttl', format="ttl")


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

# print(byUniversity)

doc = dominate.document(title='Course List')

def scaffold(contents):
    return html(
        body(
            h2("Courses by University"),
            contents
            ))

def courseList(data):
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


print(scaffold(courseList(byUniversity)))

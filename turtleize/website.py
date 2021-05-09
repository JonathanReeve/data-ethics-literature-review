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
    out = ul([li(uni, ul(li(data[uni][0]))) for uni in data])
    return out

unis = [li(str(uni)) for uni in byUniversity]

print(scaffold(courseList(byUniversity)))

# print(scaffold(courseList(byUniversity)))

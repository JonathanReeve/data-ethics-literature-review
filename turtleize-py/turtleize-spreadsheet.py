#!/usr/bin/env python3

"""
This parses the Tech Ethics Curriculum spreadsheet CSV and attempts
to transform it into a Turtle RDF graph.

Usage: python turtleize-spreadsheet.py

"""

import pandas as pd
import rdflib
from rdflib.namespace import DC, DCTERMS, FOAF, RDF, OWL
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib import Namespace
import requests
import json

df = pd.read_csv('tech-ethics-courses.csv')

wikidata = Namespace('https://wikidata.org/wiki/')
ccso = Namespace('https://w3id.org/ccso/ccso/')
de = Namespace('https://data-ethics.org/')

def resolveUni(uni):
    """
    We have the name of a university, but we want to find its
    Wikipedia / Wikidata page. So we look it up on Wikidata.
    """
    params = {"action": "wbgetentities", "sites": "enwiki", "titles": uni,
              "languages": "en", "format": "json"}
    response = requests.get('http://www.wikidata.org/w/api.php?', params=params)
    if response.ok:
        decoded = json.loads(response.text)
        entityCode = list(decoded['entities'].keys())[0]
        return URIRef(wikidata + entityCode)

def toList(instructors):
    """
    Our list of instructors is a natural-language list,
    and we want to turn it into a Python list.
    """
    if type(instructors) != str:
        return [instructors]
    # Handle 'Inst A and Inst B'
    if ' and ' in instructors:
        instructors = instructors.replace(' and ', ', ')
    if ',' in instructors:
        return [inst.strip() for inst in instructors.split(',')]
    return [instructors]

g = Graph()

g.bind("foaf", FOAF)
g.bind('ccso', ccso)
g.bind('wikidata', wikidata)
g.bind('owl', OWL)
g.bind('de', de)

def cleanURL(url):
    if type(url) is not str:
        return None
    urlNormalized = url.lower().strip()
    if urlNormalized in ["", "not online", 'tbd', "not available online", "n/a (yet)"]:
        return None
    return url

def normalizeLevel(level):
    if level == '':
        return None
    if level is not str:
        return None
    return level

def cleanCode(code):
    code = str(code)
    if code == 'nan':
        return None
    return code

def urlEncode(text):
    if text is not str:
        text = str(text)
    return requests.utils.quote(text.lower().replace(' ', '-'))

def turtleize(i, row):
    ident =  URIRef(f'http://data-ethics.org/syllabi/{i}')
    g.add((ident, RDF.type, ccso.Course))
    # Syllabus
    syllabus = cleanURL(row['SYLLABUS '])
    if syllabus is not None:
        g.add((ident, ccso.hasSyllabus, URIRef(syllabus)))
    # Department
    uniNormalized = urlEncode(row['UNIVERSITY'])
    uni = URIRef(f'https://data-ethics.org/university/{uniNormalized}')
    # uniWikidata = resolveUni(row['UNIVERSITY'])
    dept = row['DEPARTMENT']
    deptNormalized = uni + '/department/' + urlEncode(dept)
    g.add((uni, RDF.type, ccso.University))
    # g.add((uni, OWL.sameAs, uniWikidata))
    g.add((ident, ccso.offeredBy, deptNormalized))
    g.add((deptNormalized, RDF.type, ccso.Department))
    g.add((deptNormalized, ccso.memberOf, uni))
    g.add((uni, ccso.legalName, Literal(row['UNIVERSITY'])))
    # Course Name
    g.add((ident, ccso.csName, Literal(row['COURSE TITLE'])))
    # Instructors
    # Handle multiple instructors
    instList = toList(row['INSTRUCTOR'])
    for inst in instList:
        instructor = Literal(inst)
        g.add((ident, ccso.hasInstructor, instructor))
        g.add((instructor, ccso.worksFor, uni))
    code = cleanCode(row['CODE'])
    if code is not None:
        g.add((ident, ccso.code, Literal(str(code))))
    level = normalizeLevel(row['LEVEL'])
    if level is not None:
        if level.lower() == 'graduate':
            g.add((ident, ccso.requiresProgram, ccso.Bachelor))
    desc = row['COURSE DESCRIPTION - URL']
    if cleanURL(desc) is not None:
        g.add((ident, ccso.description, URIRef(desc)))


for i, row in list(df.iterrows()):
    # print(resolveUni(row['UNIVERSITY']))
    turtleize(i, row)

print(g.serialize(format="turtle").decode("utf-8"))


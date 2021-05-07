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
import logging
from urlextract import URLExtract


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

def cleanURL(url):
    if type(url) != str:
        return None
    urlNormalized = url.lower().strip()
    if urlNormalized in ["", "not online", 'tbd', "not available online", "n/a (yet)"]:
        return None
    # Validate a URL by extracting it from the string
    extractor = URLExtract()
    urls = extractor.find_urls(url)
    if len(urls) == 0:
        return
    return urls[0]

def normalizeLevel(level):
    if level == '':
        return None
    if type(level) != str:
        return None
    level = level.lower()
    if 'undergraduate' in level:
        return "undergraduate"
    if 'graduate' in level:
        return "graduate"
    return level

def cleanCode(code):
    code = str(code)
    if code == 'nan':
        return None
    return code

def urlEncode(text):
    if type(text) != str:
        text = str(text)
    return requests.utils.quote(text.lower().replace(' ', '-'))

def lookupORCID(familyName, givenNames, uni):
    """
    Look up an ORCID, given name and affiliation of instructor.
    See API documentation here:
    https://info.orcid.org/documentation/api-tutorials/api-tutorial-searching-the-orcid-registry/#easy-faq-2532
    """
    baseURL = "https://pub.orcid.org/v3.0/search/"
    params = {"q": " AND ".join([f"family-name:{familyName}",
                                 f"given-names:{givenNames}",
                                 f"affiliation-org-name:{uni}"])
              }
    headers={"Content-Type": "application/json"}
    response = requests.get(baseURL, params=params, headers=headers)
    data = json.loads(response.text)
    if 'num-found' not in data:
        logging.error(f"Num-found not in data: {data}")
        return
    if data['num-found'] < 1:
        logging.error(f"Couldn't find ORCID for {familyName}, {givenNames}. Response text: {data}")
        return
    try:
        return data['result'][0]['orcid-identifier']['uri']
    except:
        logging.error(f"Couldn't extract ORCID from data: {data}")
        return

def turtleize(i, row):
    ident =  deCourse[str(i)]
    g.add((ident, RDF.type, ccso.Course))
    # Syllabus
    syllabus = cleanURL(row['SYLLABUS '])
    if syllabus is not None:
        g.add((ident, ccso.hasSyllabus, URIRef(syllabus)))
    # Department
    uniRaw = row['UNIVERSITY']
    uniNormalized = urlEncode(uniRaw)
    uni = deUniversity[uniNormalized]
    dept = row['DEPARTMENT']
    deptNormalized = uni + '/department/' + urlEncode(dept)
    g.add((uni, RDF.type, ccso.University))
    uniWikidata = resolveUni(row['UNIVERSITY'])
    g.add((uni, OWL.sameAs, uniWikidata))
    g.add((ident, ccso.offeredBy, deptNormalized))
    g.add((deptNormalized, RDF.type, ccso.Department))
    g.add((deptNormalized, ccso.belongsTo, uni))
    g.add((deptNormalized, ccso.legalName, Literal(dept)))
    g.add((uni, ccso.legalName, Literal(uniRaw)))
    # Course Name
    g.add((ident, ccso.csName, Literal(row['COURSE TITLE'])))
    # Instructors
    # Handle multiple instructors
    instList = toList(row['INSTRUCTOR'])
    for inst in instList:
        logging.debug(f"Processing instructor: {inst}")
        instructor = dePerson[urlEncode(inst)]
        g.add((ident, ccso.hasInstructor, instructor))
        g.add((instructor, ccso.worksFor, uni))
        # Now try to find resolve instructors to ORCIDs
        namesNormalized = normalizeName(inst)
        if namesNormalized is None:
            continue
        else:
            familyName, givenNames = namesNormalized
            g.add((instructor, foaf.familyName, Literal(familyName)))
            g.add((instructor, foaf.givenName, Literal(givenNames)))
        hasOrcid = URIRef("https://w3id.org/reproduceme#ORCID")
        orcid = lookupORCID(familyName, givenNames, uniRaw)
        if orcid is not None:
            g.add((instructor, hasOrcid, Literal(orcid)))
    code = cleanCode(row['CODE'])
    if code is not None:
        g.add((ident, ccso.code, Literal(str(code))))
    level = normalizeLevel(row['LEVEL'])
    if level is not None:
        if level == 'certificate':
            g.add((ident, ccso.includedIn, ccso.Certificate))
        if level == 'graduate':
            g.add((ident, ccso.requiresProgram, ccso.Bachelor))
            g.add((ident, ccso.includedIn, ccso.Master))
        if level in ['master', 'masters']:
            g.add((ident, ccso.requiresProgram, ccso.Bachelor))
            g.add((ident, ccso.includedIn, ccso.Master))
        if level in ['phd', 'ph.d.']:
            g.add((ident, ccso.requiresProgram, ccso.Bachelor))
            g.add((ident, ccso.requiresProgram, ccso.Master))
            g.add((ident, ccso.includedIn, ccso.Doctorate))
    language = normalizeLanguage(row['LANGUAGE'])
    if language is not None:
        # I don't know why language is a property of Syllabus, and not Course,
        # but let's just go with it.
        # g.add((URIRef(syllabus), ccso.language, Literal(language)))
        g.add((ident, ccso.language, Literal(language)))
    desc = row['COURSE DESCRIPTION - URL']
    if cleanURL(desc) is not None:
        g.add((ident, ccso.description, URIRef(desc)))
    additionalURLs = cleanURL(row['ADDITIONAL URLs'])
    if additionalURLs is not None:
        g.add((ident, ccso.courseURL, URIRef(additionalURLs)))
    subTopic = normalizeTopic(row["Sub-Topic"])
    if subTopic is not None:
        g.add((ident, ccso.coversTopic, Literal(subTopic)))
    # Not sure how to handle this one yet.
    # requirement = row['REQUIREMENT?']
    # notes = row['NOTES']

def normalizeTopic(topic):
    if type(topic) is not str:
        return None
    else:
        return topic

def normalizeLanguage(lang):
    """ There's certainly a better-practices way of doing this,
    but since all the courses appear to be in English, this will do for now.
    """
    if type(lang) is not str:
        return None
    if lang.lower() in ['english', 'eng']:
        return 'en'
    if lang.lower() in ['german', 'ger', 'de']:
        return 'de'
    if lang.lower() in ['french', 'francais', 'fr']:
        return 'fr'


def normalizeName(name):
    """
    Some names are written with titles or other irregularities.
    Let's try to normalize it, and return given / family names.
    """
    if type(name) != str:
        return
    name = name.strip()
    if name.lower() in ['various', 'other', 'varies', 'many']:
        return
    names = name.split()
    if len(names) < 2:
        print(f"Suspicious name: {name}, skipping.")
        return
    print(names)
    familyName, givenNames = name.split()[-1], name.split()[:-1]
    namesNotTitles = []
    for givenName in givenNames:
        titles = ["Mr", "Dr", "Ms", "Mrs", "Miss", "Rev"]
        titlesWithPeriods = [title + "." for title in titles]
        if givenName in titles or givenName in titlesWithPeriods:
            continue
        else:
            namesNotTitles.append(givenName)
    givenNamesClean = " ".join(namesNotTitles)
    return familyName, givenNamesClean



if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    df = pd.read_csv('tech-ethics-courses.csv')

    wikidata = Namespace('https://wikidata.org/wiki/')
    ccso = Namespace('https://w3id.org/ccso/ccso/')
    foaf = FOAF
    base = 'https://data-ethics.tech'
    de = Namespace(base + '/')
    dePerson = Namespace(f'{base}/person/')
    deCourse = Namespace(f'{base}/course/')
    deText = Namespace(f'{base}/text/')
    deUniversity = Namespace(f'{base}/university/')

    g = Graph()

    g.bind("foaf", FOAF)
    g.bind('ccso', ccso)
    g.bind('wikidata', wikidata)
    g.bind('owl', OWL)
    g.bind('de', de)
    g.bind('dePerson', dePerson)
    g.bind('deCourse', deCourse)
    g.bind('deText', deText)
    g.bind('deUniversity', deUniversity)

    for i, row in list(df.iterrows()):
        # print(resolveUni(row['UNIVERSITY']))
        turtleize(i, row)

    print(g.serialize(format="turtle").decode("utf-8"))

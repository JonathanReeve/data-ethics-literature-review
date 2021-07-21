
from rdflib.namespace import DC, DCTERMS, FOAF, RDF, OWL
from rdflib import Graph
from rdflib import URIRef, BNode, Literal
from rdflib import Namespace
import rdflib
import click
import sys
import requests
import logging
import json
import semanticscholar as sch

#an example using semantic scholar API with given DOI

paper = sch.paper('10.1007/s13347-016-0251-1', timeout=2)
paper.keys()
paper['title']
paper['authors']
paper['abstract']


#to read the file
turtleFile = "/Users/zhuohan/Desktop/temp/data/coursesAndTexts.ttl"

#my semantic scholar function. Based on given DOI, it can return title, author and abstract

def querySemanticScholar(DOI,title = None, author=None):
    for i in DOI:

        paper = sch.paper(i)
        title_str = paper['title']
        author_str = paper['authors']
        abstract = paper['abstract']
        topic = paper['topics']
        year = paper['year']
        for author in paper['authors']:
            author_name = author['name']
            
        print ('Title: %s' %  title)
        print ('Author: %s' %  author_name)
        print ('Abstract: %s' %  abstract)
        print ('Topic: %s' %  topic)
        print ('Year: %s' %  year)

        #Add variables title, author to the graph
#         g.add((item, dcterms:title, title))
#         g.add((item, dcterms:creator, author))
    return (title_str, author_name, abstract, topic, year)


#revise main function

def main():
    g = rdflib.Graph()
    g.load(turtleFile, format="ttl")
    # for item in g:
    #     print(item)
    g.bind('z', 'http://www.zotero.org/namespaces/export#')
    g.bind('dcterms', 'http://purl.org/dc/terms/')
    g.bind('foaf', 'http://xmlns.com/foaf/0.1/')
    # This only works if we have the title and author.
    # data = g.query("""select distinct ?id ?title ?authorFirst ?authorLast where {
    #     ?id a z:UserItem .
    #     ?id res:resource ?doc .
    #     ?doc dcterms:title ?title .
    #     ?doc dcterms:creator ?author .
    #     ?author foaf:givenName ?authorFirst .
    #     ?author foaf:surname ?authorLast .
    # }""")
    # itemID, title, authorFirst, authorLast = list(data)[0]
    # print(title, authorFirst, authorLast)
    # This will work even if we don't have an author
    data = g.query("""select distinct ?id ?title ?authorFirst ?authorLast ?DOI where {
        ?id a z:UserItem .
        ?id res:resource ?doc .
        ?doc dcterms:title ?title .
        ?doc bibo:doi ?DOI .
        OPTIONAL {
          ?doc dcterms:creator ?author .
          ?author foaf:givenName ?authorFirst .
          ?author foaf:surname ?authorLast .
          
        }
    }""")   
    resultsDict = {}
    for result in data:
        itemID, title, authorFirst, authorLast, DOI = result
        print(itemID, title, authorFirst, authorLast, DOI)
        if authorFirst is not None and authorLast is not None:
            author = f"{authorFirst} {authorLast}"
        else:
            author = None
        itemID = str(itemID)
        if itemID in resultsDict:
            continue # Only take the first one for each ID
        else:
            resultsDict[itemID] = DOI
    for itemID, titleAuthor in resultsDict.items():
        DOI = titleAuthor
        querySemanticScholar(DOI)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

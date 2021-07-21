
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
turtleFile = "../data/coursesAndTexts.ttl"

#my semantic scholar function. Based on given DOI, it can return title, author， abstract and citations
def SementicScholar():
    title = []
    author = []
    abstract = []
    cit_url = []
    for elem in range(0,len(data)):
        my_doi = str(list(data)[elem][4])
        #iid.append(str(list(data)[elem][0]))
        if my_doi[-1]=='.':
            clean_doi = my_doi[:-1]
            paper = sch.paper((clean_doi))
            if paper =={}:
                title.append({})
                abstract.append({})
                author.append({})
                cit_url.append({})
            else:    
                title.append(paper['title'])
                abstract.append(paper['abstract'])
                for aut in paper['authors']:
                    author.append(aut['name'])
                for c in paper['citations']:
                    cit_url.append(c['url'])
        else:
            paper = sch.paper((my_doi))
            if paper =={}:
                title.append({})
                abstract.append({})
                author.append({})
                cit_url.append({})
            else:    
                title.append(paper['title'])
                abstract.append(paper['abstract'])
                for aut in paper['authors']:
                    author.append(aut['name'])
                for c in paper['citations']:
                    cit_url.append(c['url'])
    return(title, author, abstract, cit_url)
            

#revised main function
def main():
    g = rdflib.Graph()
    g.load(turtleFile, format="ttl")
    # for item in g:
    #     print(item)
    g.bind('z', 'http://www.zotero.org/namespaces/export#')
    g.bind('dcterms', 'http://purl.org/dc/terms/')
    g.bind('foaf', 'http://xmlns.com/foaf/0.1/')
    g.bind('cito','http://purl.org/spar/cito')
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
            resultsDict[itemID] = (DOI, title, author)
    for itemID, titleAuthor in resultsDict.items():
        DOI, title, author = titleAuthor
    (v1,v2,v3,v4) = SementicScholar()#title, author, abstract, citation
    
    #To add variables to the graph
    from rdflib import URIRef
    from rdflib import Literal
    print("item id is", itemID)
    #url to rdflib
    uitemID = URIRef(itemID)
    
    g.add((uitemID, URIRef('http://purl.org/dc/terms/title'), Literal(v1)))
    g.add((uitemID, URIRef('http://purl.org/dc/terms/abstract'), Literal(v3)))
#   Direct form for a citation
#     uitemID cito:extends Literal(v3) .        

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()

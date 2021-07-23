# My main function for querying Arxiv
# My main
from rdflib import URIRef
from rdflib import Literal
def main():
    g = rdflib.Graph()
    g.load(turtleFile, format="ttl")
    #    for item in g:
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
    data = g.query("""select distinct ?id ?title ?authorFirst ?authorLast where {
        ?id a z:UserItem .
        ?id res:resource ?doc .
        ?doc dcterms:title ?title .
        OPTIONAL {
          ?doc dcterms:creator ?author .
          ?author foaf:givenName ?authorFirst .
          ?author foaf:surname ?authorLast .
        }
    }""")
    resultsDict = {}
    for result in data:
        itemID, title, authorFirst, authorLast = result
        print(itemID, title, authorFirst, authorLast)
        if authorFirst is not None and authorLast is not None:
            author = f"{authorFirst} {authorLast}"
        else:
            author = None
        itemID = str(itemID)
        if itemID in resultsDict:
            continue # Only take the first one for each ID
        else:
            resultsDict[itemID] = (title, author)
    for itemID, titleAuthor in resultsDict.items():
        title, author = titleAuthor
        print("orig title", title)
        # replace with my function
        ss = title.split()
        newstring=""
        for st in ss:
            st1 = ExtractAlphanumeric(st)
            newstring=newstring+st1+" "
        newstring=newstring[:-1]
        
        
        (t1, t2, t3, t4) = queryArxiv(newstring)# title, author, arxiv id, abstract
        
        if author != None:
            # query Author 
            aq = "select ?givenName ?surname where{ "
            aq = aq + author
            aq =aq + " a foaf:Person .} "
            
            qauthor = g.query(aq)
        
            print("qauthor ", quathor)
            (t1, t2, t3, t4) = queryArxiv(newstring, qauthor)
        
        
        
        print("item id is", itemID)
        # url to rdflib term : wrap in rdf (rdflib documentation)
        uitemID = URIRef(itemID)
        
        print("best title:", t1)
        print("best author:", t2) # dc terms creator
        #g.add((uitemID, "dcterms:title", t1))
        #g.add((uitemID, "dcterms:abstract", t4))
        g.add((uitemID, URIRef('http://purl.org/dc/terms/title'), Literal(t1))) #URIRef(t1)))
        g.add((uitemID, URIRef('http://purl.org/dc/terms/creator'), Literal(t2)))
        g.add((uitemID, URIRef('http://purl.org/dc/terms/abstract'), Literal(t4))) # URIRef(t4)))

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
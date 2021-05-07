import sys
import docker
import requests
from time import sleep
import json
import click
import re
from bs4 import BeautifulSoup

"""
Turn lots of things into RDF.
Use the Zotero Translation Server (https://github.com/zotero/translation-server)
via Docker to do most of it.

Usage:

$ python toRDF.py start

$ python toRDF.py url 'https://heinonline.org/HOL/LandingPage?handle=hein.journals/wflr49&div=16&id=&page='

$ python toRDF.py book "Weapons of Math Destruction"

$ python toRDF.py identifier 10.1177/2053951714559253
"""

@click.group()
def cli():
    """ Translate lots of book/article identifiers into RDF."""
    pass

@cli.command()
def start():
    """ Start the Zotero translation server in a Docker container."""
    client = docker.from_env()
    container = client.containers.run("zotero/translation-server",
                                    detach=True, ports={1969:1969}, tty=True,
                                    stdin_open=True)
    myContainer = [cont for cont in client.containers.list() if cont == container][0]
    while myContainer.status != 'running':
        print('Waiting for container to start...')
        sleep(1)
    click.echo(f"Container ID: {myContainer}")

@cli.command()
@click.argument('query', nargs=1)
def stop():
    """ Stop the Zotero translation server."""
    myContainer.stop()

def translateURL(url):
    """
    Get bibliographic information from a URL.
    """
    # print(f"Translating URL: {url}")
    response = requests.post("http://127.0.0.1:1969/web",
                            data=url,
                            headers={'Content-Type': 'text/plain'})
    if response.ok:
        response.encoding='utf-8'
        return response.text

def translateJSON(zoteroJSON):
    """
    Convert the JSON format that translateURL() returns into Bibliontology RDF.
    """
    response = requests.post('http://127.0.0.1:1969/export',
                             data=zoteroJSON,
                             params={"format": "rdf_bibliontology"},
                             headers={"Content-Type": "application/json"})
    if response.ok:
        return response.text

def ident2rdf(ident):
    """
    Translate an identifier to RDF, where that identifier is one of a DOI, ISBN, arXiv ID, etc.
    """
    response = requests.post('http://127.0.0.1:1969/search',
                             data=ident,
                             params={"format": "rdf_bibliontology"},
                             headers={"Content-Type": "text/plain"})
    zoteroJSON = response.text if response.ok else None
    try:
        decodedJSON = json.dumps(json.loads(zoteroJSON))
    except:
        print(f"Couldn't translate identifier: {ident}")
        print(zoteroJSON)
        return None
    return translateJSON(decodedJSON)


def url2rdf(url):
    """ Converts a URL to RDF/XML. """
    zoteroJSON = translateURL(url)
    try:
        decodedJSON = json.dumps(json.loads(zoteroJSON))
    except:
        print(f"Couldn't translate url: {url}")
        return None
    return translateJSON(decodedJSON)

def getSyllabus(url):
    # TODO: handle PDF syllabi
    if url.endswith('.pdf'):
        # 1. Download PDF
        # 2. Convert to text
        return # TODO
    elif url.endswith('.htm') or url.endswith('.html'):
        resp = requests.get(url)
        if resp.ok:
            return resp.text
        else:
            exit(f"Couldn't download syllabus html. Response: {resp.status}")
    else:
        exit(f"Unknown syllabus format: {url}")

def getURLs(html):
    soup = BeautifulSoup(html)
    links = soup.find_all('a')
    return [link.get('href') for link in links]

def processURLs(urls):
    allItemIDs = []
    if len(urls) > 0:
        for url in urls:
            print(f"Trying url: {url}")
            rdf = url2rdf(url)
            if rdf is not None:
                itemId = writeRDF(rdf)
                allItemIDs.append(itemId)
    print(formatIDs(allItemIDs))

def writeRDF(rdf):
    """ Write out the RDF to readings/<ID>.rdf.xml. """
    matches = re.finditer('<z:UserItem rdf:about="(.*?)">', rdf)
    itemIds = [match.group(1) for match in matches if match is not None]
    itemId = itemIds[0]
    fn = f"readings/{itemId}.rdf.xml"
    with open(fn, 'w') as f:
        f.write(rdf)
    print(f"Wrote {fn}")
    click.echo(rdf)
    return itemId

def formatIDs(itemList):
    """
    We have lots of zotero ids, and we want to turn these into links in RDF.
    """
    return f"""
    ccso:hasLM {" , ".join(itemList)} ;
    """

def getISBN(query):
    """ Query the Google Books API to get an ISBN for a book. """
    params = {"q": query}
    resp = requests.get('https://www.googleapis.com/books/v1/volumes', params=params)
    if resp.ok:
        data = json.loads(resp.text)
        firstItem = data.get('items')[0]
        isbns = [ident['identifier'] for ident in
                 firstItem['volumeInfo']['industryIdentifiers']
                 if ident['type']=='ISBN_13' or ident['type']=='ISBN_10']
        return max(isbns)
    else:
        print("Something went wrong with this query.")
        print(resp)

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
    return json.loads(response.text)




@cli.command()
@click.argument('URL', nargs=1)
def url(url):
    """Translate a URL to RDF,
    where the URL is a link to an article or book."""
    rdf = url2rdf(url)
    writeRDF(rdf)
    click.echo(rdf)


@cli.command()
@click.argument('ident', nargs=1)
def identifier(ident):
    """Translate a DOI, arXiv, or ISBN to RDF"""
    click.echo(ident2rdf(ident))

@cli.command()
@click.argument('URL', nargs=1)
def syllabus(url):
    """Download a syllabus from a URL, extract links from it,
    and create RDF from those links."""
    html = getSyllabus(url)
    links = getURLs(html)
    processURLs(links)

@cli.command()
@click.argument('query', nargs=1)
def book(query):
    """ Try to get RDF for a book, by title or similar query.
    Uses the Google Books API.
    """
    isbn = getISBN(query)
    print('ISBN: ', isbn)
    rdf = ident2rdf(isbn)
    click.echo(rdf)
    click.echo(writeRDF(rdf))



if __name__== "__main__":
    cli()
    # lookupORCID("johnson")

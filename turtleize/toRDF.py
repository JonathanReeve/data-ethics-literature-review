import sys
import os
import docker
import requests
from time import sleep
import json
import click
import re
from bs4 import BeautifulSoup
import logging
import pdftotext
from urlextract import URLExtract
from os.path import exists

"""
Turn lots of things into RDF.
Use the Zotero Translation Server (https://github.com/zotero/translation-server)
via Docker to do most of it.

Usage:

$ python toRDF.py start

$ python toRDF.py url 'https://heinonline.org/HOL/LandingPage?handle=hein.journals/wflr49&div=16&id=&page='

$ python toRDF.py book "Weapons of Math Destruction"

$ python toRDF.py identifier 10.1177/2053951714559253

$ python toRDF.py bibtex references.bib
"""

logging.basicConfig(level=logging.DEBUG)

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
        logging.info('Waiting for container to start...')
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

def bibtex2rdf(bibtexFile):
    """
    Convert a bibtex file into Bibliontology RDF.
    """
    response = requests.post('http://127.0.0.1:1969/import',
                             data=bibtexFile,
                             params={"format": "bibtex"},
                             headers={"Content-Type": "text/plain"})
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


def getPDFSyllabus(url, courseID):
    # Do we have it already?
    cacheFilename = f"../syllabi/{courseID}.pdf"
    if exists(cacheFilename):
        f = open(cacheFilename)
    else:
        f, content = downloadFile(url, '../syllabi', courseID)
    # Convert to text
    pdf = pdftotext.PDF(f)
    pdfText = "\n\n".join(pdf)
    f.close()
    return pdfText


def getHTMLSyllabus(url, courseID):
    """ Download a HTML syllabus."""
    # First see if we haven't already downloaded it.
    cacheFilename = f"../syllabi/{courseID}.html"
    isCacheFile = exists(cacheFilename)
    if isCacheFile: # We already have it. Use the cached version
        with open(cacheFilename) as f:
            return f.read()
    else:
        # Download HTML syllabus.
        resp = requests.get(url)
        if resp.ok:
            syllabusHtml = resp.text
            with open(cacheFilename, 'w') as f:
                f.write(syllabusHtml)
            return resp.text
        else:
            logging.error(f"Couldn't download syllabus html. Response: {resp.status_code}")
            return


def getDocSyllabus(url):
    # TODO
    logging.error("Docx syllabi not handled yet")
    return


def downloadFile(url, destDir, courseID):
    """ Download a file from the interwebs, and
    save it to the destination directory.
    Returns file handle and content."""
    # First, do we have this already?
    fn = url.split('/')[-1]
    ext = fn.split('.')[-1] # Maintain file extension
    if ext not in ['.pdf', '.htm', '.doc', '.docx']:
        ext = ".html" # Handle bare URLs that are actually HTML
    outPath = f"{destDir}/{courseID}.{ext}"
    if exists(outPath):
        f = open(outPath)
        return f, f.read()
    else:
        resp = requests.get(url)
        if resp.ok:
            logging.info(f"Writing file: {outPath}")
            content = resp.content
            with open(outPath, 'wb') as f:
                f.write(content)
                return f, content
        else:
            logging.error(f"Received error: {resp.status_code} when trying to get file {url}")
            return None, None

def extractHTMLBib(html):
    """
    Extract bibliographic data from HTML, using anystyle.
    First we'll need to convert to text.
    """
    soup = BeautifulSoup(html, features='lxml')
    text = soup.getText()
    return extractPlainTextBib(text)

def extractPlainTextBib(text):
    """
    Try to get citations from plain text, using anystyle.
    """
    tempfile = "/tmp/syllabus.txt"
    with open(tempfile, 'w') as f:
        f.write(text)
    os.system('anystyle find ' + tempfile)
    return

def extractHTMLLinks(html):
    soup = BeautifulSoup(html, features='lxml')
    links = soup.find_all('a')
    logging.debug(f"Found {len(links)} links")
    return [link.get('href') for link in links]


def extractPlainTextLinks(text):
    extractor = URLExtract()
    urls = extractor.find_urls(text)
    return urls


def processURLs(urls):
    """ Given a list of URLs, found in a syllabus, and probably of an article or paper,
    let's process it with Zotero, and see if we can make a bibliographic entity out of it."""
    allItemIDs = []
    if len(urls) > 0:
        for url in urls:
            logging.info(f"Trying url: {url}")
            rdf = url2rdf(url)
            if rdf is not None:
                itemId = writeRDF(rdf)
                allItemIDs.append(itemId)
    logging.info(formatIDs(allItemIDs))
    return allItemIDs


def writeRDF(rdf):
    """ Write out the RDF to readings/<ID>.rdf.xml. """
    # Find the item ID for each one
    matches = re.finditer('<z:UserItem rdf:about="(.*?)">', rdf)
    itemIds = [match.group(1) for match in matches if match is not None]
    itemId = itemIds[0]
    fn = f"../readings/{itemId}.rdf.xml"
    # Check to make sure we don't already have it
    if exists(fn):
        return itemId
        logging.info(f"Looks like we already have {fn}")
    else:
        with open(fn, 'w') as f:
            f.write(rdf)
        logging.info(f"Wrote {fn}")
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
        logging.error("Something went wrong with this query.")
        logging.error(resp)


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

def processSyllabus(url, courseID):
    """ We have to put this in a separate function from syllabus(),
    for Click reasons."""
    logging.info(f"Processing syllabus: {url}")
    if url.endswith('.pdf'):
        pdfText = getPDFSyllabus(url, courseID)
        if pdfText is not None:
            links = extractPlainTextLinks(pdf)
        else:
            return
    elif url.endswith('.docx'):
        docText = getDocSyllabus(url)
        links = extractPlainTextLinks(docText)
    else: # Catches .html but also bare urls
        html = getHTMLSyllabus(url, courseID)
        if html is not None:
            # First try to get data from anystyle
            bibtex = extractHTMLBib(html)
            click.echo(bibtex)
            # Then just extract the links
            links = extractHTMLLinks(html)
            if links is None:
                # Try it this way instead, if the first way didn't work
                links = extractPlainTextLinks(html)
        else:
            return
    if links is None:
        logging.error(f"Couldn't find any links in syllabus with URL: {url}")
        return
    textIDs = processURLs(links)
    return textIDs


@cli.command()
@click.argument('URL', nargs=1)
def syllabus(url):
    """Download a syllabus from a URL, extract links from it,
    and create RDF from those links."""
    processSyllabus(url, 0)

@cli.command()
@click.argument('query', nargs=1)
def book(query):
    """ Try to get RDF for a book, by title or similar query.
    Uses the Google Books API.
    """
    isbn = getISBN(query)
    logging.info('ISBN: ', isbn)
    rdf = ident2rdf(isbn)
    click.echo(rdf)
    click.echo(writeRDF(rdf))

@cli.command()
@click.argument('bibtexFile', nargs=1)
def bibtex(bibtexFile):
    """ Convert Bibtex to RDF."""
    if not bibtexFile.endswith('.bib') or bibtexFile.endswith('.bibtex'):
        logging.error(f"File extension of {bibtexFile} not supported. Must be .bib or .bibtex.")
        exit()
    with open(bibtexFile) as fn:
        bib = fn.read()
    rdf = bibtex2rdf(bib)
    click.echo(rdf)
    click.echo(writeRDF(rdf))

if __name__== "__main__":
    cli()
    # lookupORCID("johnson")

import sys
import docker
import requests
from time import sleep
import json
import click

"""
Use the Zotero Translation Server (https://github.com/zotero/translation-server)
via Docker.
"""

def startServer():
    client = docker.from_env()
    container = client.containers.run("zotero/translation-server",
                                    detach=True, ports={1969:1969}, tty=True,
                                    stdin_open=True)
    myContainer = [cont for cont in client.containers.list() if cont == container][0]
    while myContainer.status != 'running':
        print('Waiting for container to start...')
        sleep(1)
    return myContainer

def stopServer():
    myContainer.stop()

def translateURL(url):
    """
    Get bibliographic information from a URL.
    """
    print(f"Translating URL: {url}")
    response = requests.post("http://127.0.0.1:1969/web",
                            data=url,
                            headers={'Content-Type': 'text/plain'})
    if response.ok:
        response.encoding='utf-8'
        return response.text

def translateJSON(zoteroJSON):
    """
    Convert the JSON format that translateURL() returns
    """
    response = requests.post('http://127.0.0.1:1969/export',
                             data=zoteroJSON,
                             params={"format": "rdf_bibliontology"},
                             headers={"Content-Type": "application/json"})
    if response.ok:
        print(response.text)

# zoteroJSON = translateURL('https://www.nytimes.com/2018/06/11/technology/net-neutrality-repeal.html')
# decodedJSON = json.dumps(json.loads(zoteroJSON))
# translateJSON(decodedJSON)

def translateID():
    pass

@click.group()
def cli():
    click.echo('Heyo!')

@cli.command()
@click.argument('URL', nargs=1)
def url(url):
    """Translate a URL to RDF"""
    zoteroJSON = translateURL(url)
    decodedJSON = json.dumps(json.loads(zoteroJSON))
    translateJSON(decodedJSON)


@cli.command()
@click.argument('URL', nargs=1)
def identifier(url):
    """Translate a DOI, arXiv, or ISBN to RDF"""
    translateID()

if __name__== "__main__":
    cli()

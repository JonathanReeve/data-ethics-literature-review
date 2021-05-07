#!/usr/bin/env python3

"""
So we've built a graph from our initial spreadsheet, and now we want to
gather additional information from the semantic web, and add it to the graph.

"""

import rdflib

g = rdflib.Graph()

g.load('graph.ttl', format="ttl")

# 1. Query for universities that have sameAs wikidata
# 2. Download Wikidata as TTL
# 3. Get latitude and longitude and add it to our graph
# 4. Get country of origin and add it to our graph

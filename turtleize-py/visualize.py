#!/usr/bin/env python3

import rdflib
from rdflib import Graph
from rdflib.tools.rdf2dot import rdf2dot
import dominate
from dominate.tags import div, script, style
from dominate.util import raw
import json

g = Graph()
g.parse("../references.ttl", format="ttl")

nodes = list(set([str(node) for node in g.all_nodes()]))

nodesFormatted = [{"id": n, "label": n} for n in nodes]

jsonNodes = json.dumps(nodesFormatted)

statementDicts = []
for stmt in g:
    s, v, o = stmt
    stmtDict = {"from": s, "label": v, "to": o}
    statementDicts.append(stmtDict)

jsonEdges = json.dumps(statementDicts)

doc = dominate.document(title='Visualization of Data Ethics Graph')

with doc.head:
    script(type='text/javascript',
           src='https://unpkg.com/vis-network/standalone/umd/vis-network.min.js')
    style("""
        #mynetwork {
            width: 600px;
            height: 400px;
            border: 1px solid lightgray;
        }
    """)

with doc.body:
    div(id='mynetwork')
    script(raw(
        """
        // create an array with nodes
        //var nodes = new vis.DataSet([
        //    {id: 1, label: 'Node 1'},
        //    {id: 2, label: 'Node 2'},
        //    {id: 3, label: 'Node 3'},
        //    {id: 4, label: 'Node 4'},
        //    {id: 5, label: 'Node 5'}
        //]);
        var nodes = new vis.DataSet(%s)

        // create an array with edges
        // var edges = new vis.DataSet([
        //     {from: 1, to: 3},
        //     {from: 1, to: 2},
        //     {from: 2, to: 4},
        //     {from: 2, to: 5}
        // ]);
        var edges = new vis.DataSet(%s)

        // create a network
        var container = document.getElementById('mynetwork');

        // provide the data in the vis format
        var data = {nodes: nodes, edges: edges};
        var options = {layout: {improvedLayout: false}};

        // initialize your network!
        var network = new vis.Network(container, data, options);
        """ % (jsonNodes, jsonEdges)), type="text/javascript")

print(doc)

#!/usr/bin/env python3
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, RDFS
from rdfFuncs import *
from importlib import reload


thing = URIRef(u'http://schema.org/Thing')
lrmig = Graph().parse('lrmirdfs.ttl', format = 'turtle')
with open('metatempl.txt') as inf:
    metatempl = inf.read()



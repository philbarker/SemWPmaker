#!/usr/bin/env python3
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, RDFS

def print_classes(g: Graph):
    for c in g.subjects(RDF.type, RDFS.Class):
        print(c, g.label(c))
    return

def print_properties(g: Graph, c: URIRef):
# given a graph and class return those terms have that class as
# as their domain, i.e. the properties pertaining to the class
    domIncl = URIRef(u'http://schema.org/domainIncludes')
    for p in g.subjects(domIncl, c):
        print(p)

def class_label(g: Graph, c: URIRef, lang='en'):
# given a graph, class and a language code string returns the most
# appropriate label for the class as a string.
# Uses g.preferredLabel with preferred language but defaults first
# alternative option if possible preferred lang not available
    if g.preferredLabel(c, lang):
        classlabel = g.preferredLabel(c, lang)[0][1].toPython()
    elif g.preferredLabel(c):
        classlabel = g.preferredLabel(c)[0][1].toPython()
    else:
        raise Exception('class has no label')
        return
    return classlabel

def sub_classes(g: Graph, c: URIRef):
# given a graph and a class returns a list of rdfs subclasses of the class 
# from the graph.
    sclist = []
    if g.subjects(RDFS.subClassOf, c):
        for sc in g.subjects(RDFS.subClassOf, c):
             sclist.append(sc)
             sclist.extend(sub_classes(g, sc))
        return sclist
    else:
        return sclist

def write_metafile(g: Graph, c: URIRef, template: str):
# given a graph and a class write a php file for creating metadata for that
# type of thing. Uses a template to create custom post type and create meta
# boxes for editing custom metadata for posts of that type.
    classlabel = class_label(g, c)

    subclasses = []
    subclasses.extend(sub_classes(g,c))
    subclasslabels = classlabel
    for subclass in subclasses:
        subclasslabels = subclasslabels + ', ' + class_label(g, subclass)
    
    template = template.replace("$CLASSLABEL$", classlabel)
    template = template.replace("$SUBCLASSLABELS$", subclasslabels)
    with open(classlabel.lower()+'meta.php', 'w') as outf:
        outf.write(template )
    return

    

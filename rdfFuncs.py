#!/usr/bin/env python3
from rdflib import Graph, URIRef
from rdflib.namespace import RDF, RDFS

class SemWP(Graph):
    
    def __init__(self, fname='lrmirdfs.ttl',
                 template_fname='metatempl.txt',
                 fmat='turtle'):
        self.thing = URIRef(u'http://schema.org/Thing')
        self.g = Graph().parse(fname, format=fmat)
        with open(template_fname) as inf:
            self.template = inf.read()

    def print_classes(self):
        for c in self.g.subjects(RDF.type, RDFS.Class):
            print(c, self.g.label(c))
        return

    def print_properties(self, c: URIRef):
    # given a graph and class return those terms have that class as
    # as their domain, i.e. the properties pertaining to the class
        domIncl = URIRef(u'http://schema.org/domainIncludes')
        for p in self.g.subjects(domIncl, c):
            print(p)

    def class_label(self, c: URIRef, lang='en'):
    # given a graph, class and a language code string returns the most
    # appropriate label for the class as a string.
    # Uses g.preferredLabel with preferred language but defaults first
    # alternative option if possible preferred lang not available
        if self.g.preferredLabel(c, lang):
            classlabel = self.g.preferredLabel(c, lang)[0][1].toPython()
        elif self.g.preferredLabel(c):
            classlabel = self.g.preferredLabel(c)[0][1].toPython()
        else:
            raise Exception('class has no label')
            return
        return classlabel

    def sub_classes(self, c: URIRef):
    # given a graph and a class returns a list of rdfs subclasses of the class 
    # from the graph.
        sclist = []
        if self.g.subjects(RDFS.subClassOf, c):
            for sc in self.g.subjects(RDFS.subClassOf, c):
                 sclist.append(sc)
                 sclist.extend(self.sub_classes(sc))
            return sclist
        else:
            return sclist

    def write_metafile(self, c: URIRef):
    # given a graph and a class write a php file for creating metadata for that
    # type of thing. Uses a template to create custom post type and create meta
    # boxes for editing custom metadata for posts of that type.
        classlabel = self.class_label(c)

        subclasses = []
        subclasses.extend(self.sub_classes(c))
        subclasslabels = classlabel
        for subclass in subclasses:
            subclasslabels = subclasslabels + ', ' + self.class_label(subclass)
        
        self.template = self.template.replace("$CLASSLABEL$", classlabel)
        self.template = self.template.replace("$SUBCLASSLABELS$", subclasslabels)
        with open(classlabel.lower()+'meta.php', 'w') as outf:
            outf.write(self.template)
        return


#!/usr/bin/env python3
from rdflib import Graph, URIRef, Namespace
from rdflib.namespace import RDF, RDFS
schema = Namespace(u'http://schema.org/')
thing = schema.Thing

from html.parser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)



class SemWP(Graph):
    
    def __init__(self, fname='lrmirdfs.ttl',
                 template_fname='metatempl.txt',
                 fmat='turtle'):
        self.g = Graph().parse(fname, format=fmat)
        with open(template_fname) as inf:
            self.template = inf.read()

    def print_classes(self):
        for c in self.g.subjects(RDF.type, RDFS.Class):
            print(c, self.g.label(c))
        return

    def print_properties(self, c: URIRef):
    # given a class return those terms have that class as
    # as their domain, i.e. the properties pertaining to the class
        for p in self.g.subjects(schema.domainIncludes, c):
            print(p)

    def resource_label(self, r: URIRef, lang='en'):
    # given a resource uri and a language code string returns the most
    # appropriate label for the resource as a string.
    # Uses g.preferredLabel with preferred language but defaults first
    # alternative option if possible preferred lang not available
        if self.g.preferredLabel(r, lang):
            resourcelabel = self.g.preferredLabel(r, lang)[0][1].toPython()
        elif self.g.preferredLabel(r):
            resourcelabel = self.g.preferredLabel(r)[0][1].toPython()
        else:
            raise Exception('resource has no label')
            return
        return resourcelabel.lower()

    def resource_comment(self, r: URIRef):
    # given a resource uri returns the rdfs comment as a string
    # stripped of its HTML cruft, new lines and quotes
        s = MLStripper()
        html = self.g.value(r, RDFS.comment, None).toPython()
        html += '<br>'      # bizarrely, will return null if no html tags at all
        s.feed(html)
        comment = s.get_data()
        comment = comment.replace('\n',' ')
        comment = comment.replace("'","")
        comment = comment.replace('"','')
        comment = comment.replace(')','')
        comment = comment.replace('(','')
        return comment    

    def sub_classes(self, c: URIRef):
    # given a class returns a list of rdfs subclasses of the class 
    # from the current instance of SemWP graph.
        sclist = []
        if self.g.subjects(RDFS.subClassOf, c):
            for sc in self.g.subjects(RDFS.subClassOf, c):
                 sclist.append(sc)
                 sclist.extend(self.sub_classes(sc))
            return sclist
        else:
            return sclist
        
    def properties(self, c: URIRef):
    # given a class, return a list of those terms whos domainIncludes that class
    # and are properties
        p_list =[]
        if self.g.subjects(schema.domainIncludes, c):
            for p in self.g.subjects(schema.domainIncludes, c):
                p_list.append(p)   #to do: check this is a rdf:property
            return p_list
        else:
            return p_list

    def fieldsarray(self, c: URIRef):
    # given a class, return a string which php fragment to define the
    # metabox fields for the properties of the class.
        fieldsarray = ['array(']
        textfieldtemplate = """
                            array(
                                    'type'  => 'textarea',
                                    'name'  => __( '{name}' ),
                                    'id'    => "{{$prefix}}{id}",
                                    'desc'  => __( '{desc}' ),
                                    'clone' => true,
                                    'cols'  => 20,
                                    'rows'  => 3,
                            ),"""
        urlfieldtemplate  = """
                            array(
                                    'type'  => 'url',
                                    'name'  => __( '{name}' ),
                                    'id'    => "{{$prefix}}{id}",
                                    'desc'  => __( '{desc}' ),
                                    'clone' => true,
                            ),"""

        for p in self.properties(c):

            for expected_range in self.g.objects(p, schema.rangeIncludes):
                if (expected_range == schema.Text):
                    fieldsarray.append(textfieldtemplate.format(name = self.resource_label(p)
                                                                     + ' ('
                                                                     + self.resource_label(expected_range)
                                                                     + ')',
                                                                id   = self.resource_label(p)
                                                                     + self.resource_label(expected_range),
                                                                desc = self.resource_comment(p)
                                                                ))
                elif (expected_range == schema.URL):
                    fieldsarray.append(urlfieldtemplate.format(name = self.resource_label(p)
                                                                     + ' ('
                                                                     + self.resource_label(expected_range)
                                                                     + ')',
                                                                id   = self.resource_label(p)
                                                                     + self.resource_label(expected_range),
                                                               desc = self.resource_comment(p)
                                                               ))
                else:
                    print(p, 'is a', expected_range)
                
        fieldsarray.append('\n                ),')
        return ''.join(fieldsarray)

    def write_metafile(self, c: URIRef):
    # given a graph and a class write a php file for creating metadata for that
    # type of thing. Uses a template to create custom post type and create meta
    # boxes for editing custom metadata for posts of that type.
        classlabel = self.resource_label(c)

        subclasses = []
        subclasses.extend(self.sub_classes(c))
        subclasslabels = "'" + classlabel + "'"
        for subclass in subclasses:
            subclasslabels = subclasslabels + ", '" + self.resource_label(subclass) + "'"
        
        self.template = self.template.replace("$CLASSLABEL$", classlabel)
        self.template = self.template.replace("$SUBCLASSLABELS$", subclasslabels)

  
        self.template = self.template.replace("$FIELDSARRAY$", self.fieldsarray(c))
        
        with open(classlabel.lower()+'meta.php', 'w') as outf:
            outf.write(self.template)
        return


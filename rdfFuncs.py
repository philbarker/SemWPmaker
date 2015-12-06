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
                       fmat='turtle'):
        self.g = Graph().parse(fname, format=fmat)

    def resource_label(self, r: URIRef, lang='en'):
    # Given SemWP object amd a resource uri and a language code string
    # returns the most appropriate label for the resource as a string.
    # Uses g.preferredLabel with preferred language but defaults first
    # alternative option if possible preferred lang not available
        if self.g.preferredLabel(r, lang):
            resourcelabel = self.g.preferredLabel(r, lang)[0][1].toPython()
        elif self.g.preferredLabel(r):
            resourcelabel = self.g.preferredLabel(r)[0][1].toPython()
        else:
            raise Exception('resource %r has no label' % r)
            return
        return resourcelabel

    def resource_id(self, r: URIRef, lang='en'):
    # Given SemWP object amd a resource uri and a language code string
    # returns a string that can be used as an id for custom post types
    # for that resource.
    # Uses g.preferredLabel with preferred language but defaults first
    # alternative option if possible preferred lang not available
    # bumps to lower case and truncates to 20 chars
        resourceid = self.resource_label(r, lang)[:20].lower()
        return resourceid

    def resource_comment(self, r: URIRef):
    # Given SemWP object and a resource uri returns the rdfs comment as a string
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
    # Given SemWP object and a class returns a list of rdfs subclasses of the class 
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
    # Given SemWP object and a class, return a list of those terms whos domainIncludes that class
    # and are properties
        p_list =[]
        if self.g.subjects(schema.domainIncludes, c):
            for p in self.g.subjects(schema.domainIncludes, c):
                p_list.append(p)   #to do: check this is a rdf:property
            return p_list
        else:
            return p_list

    def fieldsarray(self, c: URIRef):
    # Given SemWP object and a class, return a string which php fragment to define the
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
        datefieldtemplate  = """
                            array(
                                    'type'  => 'date',
                                    'name'  => __( '{name}' ),
                                    'id'    => "{{$prefix}}{id}",
                                    'desc'  => __( '{desc}' ),
                                    'clone' => true,
                            ),"""
        datetimefieldtemplate  = """
                            array(
                                    'type'  => 'datetime',
                                    'name'  => __( '{name}' ),
                                    'id'    => "{{$prefix}}{id}",
                                    'desc'  => __( '{desc}' ),
                                    'clone' => true,
                            ),"""
        urlfieldtemplate  = """
                            array(
                                    'type'  => 'url',
                                    'name'  => __( '{name}' ),
                                    'id'    => "{{$prefix}}{id}",
                                    'desc'  => __( '{desc}' ),
                                    'clone' => true,
                            ),"""
        numberfieldtemplate  = """
                            array(
                                    'type'  => 'url',
                                    'name'  => __( '{name}' ),
                                    'id'    => "{{$prefix}}{id}",
                                    'desc'  => __( '{desc}' ),
                                    'clone' => true,
                            ),"""
        objectfieldtemplate  = """
                            array(
                                    'type'  => 'post',
                                    'name'  => __( '{name}' ),
                                    'id'    => "{{$prefix}}{id}",
                                    'desc'  => __( '{desc}' ),
                                    'post_type'  => array({classes}),
                                    'field_type' => 'select_advanced',
                                    'query_args'  => array(
                                        'post_status'    => 'publish',
                                        'posts_per_page' => - 1,
                                         ),
                                    'clone' => true,
                            ),"""

        for p in self.properties(c):
            for expected_range in self.g.objects(p, schema.rangeIncludes):
                if (expected_range == schema.Text):
                    fieldtemplate = textfieldtemplate
                    name = self.resource_label(p) + ' (' + self.resource_label(expected_range) + ')'
                    id   = self.resource_id(p) + self.resource_id(expected_range)
                    desc = self.resource_comment(p)
                    subclassids = ''
                elif (expected_range == schema.URL):
                    fieldtemplate = urlfieldtemplate
                    name = self.resource_label(p) + ' (' + self.resource_label(expected_range) + ')'
                    id   = self.resource_id(p) + self.resource_id(expected_range)
                    desc = self.resource_comment(p)
                    subclassids = ''
                elif (expected_range == schema.Date):
                    fieldtemplate = datefieldtemplate
                    name = self.resource_label(p) + ' (' + self.resource_label(expected_range) + ')'
                    id   = self.resource_id(p) + self.resource_id(expected_range)
                    desc = self.resource_comment(p)
                    subclassids = ''
                elif (expected_range == schema.DateTime):
                    fieldtemplate = datetimefieldtemplate
                    name = self.resource_label(p) + ' (' + self.resource_label(expected_range) + ')'
                    id   = self.resource_id(p) + self.resource_id(expected_range)
                    desc = self.resource_comment(p)
                    subclassids = ''
                elif (expected_range == schema.Number or
                      expected_range == schema.Integer ):
                    fieldtemplate = numberfieldtemplate
                    name = self.resource_label(p) + ' (' + self.resource_label(expected_range) + ')'
                    id   = self.resource_id(p) + self.resource_id(expected_range)
                    desc = self.resource_comment(p)
                    subclassids = ''
                elif (  expected_range == schema.ImageObject or
                        expected_range == schema.CreativeWork or
                        expected_range == schema.Place or
                        expected_range == schema.Organization or
                        expected_range == schema.Person or
                        expected_range == schema.Review or
                        expected_range == schema.VideoObject or
                        expected_range == schema.MediaObject or
                        expected_range == schema.AlignmentObject or
                        expected_range == schema.Audience or
                        expected_range == schema.Thing or
                        expected_range == schema.SoftwareApplication or
                        expected_range == schema.Event ):
                    fieldtemplate = objectfieldtemplate
                    name = self.resource_label(p) + ' (' + self.resource_label(expected_range) + ')'
                    id   = self.resource_id(p) + self.resource_id(expected_range)
                    desc = self.resource_comment(p)
                    subclasses = []
                    subclasses.extend(self.sub_classes(expected_range))
                    classid = self.resource_id(expected_range)
                    subclassids = "'" + classid + "'"
                    for subclass in subclasses:
                        subclassids = subclassids + ", '" + self.resource_id(subclass) + "'"
                elif (expected_range == schema.Language or        #to do: enumerations!
                      expected_range == schema.BookFormatType ):
                    fieldtemplate = textfieldtemplate
                    name = self.resource_label(p) + ' (' + self.resource_label(expected_range) + ')'
                    id   = self.resource_id(p) + self.resource_id(expected_range)
                    desc = self.resource_comment(p)
                    subclassids = ''
                elif (expected_range == schema.Duration):         #to do: Duration
                    fieldtemplate = textfieldtemplate
                    name = self.resource_label(p) + ' (' + self.resource_label(expected_range) + ')'
                    id   = self.resource_id(p) + self.resource_id(expected_range)
                    desc = self.resource_comment(p)
                    subclassids = ''
                elif ( expected_range == schema.QuantitativeValue or  # these should be complex types
                       expected_range == schema.PostalAddress or      # but the class is not included
                       expected_range == schema.Class or      
                       expected_range == schema.Distance or
                       expected_range == schema.ProgramMembership):   
                    fieldtemplate = textfieldtemplate             
                    name = self.resource_label(p)
                    id   = self.resource_id(p)
                    desc = self.resource_comment(p)
                    subclassids = ''
                else:                                # ulitmately this should raise and expection
                    print(p, 'is a', expected_range) # but for now just inform what new range types
                    name = ''                        # need to be included and work around errors.
                    id = ''
                    desc = ''
                    subclassids = ''
                    fieldtemplate = ''
                fieldsarray.append(fieldtemplate.format(name = name,
                                                        id   = id,
                                                        desc = self.resource_comment(p),
                                                        classes = subclassids))
        fieldsarray.append('\n                ),')
        return ''.join(fieldsarray)

    def write_metafile(self, c: URIRef,
                       template_fname='metatempl.txt'):
    # Given SemWP object and a class write a php file for creating metadata for that
    # type of thing. Uses a template to create custom post type and create meta
    # boxes for editing custom metadata for posts of that type.

        with open(template_fname) as infile:
            self.template = infile.read()

        classlabel = self.resource_label(c)
        classid = self.resource_id(c)
        subclasses = []
        subclasses.extend(self.sub_classes(c))
        subclassids = "'" + classid + "'"
        for subclass in subclasses:
            subclassids = subclassids + ", '" + self.resource_id(subclass) + "'"
        
        self.template = self.template.replace("$CLASSLABEL$", classid)
        self.template = self.template.replace("$SUBCLASSLABELS$", subclassids)  
        self.template = self.template.replace("$FIELDSARRAY$", self.fieldsarray(c))
        
        with open('inc/'+classlabel.lower()+'meta.php', 'w') as outf:
            outf.write(self.template)
        return


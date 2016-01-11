#!/usr/bin/env python3
from rdfFuncs import SemWP 
from tkinter import Tk, StringVar, IntVar, Text
from tkinter.constants import N, S, E, W, NS, NW, EW, SE, NSEW, LEFT
from tkinter.constants import SUNKEN, NONE, WORD, END, NORMAL, DISABLED
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.ttk import Frame, Notebook, Treeview, Label, Button, Scrollbar, Checkbutton
from rdflib import URIRef, Namespace, Literal
from pbtkextend import CheckbuttonGroup, VerticalScrolledFrame, TextPage, \
                        ButtonBar

schema = Namespace(u'http://schema.org/')
semwp_ns = Namespace(u'http://ns.pjjk.net/semwp')

class SEMWPConfig(Frame):

    def build_classtree(self):
        for child in self.classtree.get_children(): # get rid of existing entries in class tree 
            self.classtree.delete(child)            # before building a new one
        
        def insert_subclasses(c, p):
            for sc in self.rdfschema.sub_classes(c, recurse=False):
                parent = self.classtree.insert(p, 'end',
                                               text=self.rdfschema.resource_label(sc),
                                               open=True, iid=sc,
                                               tags=('include'))
                if (self.rdfschema.sub_classes(sc, recurse=False) != []):
                    insert_subclasses(sc, parent)
                            
        for c in self.rdfschema.top_classes():
            parent = self.classtree.insert('', 'end',
                                           text=self.rdfschema.resource_label(c),
                                           open=True, iid=c,
                                           tags=('include'))
            if (self.rdfschema.sub_classes(c, recurse=False) != []):
                insert_subclasses(c, parent)
        
    def open_rdfs(self):
        self.rdfsFileName.set(askopenfilename(filetypes=[("ttl","*.ttl")]))
        self.rdfschema = SemWP(fname=self.rdfsFileName.get())
        if self.rdfschema.name is not None:
            self.rdfsName.set(self.rdfschema.name)
        else:
            self.rdfsName.set('unnamed RDF Schema')
        self.build_classtree()
        if self.templateFileName.get() is not '':
            self.write_btn.config(command=self.write, state=NORMAL)

    def open_template(self):
        self.templateFileName.set(askopenfilename(filetypes=[("txt","*.txt")]))
        with open(self.templateFileName.get()) as infile:
            self.template_txt.delete('1.0', END)
            self.template_txt.insert(END, infile.read())
        if self.template_txt.get('1.0') == '':
            raise Exception('%r does not seem to be a valid template'
                             % self.templateFileName.get())
        if self.rdfsName.get() is not '':
            self.write_btn.config(command=self.write, state=NORMAL)
        self.savetemplate_btn.config(command=self.save_template, state=NORMAL)


    def write(self):
        self.rdfschema.write_metafile(c=self.rdfschema.thing)
        
    def save_template(self):
        self.templateFileName.set(asksaveasfilename(filetypes=[("txt","*.txt")]))
        with open(self.templateFileName.get(), 'w') as outfile:
            if outfile is None:
                return
            else:
                outfile.write(self.template_txt.get('1.0', END) )
        pass
        
    def set_property_flag(self, p:URIRef):
        include = []
        plabel = self.rdfschema.resource_label(p, lang='en')
        for key in self.propcheckboxes[plabel].vals.keys():
            if self.propcheckboxes[plabel].vals[key].get() == 1:
                include.append(key)
        self.rdfschema.set_pinclude_flags(p, include)

    def update_propertyinfo(self):
        # Display list of properties for the item currently selected in the classtree iff
        # that item is selected to have a custom post type created for it; then, 
        # create a checkbox for each property of displayed classes which determines what
        # type of metadata box is created for that property (if any).
        item = self.classtree.focus()
        itemref = URIRef(item)
        for child in self.propertiesframe.interior.winfo_children():
            child.destroy()
        showpropertyinfo = False
        for inflag in self.rdfschema.g.objects(subject=itemref, predicate=semwp_ns.include):
            if inflag == Literal('True'):    # sets showpropertyinfo if post type is to be 
                showpropertyinfo = True      # created for class
        if showpropertyinfo:
            pcount = 0             # property count, used to set grid row of checkbox
            self.propcheckboxes = dict()
            for p in self.rdfschema.properties(itemref):
                proplabel = self.rdfschema.resource_label(p, lang='en')
                heading = proplabel + '. Range includes: '
                flags=self.rdfschema.get_pinclude_flags(p)
                names=['text']
                for c in self.rdfschema.g.objects(p, schema.rangeIncludes):
                    heading = heading +' '+ self.rdfschema.resource_label(c, lang='en')
                    if c == schema.Text:
                        names.append('long text')
                        if flags == []:
                            self.rdfschema.set_pinclude_flags(p, incl=['text'])
                    else:
                        rangelabel = self.rdfschema.resource_label(c, lang='en')
                        names.append(rangelabel)
                        if flags == []:
                            self.rdfschema.set_pinclude_flags(p, incl=[rangelabel])
                Label(self.propertiesframe.interior, text=heading, padding='3 0 0 0'
                      ).grid(row=2*pcount, column=0, columnspan=10, sticky=NW)
                Label(self.propertiesframe.interior, text='Include as:', padding='32 0 0 9'
                      ).grid(row=2*pcount+1, column=0, sticky=NW)    
                self.propcheckboxes[proplabel] = CheckbuttonGroup(
                                                    self.propertiesframe.interior, names,
                                                    command=lambda prop=p: self.set_property_flag(prop),
                                                    side=LEFT)
                self.propcheckboxes[proplabel].grid(row=2*pcount+1, column=1, sticky=NW)
                for name in self.rdfschema.get_pinclude_flags(p):
                    self.propcheckboxes[proplabel].vals[name].set(1)
                pcount += 1
                    

    def update_classinfo(self, event):
        item = self.classtree.focus()
        itemref = URIRef(item)
        self.className.set(self.rdfschema.resource_label(itemref, lang='en'))
        self.classDescrTxt.configure(state = NORMAL)
        self.classDescrTxt.delete('1.0', END)
        self.classDescrTxt.insert(END, self.rdfschema.resource_comment(itemref, lang='en'))
        self.classDescrTxt.configure(state = DISABLED)
        # the following deals with setting the includeclass flag which determines whether
        # the class if greyed out or not, setting the includeclass int variable which
        # determines the check button state, based on the include property of the class in
        # the graph. If the include property is not present for the class it is set to
        # 'include' and the flag & checkbutton set accordingly.
        count = 0
        for o in self.rdfschema.g.objects(itemref, semwp_ns.include):
            if o == Literal('False'):
                self.includeclass.set(0)
                count = 1
#                self.includeclassflag.set('was '+o.toPython())
                self.classtree.item(itemref, tags=('notinclude'))
                self.classtree.tag_configure('notinclude', foreground='gray')
            elif o == Literal('True'):
                self.includeclass.set(1)
                count = 1
#               self.includeclassflag.set('was '+o.toPython())
                self.classtree.item(itemref, tags=('include'))
                self.classtree.tag_configure('include', foreground='black')
        if count == 0:
            self.rdfschema.set_include_true(itemref)
            self.includeclass.set(1)
#            self.includeclassflag.set('count 0 set to true')
            self.classtree.item(itemref, tags=('include'))
            self.classtree.tag_configure('include', foreground='black')
        self.update_propertyinfo()   
            
    def set_classtree_include(self, i: URIRef, s: str):
        if s == 'include':
            self.classtree.item(i, tags=('include'))
            self.classtree.tag_configure('include', foreground='black')
            parent = self.classtree.parent(i)
            if parent is not '':
                self.set_classtree_include(parent, 'include')
        elif s == 'notinclude':
            self.classtree.item(i, tags=('notinclude'))
            self.classtree.tag_configure('notinclude', foreground='gray')
            for child in self.classtree.get_children(i):
                self.set_classtree_include(child, 'notinclude')
        
    def include_class(self):
        item = self.classtree.focus()
        itemref = URIRef(item)
        if self.includeclass.get() == 1:
            self.rdfschema.set_include_true(itemref)
            self.set_classtree_include(itemref, 'include')
        elif self.includeclass.get() == 0:
            self.rdfschema.set_include_false(itemref)
            self.set_classtree_include(itemref, 'notinclude')
#        for o in self.rdfschema.g.objects(itemref, semwp_ns.include):
#            self.includeclassflag.set(o.toPython())
        self.update_propertyinfo()            
        
    def create_rdfs_frame(self, master:Notebook):
        rdfsframe = Frame(master, padding = '3 3 3 3', width=600, height=400)
        Label(rdfsframe, text='RDFS Name:', padding='3 3 3 3').grid(row=0, column=0, padx=3, pady=3)
        rdfsNameLbl = Label(rdfsframe, textvariable=self.rdfsName,
                            background='#bbb', relief=SUNKEN, padding='3 0 3 3')
        rdfsNameLbl.grid(row=0, column=1, columnspan=3, sticky=EW, padx=3, pady=6)
        self.classtree.heading(column='#0', text='ClassTree')
        ysb = Scrollbar(rdfsframe, orient='vertical', command=self.classtree.yview)
        xsb = Scrollbar(rdfsframe, orient='horizontal', command=self.classtree.xview)
        self.classtree.configure(yscrollcommand=ysb.set)
        self.classtree.configure(xscrollcommand=xsb.set)
        self.classtree.bind('<<TreeviewSelect>>', self.update_classinfo)
        self.classtree.grid(row=1, column=0, columnspan=2, in_=rdfsframe, sticky=NSEW)
        self.classtree.lift(rdfsframe)
        self.classtree.tag_configure('include', foreground='black')
        self.classtree.tag_configure('notinclude', foreground='gray')
        ysb.grid(row=1, column=2, sticky=(NS))
        xsb.grid(row=2, column=0, columnspan=2, sticky=(EW))
        classinfoframe = Frame(rdfsframe, width=300, height=400)
        classinfoframe.grid(row=1, column=3, padx=3, pady=3, sticky=(NSEW))
        Label(classinfoframe, text='Class Name:',
              font='bold', padding='3 3 3 3').grid(row=1, column=0, sticky=NW)
        classNameLbl = Label(classinfoframe, textvariable=self.className,
                            background='#bbb', relief=SUNKEN, padding='3 3 3 3',
                             font='bold', width=25)
        classNameLbl.grid(row=1, column=1, sticky=EW)
        Label(classinfoframe, text='Description:',
              font='bold', padding='3 3 3 3').grid(row=2, column=0, sticky=NW)
        self.classDescrTxt.grid(row=2, column=1, in_=classinfoframe, sticky=EW)
        self.classDescrTxt.lift(classinfoframe)
        include_chk = Checkbutton(classinfoframe,
                                  text='include this class',
                                  variable=self.includeclass,
                                  command=self.include_class)
        include_chk.grid(row=3, column=1, sticky=E)
        Label(classinfoframe, text='Properties:',
              font='bold', padding='3 3 3 3').grid(row=5, column=0, sticky=NW)
        self.propertiesframe.grid(in_ = classinfoframe, row=5, column=1, sticky=(N+E+S+W))
        self.propertiesframe.lift(classinfoframe)

        classinfoframe.rowconfigure(5, weight=1)
        classinfoframe.columnconfigure(1, weight=1)
        rdfsframe.columnconfigure(1, weight=1)
        rdfsframe.columnconfigure(3, weight=3)
        rdfsframe.rowconfigure(1, weight=1)        
        master.add(rdfsframe, text='RDFS')

    def create_status_bar(self, master):
        statbar = Frame(master, padding = '3 3 3 3')
        statbar.grid(column=0, row=2, sticky=(EW, S))
        Label(statbar, text='RDFS File:', padding='0 3 0 3').grid(row=0, column=0, sticky=SE)
        rdfsFileNameLbl = Label(statbar, textvariable=self.rdfsFileName,
                                background='#bbb', relief=SUNKEN, padding='3 3 3 3')
        rdfsFileNameLbl.grid(column=1, row=0, sticky=(EW))
        Label(statbar, text='Template file:', padding='0 3 0 3').grid(row=1, column=0, sticky=SE)        
        templateFileNameLbl = Label(statbar, textvariable=self.templateFileName,
                                    background='#bbb', relief=SUNKEN, padding='3 3 3 3')
        templateFileNameLbl.grid(column=1, row=1, sticky=(EW))
        statbar.columnconfigure(1, weight=1)
        for child in statbar.winfo_children():
            child.grid_configure(padx=3, pady=3)

    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.master = master

        # the following stringvars & widgets reference values used by
        # several functions. Declared here for clarity,
        # packed in relevant frame when frame is created
        # and values set when available.
        self.rdfs_btn = Button(master, text="Open\nRDFS",
                               command=self.open_rdfs)
        self.template_btn = Button(master, text="Open\nTemplate",
                                   command=self.open_template)
        self.write_btn = Button(master, text="Write\nPHP",
                                command='', state=DISABLED)
        self.savetemplate_btn = Button(master, text="Save\nTemplate",
                                       command='', state=DISABLED)
        self.saverdfs_btn = Button(master, text="Save\nRDFS",
                                       command='', state=DISABLED)
        btnlst = [self.rdfs_btn, self.template_btn, self.savetemplate_btn, self.saverdfs_btn, self.write_btn]
        ButtonBar(master, btnlst, 3, padding='3 3 0 0'
                  ).grid(column=0,row=0, sticky=(N, W))
        self.classtree = Treeview(master)
        self.rdfsFileName = StringVar()
        self.rdfsName = StringVar()
        self.templateFileName = StringVar()
        self.className = StringVar()
        self.classDescrTxt = Text(master,
                                  background='#bbb',
                                  relief=SUNKEN, 
                                  wrap=WORD,
                                  height=4,
                                  width=60,
                                  state = DISABLED)
        self.propertiesframe = VerticalScrolledFrame(master,
                                     relief=SUNKEN)
                            # the (variable) widgets in this will have info
                            # about properties of the selected class
        self.includeclass = IntVar()
        self.includeclass.set(1)
#        self.includeclassflag = StringVar()
#        self.includepropsflags=dict()
        self.ntbk = Notebook(master, padding='6 12 6 12')
        self.create_rdfs_frame(self.ntbk)
        self.template_txt = TextPage(self.ntbk, 'Template', 
                                    background='#fff',
                                    relief=SUNKEN, 
                                    wrap = NONE,
                                    width = 40,
                                    height = 40)
        self.ntbk.grid(column=0, row=1, sticky=NSEW)
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=1)
        self.create_status_bar(master)
        

if __name__ == '__main__':
    root = Tk()
    root.title('Semantic WordPress Configurator')
    SEMWPConfig(master=root).mainloop()
    

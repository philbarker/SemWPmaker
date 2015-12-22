#!/usr/bin/env python3
from rdfFuncs import SemWP 
from tkinter import *
from tkinter.filedialog import *
from tkinter.ttk import *
from rdflib import URIRef, Namespace, Literal
from rdflib.namespace import RDF, RDFS
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
                                               open=True, iid=sc)
                if (self.rdfschema.sub_classes(sc, recurse=False) != []):
                    insert_subclasses(sc, parent)
                            
        for c in self.rdfschema.top_classes():
            parent = self.classtree.insert('', 'end',
                                           text=self.rdfschema.resource_label(c),
                                           open=True, iid=c)
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
            self.write_btn.config(command=lambda:self.write(), state=NORMAL)

    def write(self):
        self.rdfschema.write_metafile(c=self.rdfschema.thing)

    def update_classinfo(self, event):
        item = self.classtree.focus()
        itemref = URIRef(item)
        self.className.set(self.rdfschema.resource_label(itemref, lang='en'))
        self.classDescrTxt.configure(state = NORMAL)
        self.classDescrTxt.delete('1.0', END)
        self.classDescrTxt.insert(END, self.rdfschema.resource_comment(itemref, lang='en'))
        self.classDescrTxt.configure(state = DISABLED)
        count = 0
        for o in self.rdfschema.g.objects(itemref, semwp_ns.include):
            if o == Literal('False'):
                 self.includeclass.set(0)
                 count = 1
                 self.includeclassflag.set('was '+o.toPython())

            elif o == Literal('True'):
                 self.includeclass.set(1)
                 count = 1
                 self.includeclassflag.set('was '+o.toPython())
 
        if count == 0:
            self.rdfschema.set_include_true(itemref)
            self.includeclass.set(1)
            self.includeclassflag.set('count 0 set to true')

#        for o in self.rdfschema.g.objects(itemref, semwp_ns.include):
#            self.includeclassflag.set(o.toPython())
                 
        
    def include_class(self):
        item = self.classtree.focus()
        itemref = URIRef(item)
        if self.includeclass.get() == 1:
            self.rdfschema.set_include_true(itemref)
        elif self.includeclass.get() == 0:
            self.rdfschema.set_include_false(itemref)
        for o in self.rdfschema.g.objects(itemref, semwp_ns.include):
            self.includeclassflag.set(o.toPython())

        
    def create_buttonbar(self, master):
        bbframe = Frame(master, padding='3 3 3 3')
        self.rdfs_btn.grid(column=0, row=0, in_=bbframe)
        self.rdfs_btn.lift(bbframe)
        self.template_btn.grid(column=1, row=0, in_=bbframe)
        self.template_btn.lift(bbframe)
        self.write_btn.grid(column=2, row=0, in_=bbframe)
        self.write_btn.lift(bbframe)
        for child in bbframe.winfo_children():
            child.grid_configure(padx=3, pady=3)
        bbframe.grid(column=0,row=0, sticky=(N, W))
        
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
        self.classtree.grid(row=1, column=0, columnspan=2, in_=rdfsframe, sticky=(N+E+S+W))
        self.classtree.lift(rdfsframe)
        ysb.grid(row=1, column=2, sticky=(NS))
        xsb.grid(row=2, column=0, columnspan=2, sticky=(EW))
        classinfoframe = Frame(rdfsframe, width=300, height=400)
        classinfoframe.grid(row=1, column=3, padx=3, pady=3, sticky=(N+E+S+W))
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
        includeclassflag_lbl=Label(classinfoframe, textvariable= self.includeclassflag,
                                   background='#bbb', relief=SUNKEN, padding='3 3 3 3',
                                   font='bold', width=25)
        includeclassflag_lbl.grid(row=4, column=1, sticky=EW)

        classinfoframe.columnconfigure(1, weight=1)
        rdfsframe.columnconfigure(1, weight=1)
        rdfsframe.columnconfigure(3, weight=3)
        rdfsframe.rowconfigure(1, weight=1)
        master.add(rdfsframe, text='RDFS')

    def create_template_frame(self, master:Notebook):
        templateframe = Frame(master, padding = '', width=600, height=400)
        master.add(templateframe, text='Template')

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
        # configured when values for them are available.
        self.rdfs_btn = Button(master, text="Open\nRDFS",
                               command=lambda: self.open_rdfs())
        self.template_btn = Button(master, text="Open\nTemplate",
                                   command='')
        self.write_btn = Button(master, text="Write\nPHP",
                                command='', state=DISABLED)
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
        self.includeclass = IntVar()
        self.includeclass.set(1)
        self.includeclassflag = StringVar()
        self.create_buttonbar(master)
        self.ntbk = Notebook(master, padding='6 12 6 12')
        self.create_rdfs_frame(self.ntbk)
        self.create_template_frame(self.ntbk)        
        self.ntbk.grid(column=0, row=1, sticky=NSEW)
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(1, weight=1)
        self.create_status_bar(master)
        


root = Tk()
root.title('Semantic WordPress Configurator')
app = SEMWPConfig(master=root)
app.mainloop()
    

#!/usr/bin/env python3
from rdfFuncs import SemWP
from tkinter import *
from tkinter.filedialog import *
from tkinter.ttk import *

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
        self.classURI.set(item)
     
    def create_buttonbar(self, master):
        bbframe = Frame(master, padding='3 3 3 3')
        self.rdfs_btn = Button(bbframe, text="Open\nRDFS", command=lambda: self.open_rdfs())
        self.rdfs_btn.grid(column=0, row=0)
        self.template_btn = Button(bbframe, text="Open\nTemplate", command='')
        self.template_btn.grid(column=1, row=0)
        self.write_btn = Button(bbframe, text="Write\nPHP", command='', state=DISABLED)
        self.write_btn.grid(column=2, row=0)
        for child in bbframe.winfo_children():
            child.grid_configure(padx=3, pady=3)
        bbframe.grid(column=0,row=0, sticky=(N, W))
        
    def create_rdfs_frame(self, master:Notebook):
        rdfsframe = Frame(master, padding = '3 3 3 3', width=600, height=400)
        Label(rdfsframe, text='RDFS Name:', padding='3 3 3 3').grid(row=0, column=0, padx=3, pady=3)
        rdfsNameLbl = Label(rdfsframe, textvariable=self.rdfsName,
                            background='#bbb', relief=SUNKEN, padding='3 0 3 3')
        rdfsNameLbl.grid(row=0, column=1, columnspan=3, sticky=EW, padx=3, pady=6)
        self.classtree = Treeview(rdfsframe)
        self.classtree.heading(column='#0', text='ClassTree')
        ysb = Scrollbar(rdfsframe, orient='vertical', command=self.classtree.yview)
        xsb = Scrollbar(rdfsframe, orient='horizontal', command=self.classtree.xview)
        self.classtree.configure(yscrollcommand=ysb.set)
        self.classtree.configure(xscrollcommand=xsb.set)
        self.classtree.bind('<<TreeviewSelect>>', self.update_classinfo)
        self.classtree.grid(row=1, column=0, columnspan=2, sticky=(N+E+S+W))
        ysb.grid(row=1, column=2, sticky=(NS))
        xsb.grid(row=2, column=0, columnspan=2, sticky=(EW))
        classinfoframe = Frame(rdfsframe, width=300, height=400, style='classinfo.TFrame')
        classinfoframe.grid(row=1, column=3, padx=3, pady=3, sticky=(N+E+S+W))
        Label(classinfoframe, text='Class URI:', padding='3 3 3 3').grid(row=0, column=0, sticky=W)
        classUriLbl = Label(classinfoframe, textvariable=self.classURI,
                            background='#bbb', relief=SUNKEN, padding='3 3 3 3')
        classUriLbl.grid(row=0, column=1, sticky=EW)
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
        self.rdfsFileName = StringVar()
        self.rdfsFileName.set('')
        self.rdfsName = StringVar()
        self.templateFileName = StringVar()
        self.templateFileName.set('')
        self.classURI = StringVar()
        self.classURI.set('')
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
s = Style()
s.configure('classinfo.TFrame', relief='groove',
                                padding=12)
app = SEMWPConfig(master=root)
app.mainloop()
    

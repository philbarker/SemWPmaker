#!/usr/bin/env python3
from rdfFuncs import SemWP 
from tkinter import *
from tkinter.filedialog import *
from tkinter.ttk import *
from rdflib import URIRef, Namespace, Literal
from rdflib.namespace import RDF, RDFS
schema = Namespace(u'http://schema.org/')
semwp_ns = Namespace(u'http://ns.pjjk.net/semwp')

class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!

    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    * from http://tkinter.unpythonic.net/wiki/VerticalScrolledFrame
    
    """
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        vscrollbar = Scrollbar(self, orient=VERTICAL)
        vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=vscrollbar.set)
        canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        vscrollbar.config(command=canvas.yview)

        # reset the view
        canvas.xview_moveto(0)
        canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = interior = Frame(canvas)
        interior_id = canvas.create_window(0, 0, window=interior,
                                           anchor=NW)

        # track changes to the canvas and frame width and sync them,
        # also updating the scrollbar
        def _configure_interior(event):
            # update the scrollbars to match the size of the inner frame
            size = (interior.winfo_reqwidth(), interior.winfo_reqheight())
            canvas.config(scrollregion="0 0 %s %s" % size)
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the canvas's width to fit the inner frame
                canvas.config(width=interior.winfo_reqwidth())
        interior.bind('<Configure>', _configure_interior)

        def _configure_canvas(event):
            if interior.winfo_reqwidth() != canvas.winfo_width():
                # update the inner frame's width to fill the canvas
                canvas.itemconfigure(interior_id, width=canvas.winfo_width())
        canvas.bind('<Configure>', _configure_canvas)

        return

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
        if self.rdfsName.get() is not None:
            self.write_btn.config(command=self.write, state=NORMAL)

    def write(self):
        self.rdfschema.write_metafile(c=self.rdfschema.thing)

    def update_propertyinfo(self):
        item = self.classtree.focus()
        itemref = URIRef(item)
        for child in self.propertiesframe.interior.winfo_children():
            child.destroy()
        showpropertyinfo = False
        for inflag in self.rdfschema.g.objects(subject=itemref, predicate=semwp_ns.include):
            if inflag == Literal('True'):
                showpropertyinfo = True
        if showpropertyinfo:
            pcount = 0
            self.includepropsflags.clear
            for p in self.rdfschema.properties(itemref):
                proplabel = self.rdfschema.resource_label(p, lang='en')
                self.includepropsflags[proplabel] = dict()
                heading = self.rdfschema.resource_label(p, lang='en') \
                        + '. Range includes: '
                rcount=1
                self.includepropsflags[proplabel]['text'] = StringVar()
                Checkbutton(self.propertiesframe.interior, text='text',
                            variable=self.includepropsflags[proplabel]['text']
                             ).grid(row=2*pcount+1, column=rcount, sticky=NW)

                for c in self.rdfschema.g.objects(p, schema.rangeIncludes):
                    heading = heading +' '+ self.rdfschema.resource_label(c, lang='en')
                    
                    if c == schema.Text:
                        rcount+=1
                        self.includepropsflags[proplabel]['long text'] = StringVar()
                        Checkbutton(self.propertiesframe.interior, text='long text',
                                    variable=self.includepropsflags[proplabel]['long text']
                                    ).grid(row=2*pcount+1, column=rcount, sticky=NW)
                    else:
                        rcount+=1
                        rangelabel = self.rdfschema.resource_label(c, lang='en')
                        self.includepropsflags[proplabel][rangelabel] = StringVar()
                        Checkbutton(self.propertiesframe.interior, text=rangelabel,
                                    variable=self.includepropsflags[proplabel][rangelabel]
                                    ).grid(row=2*pcount+1, column=rcount, sticky=NW)
                        
                Label(self.propertiesframe.interior, text=heading, padding='3 0 0 0'
                      ).grid(row=2*pcount, column=0, columnspan=10, sticky=NW)
                Label(self.propertiesframe.interior, text='Include as:', padding='32 0 0 9'
                      ).grid(row=2*pcount+1, column=0, sticky=NW)
                
                pcount += 1
#        self.propertiesframe.columnconfigure(1, weight=1)
                
                    

    def update_classinfo(self, event):
        item = self.classtree.focus()
        itemref = URIRef(item)
        self.className.set(self.rdfschema.resource_label(itemref, lang='en'))
        self.classDescrTxt.configure(state = NORMAL)
        self.classDescrTxt.delete('1.0', END)
        self.classDescrTxt.insert(END, self.rdfschema.resource_comment(itemref, lang='en'))
        self.classDescrTxt.configure(state = DISABLED)
        # the following deals with setting the includeclassflag which determines whether
        # the class if greyed out or not, setting the includeclass string variable which
        # determines the check button state, based on the include property of the class in
        # the graph. If the include property is not present for the class it is set to
        # 'include' and the flag & checkbutton set accordingly.
        count = 0
        for o in self.rdfschema.g.objects(itemref, semwp_ns.include):
            if o == Literal('False'):
                 self.includeclass.set(0)
                 count = 1
                 self.includeclassflag.set('was '+o.toPython())
                 self.classtree.item(itemref, tags=('notinclude'))
                 self.classtree.tag_configure('notinclude', foreground='gray')
            elif o == Literal('True'):
                 self.includeclass.set(1)
                 count = 1
                 self.includeclassflag.set('was '+o.toPython())
                 self.classtree.item(itemref, tags=('include'))
                 self.classtree.tag_configure('include', foreground='black')
        if count == 0:
            self.rdfschema.set_include_true(itemref)
            self.includeclass.set(1)
            self.includeclassflag.set('count 0 set to true')
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

        for o in self.rdfschema.g.objects(itemref, semwp_ns.include):
            self.includeclassflag.set(o.toPython())
        self.update_propertyinfo()            

        
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
        self.classtree.tag_configure('include', foreground='black')
        self.classtree.tag_configure('notinclude', foreground='gray')
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
#        includeclassflag_lbl=Label(classinfoframe, textvariable= self.includeclassflag,
#                                   background='#bbb', relief=SUNKEN, padding='3 3 3 3',
#                                   font='bold', width=25)
#        includeclassflag_lbl.grid(row=4, column=1, sticky=EW)
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

    def create_template_frame(self, master:Notebook):
        templateframe = Frame(master, padding = '', width=600, height=400)
        self.template_txt.grid(row=1, column=1,
                               in_=templateframe,
                               sticky=(N+E+S+W))
        self.template_txt.lift(templateframe)
        ysb = Scrollbar(templateframe, orient='vertical', command=self.template_txt.yview)
        ysb.grid(row=1, column=2, sticky=NS)
        self.template_txt.configure(yscrollcommand=ysb.set)        
        templateframe.columnconfigure(1, weight=1)
        templateframe.rowconfigure(1, weight=1)
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
        # and values set when available.
        self.rdfs_btn = Button(master, text="Open\nRDFS",
                               command=self.open_rdfs)
        self.template_btn = Button(master, text="Open\nTemplate",
                                   command=self.open_template)
        self.write_btn = Button(master, text="Write\nPHP",
                                command='', state=DISABLED)
        self.classtree = Treeview(master)
        self.rdfsFileName = StringVar()
        self.rdfsName = StringVar()
        self.templateFileName = StringVar()
        self.template_txt = Text(master,
                                         background='#fff',
                                         relief=SUNKEN, 
                                         wrap = NONE,
                                         width = 40,
                                         height = 40) 
        self.className = StringVar()
        self.classDescrTxt = Text(master,
                                  background='#bbb',
                                  relief=SUNKEN, 
                                  wrap=WORD,
                                  height=4,
                                  width=60,
                                  state = DISABLED)
        self.propertiesframe = VerticalScrolledFrame(master,
                                     relief=SUNKEN,
                                     padding='3 3 3 3')
                             # the (variable) widgets in this will have info
                             # about properties of the selected class
        self.includeclass = IntVar()
        self.includeclass.set(1)
        self.includeclassflag = StringVar()
        self.includepropsflags=dict()
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
#s = Style()
#s.configure('Treeview', foreground='red')

app = SEMWPConfig(master=root)
app.mainloop()
    

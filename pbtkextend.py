from tkinter import Frame, Checkbutton, Scrollbar, Canvas, IntVar
from tkinter import VERTICAL,LEFT, RIGHT, BOTH, TRUE, FALSE, Y, NW

class CheckbuttonGroup(Frame):

    r"""CheckbuttonGroup: create a tk frame with a group of tk checkbuttons packed in it
    Options: master, a tk widget into which to put the checkbutton frame;
      names, a list of strings to use as the names of the checkbuttons;
      command, name of a function to be run when any checkbutton is clicked;
      side: the side on which to pack the buttons (e.g. TOP or LEFT);
      anchor: where to anchor the check buttons;
      *args & **kw options for the frame.
    Properties: ckbtns, a dict of tk checkbuttons, keys are the names list;
      vals, a dict of values of the checkbuttons [0|1], keys are the names list.
    """
    def __init__(self, master=None, names=[], command='',
                 side=None, anchor=None, *args, **kw):
        Frame.__init__(self, master, *args, **kw)
        self.chkbtns=dict()
        self.vals=dict()
        for name in names:
            self.vals[name] = IntVar()
            self.chkbtns[name] = Checkbutton(self, text=name,
                                        variable=self.vals[name],
                                        command=command)
            self.chkbtns[name].pack(side=side, anchor=anchor)

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

import SQLinventory as sq
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk


#continue work through all_tables
#fix on exit

TITLE_FONT = ("Myriad Pro", 18, "bold")


def multi_function(*functions): #for multiple functions inside one button
    def func(*args, **kwargs):
        values = None
        for function in functions:
            values = function(*args, **kwargs)
        return values
    return func


def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        tk.destroy()


class InventoryApp(tk.Tk):

    connection = sq.createDB('Z:\Inventory\InventoryGUI\inventory.db')

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.title('Amphenol Commercial I/O')
        self.iconbitmap('Amphenol-Icon.ico')

        self.frames = {}
        for F in (MainPage, MakeTables, TableList, PageTwo):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainPage")

    def show_frame(self, page_name):
        '''Show a frame for the given page name'''
        frame = self.frames[page_name]
        frame.tkraise()

    #on_exit = tk.protocol("WN_DELETE_WINDOW", on_closing())

class MainPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        title = tk.Label(self, text="Amphenol Sample Inventory Database", font=TITLE_FONT, fg='#0062a6')
        title.pack(side="top", fill="x", pady=10)

        make_tables = tk.Button(self, text='Make Tables',
                            command=lambda: controller.show_frame("MakeTables"))
        table_list = tk.Button(self, text="View Table List",
                            command=lambda: controller.show_frame("TableList"))
        button2 = tk.Button(self, text="Go to Page Two",
                            command=lambda: controller.show_frame("PageTwo"))
        close = tk.Button(self, text="Exit",
                            command=lambda: multi_function(InventoryApp.connection.commit(),
                                                  InventoryApp.connection.close(),
                                                  exit()))

        make_tables.place(rely=1.0, relx=1.0, x=0, y=0, anchor=tk.SE)
        table_list.pack()
        button2.pack()
        close.pack()


class MakeTables(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        title = tk.Label(self, text="Initialize Tables", font=TITLE_FONT, fg='#0062A6')
        title.pack(side='top', fill='x', pady=10)

        table_list = tk.Button(self, text='Initialize Table List',
                        command=lambda: sq.createTableList(InventoryApp.connection))
        table_list.pack(side='top')

        connectors_table = tk.Button(self, text='Initialize Connectors Table',
                        command=lambda: sq.createConnectorsTable(InventoryApp.connection))
        connectors_table.pack(side='top')

        home = tk.Button(self, text='Go to the main page',
                        command=lambda: controller.show_frame('MainPage'))
        home.pack()


class TableList(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        title = tk.Label(self, text="List of All Tables:", font=TITLE_FONT, fg='#0062A6')
        title.pack(side="top", fill="x", pady=10)



        #all_tables = tk.Label(self, text=)

        home = tk.Button(self, text="Go to the main page",
                           command=lambda: controller.show_frame("MainPage"))
        home.pack()


class PageTwo(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        title = tk.Label(self, text="This is page 2", font=TITLE_FONT)
        title.pack(side="top", fill="x", pady=10)
        home = tk.Button(self, text="Go to the main page",
                           command=lambda: controller.show_frame("MainPage"))
        home.pack()


if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()

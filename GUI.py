import SQLinventory as sq
import tkinter as tk
# from tkinter import messagebox
# from tkinter import ttk
from sqlite3 import OperationalError
import openpyxl as xl


# from functools import reduce


TITLE_FONT = ("Myriad Pro", 18, "bold")


def multi_function(*functions):  # for multiple functions inside one button
    def func(*args, **kwargs):
        values = None
        for function in functions:
            values = function(*args, **kwargs)
        return values

    return func


"""
def on_closing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        tk.destroy()
"""


class InventoryApp(tk.Tk):
    connection = sq.createDB('Z:\Inventory\InventoryGUI\inventory.db')
    try:
        work_book = xl.load_workbook('inventory.xlsx')
    except FileNotFoundError:
        workbook = xl.Workbook()

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
        for F in (MainPage, MakeTables, TableList, ViewTables):
            page_name = F.__name__
            frame = F(parent=container, controller=self)
            self.frames[page_name] = frame

            # put all of the pages in the same location;
            # the one on the top of the stacking order
            # will be the one that is visible.
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("MainPage")

    def show_frame(self, page_name):
        # Show a frame for the given page name
        frame = self.frames[page_name]
        frame.tkraise()

        # on_exit = tk.protocol("WN_DELETE_WINDOW", on_closing())


class MainPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        # self.configure(background='#0062a6')

        title = tk.Label(self, text="Amphenol Sample Inventory Database", font=TITLE_FONT, fg='#0062a6')
        title.pack(side="top", fill="x", pady=10)

        make_tables = tk.Button(self, text='Make Tables',
                                command=lambda: controller.show_frame("MakeTables"))
        table_list = tk.Button(self, text="View Table List",
                               command=lambda: controller.show_frame("TableList"))
        button2 = tk.Button(self, text="Go to Table Contents",
                            command=lambda: controller.show_frame("ViewTables"))
        close = tk.Button(self, text="Exit",
                          command=lambda: multi_function(InventoryApp.connection.commit(),
                                                         InventoryApp.connection.close(),
                                                         exit()))

        make_tables.place(rely=1.0, relx=1.0, x=0, y=0, anchor=tk.SE)
        table_list.pack()
        button2.pack()
        close.pack(side='bottom')


class MakeTables(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        title = tk.Label(self, text="Initialize Tables", font=TITLE_FONT, fg='#0062A6')
        title.grid(row=0, column=0, sticky=tk.N, pady=10, columnspan=4)

        table_list = tk.Button(self, text='Initialize Table List',
                               command=lambda: sq.createTableList(InventoryApp.connection))
        table_list.grid(row=1, column=1, sticky=tk.W + tk.E)

        connectors_table = tk.Button(self, text='Initialize Connectors Table',
                                     command=lambda: sq.createConnectorsTable(InventoryApp.connection))
        connectors_table.grid(row=2, column=1, sticky=tk.W + tk.E)

        connectors_history_table = tk.Button(self, text='Initialize Connectors History Table',
                                             command=lambda: sq.createConnectorsHistoryTable(InventoryApp.connection))
        connectors_history_table.grid(row=3, column=1, sticky=tk.W + tk.E)

        sample_cases_table = tk.Button(self, text='Initialize Sample Cases Table',
                                       command=lambda: sq.createSampleCasesTable(InventoryApp.connection))
        sample_cases_table.grid(row=4, column=1, sticky=tk.W + tk.E)

        sample_cases_history_table = tk.Button(self, text='Initialize Sample Cases History Table',
                                               command=lambda: sq.createSampleCasesHistoryTable(
                                                   InventoryApp.connection))
        sample_cases_history_table.grid(row=5, column=1, sticky=tk.W + tk.E)

        home = tk.Button(self, text='Go to the main page',
                         command=lambda: controller.show_frame('MainPage'))

        home.grid(row=6, column=0, sticky=tk.S)


class TableList(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller
        title = tk.Label(self, text="List of All Tables:", font=TITLE_FONT, fg='#0062A6')
        title.grid(row=0, column=4, pady=10)

        counter = 2
        blank_item = tk.Label(self, text='1111111111111111111111', fg='#f0f0ed')
        blank_item.grid(row=1, column=3, sticky=tk.W+tk.E)

        blank_item_1 = tk.Label(self, text='1', fg='#f0f0ed')
        blank_item_1.grid(row=1, column=2, sticky=tk.W+tk.E)

        try:
            get_tables = InventoryApp.connection.execute('SELECT * FROM TableList')

            table_map = ' '.join(map(lambda x: x[0], get_tables.description))
            table_headings = tk.Label(self, text=table_map)
            table_headings.grid(row=1, column=4, sticky=tk.W)

            for item in get_tables:
                tk.Label(self, text=item).grid(row=counter, column=4, sticky=tk.W)
                counter += 1

        except OperationalError:
            unable_to_open = tk.Label(self, text='Unable to open TableList table')
            unable_to_open.grid(column=1)

        home = tk.Button(self, text="Go to the main page",
                         command=lambda: controller.show_frame("MainPage"))
        home.grid(row=(counter + 1), sticky=tk.S)


class ViewTables(tk.Frame):
    def __init__(self, parent, controller):

        # could be useless
        self.entry_temp_list = []
        self.query_temp_values = None

        tk.Frame.__init__(self, parent)
        self.controller = controller
        title = tk.Label(self, text="View Table Contents", font=TITLE_FONT, fg='#0062a6')
        title.grid(row=0, column=0, pady=10, columnspan=4)

        info_grid = tk.Label(self, text='', justify='left')
        info_grid.grid(row=3, columnspan=4, rowspan=4, pady=10)

        view_connectors = tk.Button(self, text='View Connectors',
                                    command=lambda: info_grid.configure(
                                        text=sq.view_values(
                                            InventoryApp.connection.execute(
                                                'SELECT * FROM Connectors'))))
        view_connectors.grid(row=1, column=0, pady=10, sticky=tk.W + tk.E)

        view_connectors_history = tk.Button(self, text='View Connectors History',
                                            command=lambda: info_grid.configure(
                                                text=sq.view_values(
                                                    InventoryApp.connection.execute(
                                                        'SELECT * FROM ConnectorsHistory'))))
        view_connectors_history.grid(row=1, column=1, sticky=tk.W + tk.E)

        view_sample_cases = tk.Button(self, text='View Sample Cases',
                                      command=lambda: info_grid.configure(
                                          text=sq.view_values(
                                              InventoryApp.connection.execute(
                                                  'SELECT * FROM SampleCases'))))
        view_sample_cases.grid(row=1, column=2, sticky=tk.W + tk.E)

        view_sample_cases_history = tk.Button(self, text='View Sample Cases History',
                                              command=lambda: info_grid.configure(
                                                  text=sq.view_values(
                                                      InventoryApp.connection.execute(
                                                          'SELECT * FROM SampleCasesHistory'))))
        view_sample_cases_history.grid(row=1, column=3, sticky=tk.W + tk.E)

        variable_lookup_text = tk.Label(self, text='Variable Lookup')
        variable_lookup_text.grid(row=2, column=0, sticky=tk.W + tk.E)

        variable_lookup_column_label = tk.Label(self, text='Type')
        variable_lookup_column_label.grid(row=2, column=1, sticky=tk.W+tk.E)

        variable_lookup_column = tk.Entry(self, width=30)
        variable_lookup_column.insert(0, "Input specifier type")
        variable_lookup_column.grid(row=3, column=1)

        variable_lookup_criteria_label = tk.Label(self, text='Criteria')
        variable_lookup_criteria_label.grid(row=2, column=2, sticky=tk.E+tk.W)

        variable_lookup_criteria = tk.Entry(self, width=30)
        variable_lookup_criteria.insert(0, "Input specifier value")
        variable_lookup_criteria.grid(row=3, column=2)

        variable_lookup_table = tk.Entry(self, width=30)
        variable_lookup_table.insert(0, 'Input table')
        variable_lookup_table.grid(row=3, column=3)

        variable_lookup_table_label = tk.Label(self, text='Table')
        variable_lookup_table_label.grid(row=2, column=3, sticky=tk.E+tk.W)

        def get_entry(*args):
            if args is not None:
                self.entry_temp_list = []
                for item in args:
                    self.entry_temp_list.append(item.get())
                    item.delete(0, tk.END)
                refresh_entry()
            return self.entry_temp_list
            # could remove the temp list if found to be useless

        def refresh_entry():
            variable_lookup_column.insert(0, 'Input specifier type')
            variable_lookup_criteria.insert(0, 'Input specifier value')
            variable_lookup_table.insert(0, 'Input table')

        def print_to_excel(items):
            pass
            # write print to excel function

        enter_button = tk.Button(self, text="Enter",
                                 command=lambda: info_grid.configure(text=sq.query_table(InventoryApp.connection,
                                                                                         get_entry(
                                                                                             variable_lookup_column,
                                                                                             variable_lookup_criteria,
                                                                                             variable_lookup_table))))
        empty_row = tk.Label(self, text='1', fg='#f0f0ed')
        empty_row.grid(row=5, column=0, sticky=tk.W+tk.E+tk.N+tk.S)

        empty_row_1 = tk.Label(self, fg='#f0f0ed', text='1')
        empty_row_1.grid(row=6, column=0, sticky=tk.W+tk.E+tk.N+tk.S)

        enter_button.grid(row=7, column=3, sticky=tk.W + tk.E)

        home = tk.Button(self, text="Go to the main page",
                         command=lambda: controller.show_frame("MainPage"))
        home.grid(column=0, row=7)


if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()

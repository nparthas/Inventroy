import SQLinventory as sq
import tkinter as tk
from tkinter import messagebox
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
        work_book = xl.Workbook()

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

        # the container is where we'll stack a bunch of frames
        # on top of each other, then the one we want visible
        # will be raised above the others
        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        if not self.connection:
            messagebox.showwarning('ERROR', 'Unable to connect to database')

        if self.connection:
            self.protocol("WM_DELETE_WINDOW", self.on_closing)

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
            frame.columnconfigure(0, weight=1)
            frame.rowconfigure(0, weight=1)
            # frame.configure(background='#ebf1f8') FIX LATER

        self.show_frame("MainPage")

    def show_frame(self, page_name):
        # Show a frame for the given page name
        frame = self.frames[page_name]
        frame.tkraise()

    def on_closing(self):
        # if messagebox.askokcancel("Quit", "Do you want to quit?"):
        InventoryApp.connection.commit()
        InventoryApp.connection.close()
        InventoryApp.work_book.save('Inventory.xlsx')

        self.destroy()


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

        if InventoryApp.connection:
            close = tk.Button(self, text="Exit",
                              command=lambda: InventoryApp.on_closing(app))
        else:
            close = tk.Button(self, text='Exit', command=lambda: multi_function(
                InventoryApp.work_book.save('Inventory.xlsx'), exit()))

        make_tables.place(rely=1.0, relx=1.0, x=0, y=0, anchor=tk.SE)
        table_list.pack()
        button2.pack()
        close.pack(side='bottom')


class MakeTables(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        title = tk.Label(self, text="Initialize Tables", font=TITLE_FONT, fg='#0062A6')
        title.pack(anchor=tk.N, side=tk.TOP, fill=tk.X, pady=(5, 10))

        result = tk.Label(self, text="")
        result.pack(side=tk.TOP, pady=(0, 10))

        button_frame = tk.Frame(self)
        button_frame.pack(anchor=tk.CENTER, side=tk.TOP, fill=tk.X)

        table_list = tk.Button(button_frame, text="Initialize Table List", width=40,
                               command=lambda: result.configure(text=sq.createTableList(InventoryApp.connection)))

        connectors_table = tk.Button(button_frame, text='Initialize Connectors Table', width=40,
                                     command=lambda: result.configure(
                                         text=sq.createConnectorsTable(InventoryApp.connection)))

        connectors_history_table = tk.Button(button_frame, text="Initialize Connectors History Table", width=40,
                                             command=lambda: result.configure(
                                                 text=sq.createConnectorsHistoryTable(InventoryApp.connection)))

        sample_cases_table = tk.Button(button_frame, text="Initialize Sample Cases Table", width=40,
                                       command=lambda: result.configure(
                                           text=sq.createSampleCasesTable(InventoryApp.connection)))

        sample_cases_history_table = tk.Button(button_frame, text="Initialize Sample Cases History Table", width=40,
                                               command=lambda: result.configure(
                                                   text=sq.createSampleCasesHistoryTable(InventoryApp.connection)))

        table_list.pack()
        connectors_table.pack()
        connectors_history_table.pack()
        sample_cases_table.pack()
        sample_cases_history_table.pack()

        home = tk.Button(self, text="Go to the main page", command=lambda: controller.show_frame("MainPage"))
        home.pack(anchor=tk.S, side=tk.LEFT, pady=(15, 0))


class TableList(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)
        self.controller = controller

        if InventoryApp.connection.execute("SELECT MAX(TableListID) FROM TableList").fetchall()[0][0] > 10:
            InventoryApp.connection.execute('''
                DELETE FROM TableList
                WHERE TableListID NOT IN (
                    SELECT MAX(TableListID)
                    FROM TableList
                    GROUP BY Name)''')

        def refresh_values():
            try:
                headings = sq.query_headings(InventoryApp.connection, 'TableList')

                values = sq.format_values(
                    sq.retrieve_values(
                        InventoryApp.connection.execute('SELECT * FROM TableList')))
                table_contents.configure(text=headings + values)

            except OperationalError:
                unable_to_open_error = tk.Label(table_frame, text='Unable to open TableList table')
                unable_to_open_error.pack()

        title = tk.Label(self, text="List of All Tables:", font=TITLE_FONT, fg='#0062A6')
        title.pack(anchor=tk.N, side=tk.TOP, fill=tk.X, pady=(5, 20))

        table_frame = tk.Frame(self)
        table_frame.pack(anchor=tk.CENTER, side=tk.TOP, fill=tk.X)

        try:
            table_headings = sq.query_headings(InventoryApp.connection, 'TableList')

            table_values = sq.format_values(
                sq.retrieve_values(
                    InventoryApp.connection.execute('SELECT * FROM TableList')))
            table_contents = tk.Label(table_frame, text=table_headings + table_values, justify='left')
            table_contents.pack(anchor=tk.N, side=tk.TOP, fill=tk.X)

        except (OperationalError, AttributeError):
            unable_to_open = tk.Label(table_frame, text='Unable to open TableList table')
            unable_to_open.pack()

        home = tk.Button(self, text="Go to the main page", command=lambda: controller.show_frame("MainPage"))
        home.pack(anchor=tk.S, side=tk.LEFT)

        refresh = tk.Button(self, text='Refresh list', command=lambda: refresh_values())
        refresh.pack(anchor=tk.S, side=tk.RIGHT)


class ViewTables(tk.Frame):  # Rewrite so that values show up in a grid
    def __init__(self, parent, controller):

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

        def on_frame_configure(event):
            info_grid_canvas.configure(scrollregion=info_grid_canvas.bbox("all"))

        def refresh_values(connection_object):
            for widget in info_grid_frame.winfo_children():
                widget.destroy()

            if connection_object == 'Error (Check Capitalization)':
                spot = tk.Label(info_grid_frame, text="Error (Check Capitalization)")
                spot.pack(anchor=tk.N, side=tk.TOP)
                return None

            if connection_object != '':
                i = 0
                j = 0
                for item in connection_object.description:
                    spot = tk.Label(info_grid_frame, text=item[0])
                    spot.grid(row=i, column=j, sticky=tk.N + tk.E + tk.S + tk.W, padx=7)
                    j += 1
                i += 1
                j = 0

                for row in connection_object:
                    for value in row:
                        spot = tk.Label(info_grid_frame, text=value)
                        spot.grid(row=i, column=j, sticky=tk.N + tk.E + tk.S + tk.W)
                        if i % 2 == 1:
                            spot.configure(bg='#b8e1eb')
                        j += 1
                    i += 1
                    j = 0

        def print_to_excel():

            work_sheet = InventoryApp.work_book.create_sheet()

            for widget in info_grid_frame.winfo_children():
                widget['text']
                pass

            # FINISH

        tk.Frame.__init__(self, parent)
        self.controller = controller

        title_frame = tk.Frame(self)
        title_frame.pack(anchor=tk.N, side=tk.TOP, fill=tk.X, pady=(5, 20))

        home_frame = tk.Frame(self)
        home_frame.pack(anchor=tk.S, side=tk.BOTTOM, fill=tk.X)

        view_tables_frame = tk.Frame(self)
        view_tables_frame.pack(anchor=tk.N, side=tk.TOP, fill=tk.X)

        for i in range(4):
            view_tables_frame.columnconfigure(i, weight=2)

        entry_frame = tk.Frame(self)
        entry_frame.pack(anchor=tk.N, side=tk.TOP, pady=15, fill=tk.X)

        for i in range(4):
            entry_frame.columnconfigure(i, weight=2)

        info_grid_canvas = tk.Canvas(self, borderwidth=0)

        info_grid_frame = tk.Frame(info_grid_canvas)
        info_grid_frame.pack(anchor=tk.N, side=tk.TOP, fill=tk.BOTH)

        info_grid_scrollbar = tk.Scrollbar(self, orient='vertical', command=info_grid_canvas.yview)

        info_grid_canvas.configure(yscrollcommand=info_grid_scrollbar.set)

        info_grid_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        info_grid_canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        info_grid_canvas.create_window((4, 4), window=info_grid_frame, anchor=tk.NW, tags='info_grid_frame')

        info_grid_frame.bind("<Configure>", on_frame_configure)

        home = tk.Button(home_frame, text="Go to the main page", command=lambda: controller.show_frame("MainPage"))
        home.pack(anchor=tk.S, side=tk.LEFT)

        title = tk.Label(title_frame, text='View Table Contents', font=TITLE_FONT, fg='#0062A6')
        title.pack()

        view_connectors = tk.Button(view_tables_frame, text='View Connectors',
                                    command=lambda: refresh_values(
                                        InventoryApp.connection.execute('SELECT * FROM Connectors')))
        view_connectors.grid(column=0, row=0, sticky=tk.W + tk.E)

        view_connectors_history = tk.Button(view_tables_frame, text='View Connectors History',
                                            command=lambda: refresh_values(
                                                InventoryApp.connection.execute(
                                                    'SELECT * FROM ConnectorsHistory')))
        view_connectors_history.grid(column=2, row=0, sticky=tk.W + tk.E)

        view_sample_cases = tk.Button(view_tables_frame, text='View Sample Cases',
                                      command=lambda: refresh_values(
                                          InventoryApp.connection.execute(
                                              'SELECT * FROM SampleCases')))
        view_sample_cases.grid(column=1, row=0, sticky=tk.W + tk.E)

        view_sample_cases_history = tk.Button(view_tables_frame, text='View Sample Cases History',
                                              command=lambda: refresh_values(
                                                  InventoryApp.connection.execute(
                                                      'SELECT * FROM SampleCasesHistory')))
        view_sample_cases_history.grid(column=3, row=0, sticky=tk.W + tk.E)

        variable_lookup_text = tk.Label(entry_frame, text='Variable Lookup')
        variable_lookup_text.grid(column=0, row=0, sticky=tk.W + tk.E, padx=(0, 15))

        variable_lookup_column_label = tk.Label(entry_frame, text="Type")
        variable_lookup_column_label.grid(column=1, row=0, sticky=tk.W)

        variable_lookup_criteria_label = tk.Label(entry_frame, text="Criteria")
        variable_lookup_criteria_label.grid(column=2, row=0, sticky=tk.W)

        variable_lookup_table_label = tk.Label(entry_frame, text="Table")
        variable_lookup_table_label.grid(column=3, row=0, sticky=tk.W)

        variable_lookup_column = tk.Entry(entry_frame, width=30)
        variable_lookup_column.insert(0, "Input specifier type")
        variable_lookup_column.grid(column=1, row=1, sticky=tk.W)

        variable_lookup_criteria = tk.Entry(entry_frame, width=30)
        variable_lookup_criteria.insert(0, 'Input specifier value')
        variable_lookup_criteria.grid(column=2, row=1, sticky=tk.W)

        variable_lookup_table = tk.Entry(entry_frame, width=30)
        variable_lookup_table.insert(0, 'Input table')
        variable_lookup_table.grid(column=3, row=1, sticky=tk.W)

        enter_button = tk.Button(entry_frame, text='Enter',
                                 command=lambda: refresh_values(
                                     sq.query_table(InventoryApp.connection, get_entry(
                                         variable_lookup_column,
                                         variable_lookup_criteria,
                                         variable_lookup_table))))
        enter_button.bind("<Return>", (lambda event: refresh_values(
                                     sq.query_table(InventoryApp.connection, get_entry(
                                         variable_lookup_column,
                                         variable_lookup_criteria,
                                         variable_lookup_table)))))
        enter_button.grid(column=3, row=2, sticky=tk.W + tk.E)

        erase_button = tk.Button(entry_frame, text='Erase', command=lambda: refresh_values(''))
        erase_button.bind("<Return>", lambda event: refresh_values(""))

        erase_button.grid(column=3, row=3, sticky=tk.W + tk.E)

if __name__ == "__main__":
    app = InventoryApp()
    app.mainloop()


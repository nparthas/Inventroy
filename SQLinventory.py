# https://pythontips.com/2013/07/30/20-python-libraries-you-cant-live-without/
# MyClass(self, required=True, someNumber=<default>, *args, **kwargs)
# http://www.informit.com/articles/article.aspx?p=2314818
# https://docs.djangoproject.com/en/1.10/intro/tutorial04/
# https://devcenter.heroku.com/articles/deploying-python
# https://www.tutorialspoint.com/sqlite/sqlite_python.htm
# https://maryrosecook.com/blog/post/a-practical-introduction-to-functional-programming
# scheme
# https://www.cs.kent.ac.uk/people/staff/dat/miranda/whyfp90.pdf
# pyqt
# http://www.learncpp.com/cpp-tutorial/71-function-parameters-and-arguments/
# http://www.pyimagesearch.com/2017/04/24/eye-blink-detection-opencv-python-dlib/
# https://github.com/PyMySQL/PyMySQL
# https://medium.com/@RobSm/deep-learning-prerequisites-logistic-regression-in-python-bcdb4c561358
# http://www.holehouse.org/mlclass/
# http://www.kdnuggets.com/2015/11/seven-steps-machine-learning-python.html

# navigate to z-drive: cd\ then Z:
# django innit Z:\Inventory>C:\Users\neilp\AppData\Local\Programs\Python\Python36-32\Scripts\dj
# django-admin.exe startproject mysite
# network access host through address 10.5.112.99:8000

import sqlite3 as sq
import time
from sqlite3 import OperationalError
import re


# Dates in DD-MM-YYYY
# Create sample case inventory + rewrite maps


def createDB(dbfile):
    try:
        connection = sq.connect(dbfile)
        print("Opened database successfully")
        return connection

    except OperationalError:
        print("Unable to initialize.")
        return False


def createTableList(connection):
    if not exists_table(connection, 'TableList'):
        connection.execute(''' CREATE TABLE TableList
            (TableListID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name TEXT NOT NULL,
            DateModified TEXT); ''')
        connection.commit()
        print('Table created successfully')
        return 'TableList table created successfully'

    else:
        print('Table already exists')
        return 'TableList table already exists'


def createConnectorsTable(connection):
    if not exists_table(connection, 'Connectors'):
        connection.execute(''' CREATE TABLE Connectors
            ( ConnectorID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL UNIQUE,
            CurrentAmount INT NOT NULL,
            Series TEXT,
            Family TEXT,
            PairName TEXT,
            BoxAmount INT,
            CartonAmount INT,
            DateOrdered TEXT,
            ProductInfo TEXT,
            OfficeAmount INT,
            StorageAmount INT,
            SampleCase TEXT);''')  # sample case name goes in SampleCase COL

        today = time.strftime('%d-%m-%y')
        todayTuple = (today,)
        connection.execute("INSERT INTO TableList (Name, DateModified) VALUES ('Connectors', ? );", todayTuple)
        connection.commit()
        print('Table created successfully')
        return 'Connectors table created successfully'

    else:
        print('Table already exists')
        return "Connectors table already exists"


def createConnectorsHistoryTable(connection):
    if not exists_table(connection, 'ConnectorsHistory'):
        connection.execute(''' CREATE TABLE ConnectorsHistory
            (HistoryID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Amount INT NOT NULL,
            Date TEXT NOT NULL,
            Difference INT,
            FOREIGN KEY(Name) REFERENCES Connectors(Name)); ''')

        today = time.strftime('%d-%m-%y')
        todayTuple = (today,)
        connection.execute("INSERT INTO TableList (Name, DateModified) VALUES ('ConnectorsHistory', ? );", todayTuple)
        connection.commit()
        print("Table created successfully")
        return 'ConnectorsHistory table created successfully'
    else:
        print('Table already exists')
        return 'ConnectorsHistory table already exists'


def createSampleCasesTable(connection):
    if not exists_table(connection, 'SampleCases'):
        connection.execute('''CREATE TABLE SampleCases
            ( SampleCaseID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL UNIQUE,
            Amount INT,
            Date TEXT ); ''')

        today = time.strftime('%d-%m-%y')
        todayTuple = (today,)

        connection.execute("INSERT INTO TableList (Name, DateModified) VALUES ('SampleCases', ? );", todayTuple)
        connection.commit()
        print('Table created successfully')
        return 'SampleCases table created successfully'
    else:
        print('Table already exists')
        return 'SampleCases table already exists'


def createSampleCasesHistoryTable(connection):
    if not exists_table(connection, 'SampleCasesHistory'):
        connection.execute(''' CREATE TABLE SampleCasesHistory
            (SampleCaseHistoryID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Amount INT NOT NULL,
            Date TEXT NOT NULL,
            Difference INT,
            FOREIGN KEY(Name) REFERENCES SampleCases(Name)); ''')

        today = time.strftime('%d-%m-%y')
        todayTouple = (today,)
        connection.execute("INSERT INTO TableList (Name, DateModified) VALUES ('SampleCasesHistory', ? );", todayTouple)
        connection.commit()
        print("Table created successfully")
        return 'SampleCasesHistory table created successfully'
    else:
        print('Table already exists')
        return 'SampleCasesHistory table already exists'


def create_changelog_table(connection):
    if not exists_table(connection, 'Changelog'):
        connection.execute('''CREATE TABLE Changelog
            (ChangelogID INTEGER PRIMARY KEY,
            TableName TEXT NOT NULL,
            Statement TEXT NOT NULL,
            DATE TEXT NOT NULL,
            FOREIGN KEY (TableName) REFERENCES TableList(Name));''')

        today = time.strftime('%d-%m-%y')
        todayTouple = (today,)
        connection.execute("INSERT INTO TableList (Name, DateModified) VALUES ('Changelog', ? );", todayTouple)
        connection.commit()
        print("Table created successfully")
        return 'Changelog table created successfully'

    else:
        print('Table already exists')
        return 'Changelog table already exists'


def fillTable(dict, connection, tableName):

    """
    Abstract using dict:
    create the following functions and call them in this function

     return {
     'Connectors' : fill_Connectors_table(),
     'ConnectorsHistory' : fill_ConnectorsHistory_table(),
     'SampleCases': fill_SampleCases_table(),
     'SampleCasesHistory' : fill_SampleCasesHistory_table()
     }[tableName]
    """

    try:
        keys = list(dict.keys())

        keySTR = ", ".join(keys)
        keySTR = '(' + keySTR + ')'

        values = str(list(dict.values()))
        valuesSTR = values.replace("'", '"')
        valuesSTR = valuesSTR.replace('[', '(')
        valuesSTR = valuesSTR.replace(']', ')')

        # DIFFERENTITATES BETWEEN ' AND " IN EXECUTE STATEMENT

        if tableName == 'Connectors':
            required_values = ('Name', 'CurrentAmount')
            entries = ('ConnectorID', 'Name', 'Series', 'CurrentAmount', 'Type', 'PairName', 'BoxAmount',
                       'CartonAmount', 'DateOrdered', 'ProductInfo', 'OfficeAmount', 'StorageAmount', 'SampleCase')

            if set(keys).issubset(set(entries)) and set(required_values).issubset(set(entries)):

                if connection.execute('''SELECT EXISTS
                        (SELECT 1 FROM Connectors WHERE Name = ?)''', (dict['Name'],)).fetchone()[0]:

                    insert_list = re.sub(r"[\[\]);]|UNION", "",
                                         str(list(zip(
                                             dict.keys(), dict.values()))).replace("',", "=").replace("('", ""),
                                         flags=re.IGNORECASE)

                    today = time.strftime('%d-%m-%y')

                    try:
                        try:
                            old_amount = connection.execute(
                                "SELECT CurrentAmount from Connectors WHERE Name = ?", (dict['Name'],)).fetchall()[0][0]

                        except OperationalError:
                            old_amount = 0

                        try:
                            history_amount = connection.execute('''
                            SELECT Amount
                            FROM ConnectorsHistory
                            WHERE Name  = ?
                            AND HistoryID =(SELECT MAX(HistoryID)
                                            FROM ConnectorsHistory
                                            WHERE Name = ?)''', (dict['Name'], dict['Name'])).fetchone()[0]
                        except (OperationalError, TypeError):
                            history_amount = 0

                        difference = old_amount - history_amount

                        entry_tuple = (dict['Name'], old_amount, today, difference,)

                        connection.execute(
                            '''INSERT INTO ConnectorsHistory (Name, Amount, Date, Difference) VALUES
                            (?,?,?,?)''', entry_tuple)

                        print('Records successfully added to connectors history table')
                        # FIX
                        connection.execute("UPDATE Connectors SET {0} WHERE Name = ?".format(str(insert_list)),
                                           (dict['Name'],))
                        print('Records successfully updated in connectors table.')

                        return 'Records successfully added to History and Connectors table'

                    except OperationalError:
                        print('Operational Error, no records modified')
                        return 'Operational Error, no records modified'

                else:
                    try:
                        connection.execute('INSERT INTO Connectors {0} VALUES {1}'.format(keySTR, valuesSTR))
                        print('Records successfully added to connectors table.')

                        return 'Records successfully added to Connectors table'
                    except OperationalError:
                        print('Operational Error, no records modified')
                        return 'Operational Error no records modified'

            else:
                print("Invalid keys for update in Connectors table")
                return 'Invalid keys for update in Connectors table'

        elif tableName == 'ConnectorsHistory':
            entries = ('Name', 'Amount', 'Date', 'Difference')

            if (set(entries) - set(keySTR) == set()) or (set(entries) - set(keySTR) == {'Difference'}):
                # REDO STATEMENT

                connection.exectute('INSERT INTO ConnectorsHistory ' + keySTR + 'VALUES ' + valuesSTR)

                if 'Difference' not in keySTR:
                    try:
                        old_amount = connection.execute('''
                            SELECT Amount
                            FROM ConnectorsHistory
                            WHERE Name  = ?
                            AND HistoryID =(SELECT MAX(HistoryID)
                                            FROM ConnectorsHistory
                                            WHERE Name = ?)''', (dict['Name'], dict['Name'])).fetchall()[0][0]
                        # VERIFY THIS STATEMENT WORKS
                    except OperationalError:
                        old_amount = 0
                    connection.execute(
                        'UPDATE ConnectorsHistory SET Difference = {0} WHERE Name = {1}'.format(old_amount,
                                                                                                dict['Name']))
                    # TEST CONNECTORS HISTORY

                print('Records successfully added to ConnectorsHistory table.')
                return 'Records successfully added to Connectors History table'

            else:
                print('Invalid keys for update in ConnectorsHistory table')
                return 'Invalid keys for update in Connectors History table'

        elif tableName == 'SampleCases':
            entries = ('Name', 'Amount', 'Date')

            if set(keys).issubset(entries):

                if 'Date' not in dict.keys():
                    dict['Date'] = time.strftime('%d-%m-%y')

                if connection.execute('''SELECT EXISTS
                                    (SELECT 1 FROM SampleCases WHERE Name = ?)''', (dict['Name'],)).fetchall()[0][0]:

                    insert_list = re.sub(r"[\[\]);]|UNION", "",
                                         str(list(zip(
                                             dict.keys(), dict.values()))).replace("',", "=").replace("('", ""),
                                         flags=re.IGNORECASE)
                    try:
                        if connection.execute('''SELECT EXISTS
                                              (SELECT * FROM SampleCases WHERE Name = ?)''',
                                              (dict['Name'],)).fetchone()[0]:
                            old_amount = connection.execute(
                                "SELECT Amount FROM SampleCases WHERE Name = ?", (dict['Name'],)).fetchall()[0][0]

                        else:

                            old_amount = 0

                        try:
                            history_amount = connection.execute('''
                                SELECT AMOUNT
                                FROM SampleCasesHistory
                                WHERE Name = ?
                                AND SampleCaseHistoryID =  (SELECT MAX(SampleCaseHistoryID
                                                            FROM ConnectorsHistory
                                                            WHERE Name = ?''',
                                                                (dict['Name'], dict["Name"])).fetchall()[0][0]
                        except OperationalError:
                            history_amount = 0

                        difference = old_amount - history_amount

                        entry_tuple = (dict['Name'], old_amount, dict['Date'], difference)

                        connection.execute(
                            "INSERT INTO SampleCasesHistory (Name, Amount, Date, Difference) VALUES (?,?,?,?)",
                            entry_tuple)

                        print("Records successfully added to sample cases history table")

                        connection.execute(
                            "UPDATE SampleCases SET {0} WHERE Name = ?".format(str(insert_list)), (dict["Name"],))

                        connection.execute(
                            '''UPDATE Connectors
                               SET CurrentAmount = CurrentAmount - ?
                               WHERE SampleCase = ?''', (dict['Amount'], dict['Name']))

                        print("Records successfully added to the sample cases table")

                        return 'Records successfully added to SampleCases table, ' \
                               'and Connector amounts successfully reduced'

                        #  FIX DECREMENT STATEMENT ON CONNECTORS
                        #  TEST SAMPLECASES

                    except OperationalError:
                        print('Operational Error, no records modified')
                        return 'Operational Error, no records modified'
                else:
                    try:
                        connection.execute("INSERT INTO SampleCases {0} VALUES {1}".format(keySTR, valuesSTR))
                        connection.execute(""
                                           "UPDATE SampleCases "
                                           "SET Date = ? "
                                           "WHERE Name = ?", (dict['Date'], dict["Name"]))

                        connection.execute(
                            '''UPDATE Connectors
                               SET CurrentAmount = CurrentAmount - ?
                               WHERE SampleCase = ?''', (dict['Amount'], dict['Name']))

                        return 'Records successfully added to SampleCases table, ' \
                               'and Connector amounts successfully reduced'

                    except OperationalError:

                        print("Operational Error, no records modified")
                        return 'Operational Error, no records modified'
            else:
                print('Invalid keys for update in Sample Cases table')
                return 'Invalid keys for update in Samples Cases table'

        elif tableName == 'SampleCasesHistory':
            entries = ('Name', 'Amount', 'Date', 'Difference')

            if (set(entries) - set(keySTR) == set()) or (set(entries) - set(keySTR) == {'Difference'}):
                if 'Difference' not in keySTR:
                    try:
                        connection.execute('''SELECT Amount
                                           FROM SampleCasesHistory
                                           WHERE Name  = ?
                                           AND HistoryID = (SELECT MAX(HistoryID)
                                                            FROM SampleCasesHistory
                                                            WHERE Name = ? ''', (dict['Name'], dict['Name']))

                    except OperationalError:
                        connection.execute('UPDATE SampleCasesHistory SET Difference = 0 WHERE Name = ' + dict['Name'])

                connection.exectute('INSERT INTO SampleCasesHistory ' + keySTR + 'VALUES ' + valuesSTR)
                print('Records successfully added to SampleCasesHistory table.')
                return 'Records successfully added to Sample Cases History table'

            else:
                print('Invalid keys for update in SampleCasesHistory table')
                return 'Invalid keys for update in Sample Cases History table'
            #  TEST SAMPLECASESHISTORY
        else:
            print('Not a valid table')
            return 'Not a valid table'

    except AttributeError:
        pass


def exists_table(connection, table_name):
    query = "SELECT 1 FROM sqlite_master WHERE type='table' and name = ?"
    return connection.execute(query, (table_name,)).fetchone() is not None


def exists_column(connection, table_name, column_name):
    query = connection.execute("PRAGMA table_info({0})".format(table_name))
    flag = False
    for item in query:
        if column_name in item:
            flag = True
    return flag


def query_table(connection, entry_list):  # entry_list is column criteria value
    connection_object = 'Error (Check Capitalization)'
    if entry_list and exists_table(connection, entry_list[2]):
        if exists_column(connection, entry_list[2], entry_list[0]):
            entry_list[1] = ''.join(['*', entry_list[1], '*'])
            execute_tuple = (entry_list[1],)
            connection_object = connection.execute(
                "SELECT * FROM {0} WHERE {1} GLOB ?".format(entry_list[2], entry_list[0]), execute_tuple)
    return connection_object


def trim_TableList(connection):
    connection.execute('''
            DELETE FROM TableList
            WHERE TableListID NOT IN (
                SELECT MAX(TableListID)
                FROM TableList
                GROUP BY Name)''')
    connection.commit()


# for test use:

db = createDB('Z:\Inventory\InventoryGUI\inventory.db')
conn_dict = {'ConnectorID': 1, 'Name': 'MUSBR', 'CurrentAmount': 10}
his_dict = {'Name': 'MUSBR', 'Amount': 25}
sample_dict = {'Name': 'HARSH', 'Amount': 5}


"""
LEGACY FUNCTIONS

def view_values(connection_object):
    values = format_values(retrieve_values(connection_object))
    if values:
        return values
    else:
        return 'Table is empty'

def retrieve_values(connection_object):
    values_list = []

    for value in connection_object:
        values_list.append(value)
    return values_list

def has_values(connection, table):
    return bool(connection.execute('SELECT COUNT(*) FROM ' + table).fetchall()[0][0])

def format_values(values_list):
    characters = ['[', ']', '(', ')', "'", ',']

    values_str = str(values_list)
    for chars in characters:
        if chars in values_str:
            if chars == '(':
                values_str = values_str.replace(chars, '\n ')
            else:
                values_str = values_str.replace(chars, "")

    return values_str


def query_headings(connection, table_name):
    try:
        table_headings = connection.execute("SELECT * FROM {0}".format(table_name))
        return ' '.join(map(lambda x: x[0], table_headings.description)) + " \n"
    except OperationalError:
        return 'Invalid: '



"""

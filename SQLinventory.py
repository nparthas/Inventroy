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

# navigate to z-drive: cd\ then cd Z:
# django innit Z:\Inventory>C:\Users\neilp\AppData\Local\Programs\Python\Python36-32\Scripts\dj
# ango-admin.exe startproject mysite
# network access host through address 10.5.112.99:8000

import sqlite3 as sq
import time

# Dates in DD-MM-YYYY
# Create sample case inventory + rewrite maps


def tableExists(connection, tableName):

    table = (tableName,)
    cur = connection.execute("SELECT count(*) FROM sqlite_master WHERE TYPE='table' AND name=?", table)
    return cur.fetchone()[0]


def createDB(dbfile):
    try:
        connection = sq.connect(dbfile)
        print("Opened database successfully")
        return connection

    except Exception as e:
        print("Unable to initialize.")


def createTableList(connection):
    if not tableExists(connection, 'TableList'):
        connection.execute(''' CREATE TABLE TableList
            (TableListID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            DateModified TEXT); ''')
        connection.commit()
        print('Table created successfully')

    else:
        print('Table already exists')


def createConnectorsTable(connection):

    if not tableExists(connection, 'Connectors'):
        connection.execute(''' CREATE TABLE Connectors
            ( ConnectorID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL UNIQUE,
            CurrentAmount INT NOT NULL,
            Series TEXT,
            Type TEXT,
            PairName TEXT,
            BoxAmount INT,
            CartonAmount INT,
            DateOrdered TEXT,
            ProductInfo TEXT,
            OfficeAmount INT,
            StorageAmount INT,
            SampleCase TEXT);''') # sample case name goes in SampleCase COL

        today = time.strftime('%d-%m-%y')
        todayTouple = (today,)
        connection.execute("INSERT INTO TableList (Name, DateModified) VALUES ('Connectors', ? );", todayTouple)
        connection.commit()
        print('Table created successfully')

    else:
        print('Table already exists')


def createConnectorHistoryTable(connection):

    if not tableExists(connection, 'ConnectorsHistory'):
        connection.execute(''' CREATE TABLE History
            (HistoryID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Amount INT NOT NULL,
            Date TEXT NOT NULL,
            Difference INT,
            FOREIGN KEY(Name) REFERENCES Connectors(Name)); ''')

        today = time.strftime('%d-%m-%y')
        todayTouple = (today,)
        connection.execute("INSERT INTO TableList (Name, DateModified) VALUES ('ConnectorsHistory', ? );", todayTouple)
        connection.commit()
        print("Table created successfully")
    else:
        print('Table already exists')

def createSampleCasesTable(connection):

    if not tableExists(connection, 'SampleCases'):
        connection.execute('''CREATE TABLE SampleCase
            ( SampleCaseID INTEGER PRIMARY KEY,
            Amount INT,
            Date TEXT ); ''')

        today = time.strftime('%d-%m-%y')
        todayTouple = (today,)

        connection.execute("INSERT INTO TableList (Name, DateModified) VALUES ('SampleCase', ? );", todayTouple)
        connection.commit()
        print('Table created successfully')
    else:
        print('Table already exists')

def createSampleCasesHistoryTable(connection):

    if not tableExists(connection, 'SampleCasesHistory'):
        connection.execute(''' CREATE TABLE SampleCasesHistory
            (SampleCaseHistoryID INTEGER PRIMARY KEY,
            Name TEXT NOT NULL,
            Amount INT NOT NULL,
            Date TEXT NOT NULL,
            Difference INT,
            FOREIGN KEY(Name) REFERENCES SampleCases(Name)); ''')

        today = time.strftime('%d-%m-%y')
        todayTouple = (today,)
        connection.execute("INSERT INTO TableList (Name, DateModified) VALUES ('SampleCaseHistory', ? );", todayTouple)
        connection.commit()
        print("Table created successfully")
    else:
        print('Table already exists')

def fillTable(dict, connection, tableName): # put conenctors for default tablename

    keys = [key.title() for key in list(dict.keys())]

    keySTR = ", ".join(keys)
    keySTR = '(' + keySTR + ')'

    values = str(list(dict.values()))
    valuesSTR = values.replace("'", '"')
    valuesSTR = valuesSTR.replace('[', '(')
    valuesSTR = valuesSTR.replace(']', ')')

    # DIFFERENTITATES BETWEEN ' AND " IN EXECUTE STATEMENT

    if tableName.upper() == 'Connectors':

        entries  = ( 'ConnectorID', 'Name', 'Series', 'CurrentAmount', 'Type', 'PairName', 'BoxAmount',
        'CartonAmount', 'DateOrdered', 'ProductInfo', 'OfficeAmount', 'StorageAmount')

        if set(keys).issubset(set(entries)):
            connection.execute('INSERT INTO Connectors ' + keySTR + ' VALUES ' + valuesSTR)
            print('Records successfully added to connectors table.')

        else:
            print("Invalid keys for update in Connectors table")

    elif tableName.upper() == 'ConnectorsHistory':
        entries = ('Name', 'Amount', 'Date', 'Difference')

        if (set(entries) - set(keySTR) == set()) or (set(entries) - set(keySTR) == {'Difference'}):
            if 'Difference' not in keySTR:
                try:
                    connection.execute('SELECT Amount '
                                       'FROM ConnectorsHistory '
                                       'WHERE Name  = ' + str(dict['Name']) +
                                       ' AND WHERE HistoryID IN (SELECT HistoryID FROM ConnectorsHistory WHERE TOP(HistoryID)')
                    #VERIFY SUBQUERY SYNTAX
                except:
                    connection.execute('UPDATE ConnectorsHistory SET Difference = 0 WHERE Name = ' + dict['Name'])
                    # TEST

            connection.exectute('INSERT INTO ConnectorsHistory ' + keySTR + 'VALUES ' + valuesSTR)
            print('Records successfully added to ConnectorsHistory table.')

        else:
            print('Invalid keys for update in ConnectorsHistory table')

    elif tableName.upper() == 'SampleCasesHistory':
        entries = ('Name', 'Amount', 'Date', 'Difference')

        if (set(entries) - set(keySTR) == set()) or (set(entries) - set(keySTR) == {'Difference'}):
            if 'Difference' not in keySTR:
                try:
                    connection.execute('SELECT Amount '
                                       'FROM SampleCasesHistory '
                                       'WHERE Name  = ' + str(dict['Name']) +
                                       ' AND WHERE HistoryID IN '
                                       '(SELECT HistoryID FROM SampleCasesHistory WHERE TOP(HistoryID)')
                    # VERIFY SUBQUERY SYNTAX
                except:
                    connection.execute('UPDATE SampleCasesHistory SET Difference = 0 WHERE Name = ' + dict['Name'])
                    # TEST

            connection.exectute('INSERT INTO SampleCasesHistory ' + keySTR + 'VALUES ' + valuesSTR)
            print('Records successfully added to SampleCasesHistory table.')

        else:
            print('Invalid keys for update in SampleCasesHistory table')

    else:
        print('Not a valid table')

    connection.commit()

#for test use:

db = createDB('Z:\Inventory\InventoryGUI\inventory.db')
conndict = { 'ID' : 1 , 'NAME' : 'MUSBR', 'CURRENTAMOUNT' : 25}
hisdict = {'NAME' : 'MUSBR', 'AMOUNT' : 25}



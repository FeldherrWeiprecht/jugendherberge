import anvil.files
from anvil.files import data_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import sqlite3
# This is a server module. It runs on the Anvil server,
# rather than in the user's browser.
#
# To allow anvil.server.call() to call functions here, we mark
# them with @anvil.server.callable.
# Here is an example - you can replace it with your own:
#
# @anvil.server.callable
# def say_hello(name):
#   print("Hello, " + name + "!")
#   return 42
#

@anvil.server.callable
def create_database():
    connection = sqlite3.connect('jugendherberge.db')
    cursor = connection.cursor()

    # Tabellen erstellen
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Preiskategorie (
            PreiskategorieID INTEGER PRIMARY KEY,
            Preis REAL,
            Beschreibung TEXT)
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Gast (
            GastID INTEGER PRIMARY KEY,
            Vorname TEXT,
            Nachname TEXT,
            Email TEXT,
            PreiskategorieID INTEGER,
            FOREIGN KEY (PreiskategorieID) REFERENCES Preiskategorie(PreiskategorieID))
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Zimmer (
            ZimmerID INTEGER PRIMARY KEY,
            Zimmernummer INTEGER,
            Schlafplaetze INTEGER,
            PreiskategorieID INTEGER,
            JugendherbergeID INTEGER,
            FOREIGN KEY (PreiskategorieID) REFERENCES Preiskategorie(PreiskategorieID),
            FOREIGN KEY (JugendherbergeID) REFERENCES Jugendherberge(JugendherbergeID))
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Buchung (
            BuchungID INTEGER PRIMARY KEY,
            Buchungsdatum DATE,
            GastID INTEGER,
            ZimmerID INTEGER,
            FOREIGN KEY (GastID) REFERENCES Gast(GastID),
            FOREIGN KEY (ZimmerID) REFERENCES Zimmer(ZimmerID))
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS MitBuchung (
            MitBuchungID INTEGER PRIMARY KEY,
            BuchungID INTEGER,
            GastID INTEGER,
            FOREIGN KEY (BuchungID) REFERENCES Buchung(BuchungID), 
            FOREIGN KEY (GastID) REFERENCES Gast(GastID))
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Jugendherberge (
            JugendherbergeID INTEGER PRIMARY KEY,
            Name TEXT,
            Adresse TEXT)
    ''')

    connection.commit()
    connection.close()

@anvil.server.callable
def fill_database():
    connection = sqlite3.connect('jugendherberge.db')
    cursor = connection.cursor()

    # Vorhandene Daten löschen
    cursor.execute('DELETE FROM MitBuchung')
    cursor.execute('DELETE FROM Buchung')
    cursor.execute('DELETE FROM Gast')
    cursor.execute('DELETE FROM Zimmer')
    cursor.execute('DELETE FROM Jugendherberge')
    cursor.execute('DELETE FROM Preiskategorie')

    # Preiskategorien befüllen
    preiskategorien = [
        (1, 30.0, 'Einzelzimmer'),
        (2, 50.0, 'Doppelzimmer'),
        (3, 20.0, 'Schlafsaal'),
        (4, 40.0, 'Familienzimmer'),
        (5, 60.0, 'Luxuszimmer')
    ]
    cursor.executemany('INSERT INTO Preiskategorie (PreiskategorieID, Preis, Beschreibung) VALUES (?, ?, ?)', preiskategorien)

    # Jugendherbergen befüllen
    jugendherbergen = [
        (1, 'Jugendherberge A', 'Musterstraße 1, 12345 Musterstadt'),
        (2, 'Jugendherberge B', 'Beispielweg 2, 54321 Beispielstadt'),
        (3, 'Jugendherberge C', 'Teststraße 3, 67890 Teststadt'),
        (4, 'Jugendherberge D', 'Probeplatz 4, 98765 Probestadt'),
        (5, 'Jugendherberge E', 'Demoallee 5, 13579 Demostadt')
    ]
    cursor.executemany('INSERT INTO Jugendherberge (JugendherbergeID, Name, Adresse) VALUES (?, ?, ?)', jugendherbergen)

    # Zimmer befüllen
    zimmer = [
        (1, 101, 1, 1, 1),
        (2, 102, 2, 2, 1),
        (3, 201, 4, 3, 2),
        (4, 202, 2, 4, 3),
        (5, 301, 6, 5, 4)
    ]
    cursor.executemany('INSERT INTO Zimmer (ZimmerID, Zimmernummer, Schlafplaetze, PreiskategorieID, JugendherbergeID) VALUES (?, ?, ?, ?, ?)', zimmer)

    # Gäste befüllen
    gaeste = [
        (1, 'Max', 'Mustermann', 'max@mustermann.de', 1),
        (2, 'Erika', 'Musterfrau', 'erika@musterfrau.de', 2),
        (3, 'Hans', 'Müller', 'hans@mueller.de', 3),
        (4, 'Laura', 'Schmidt', 'laura@schmidt.de', 4),
        (5, 'Peter', 'Schneider', 'peter@schneider.de', 5)
    ]
    cursor.executemany('INSERT INTO Gast (GastID, Vorname, Nachname, Email, PreiskategorieID) VALUES (?, ?, ?, ?, ?)', gaeste)

    # Buchungen befüllen
    buchungen = [
        (1, '2024-01-01', 1, 1),
        (2, '2024-01-02', 2, 2),
        (3, '2024-01-03', 3, 3),
        (4, '2024-01-04', 4, 4),
        (5, '2024-01-05', 5, 5)
    ]
    cursor.executemany('INSERT INTO Buchung (BuchungID, Buchungsdatum, GastID, ZimmerID) VALUES (?, ?, ?, ?)', buchungen)

    # Mitbuchungen befüllen
    mitbuchungen = [
        (1, 1, 2),
        (2, 1, 3),
        (3, 2, 1),
        (4, 3, 4),
        (5, 4, 5)
    ]
    cursor.executemany('INSERT INTO MitBuchung (MitBuchungID, BuchungID, GastID) VALUES (?, ?, ?)', mitbuchungen)

    connection.commit()
    connection.close()


@anvil.server.callable
def get_zimmer_numbers():
    connection = sqlite3.connect('jugendherberge.db')
    cursor = connection.cursor()
    
    cursor.execute('SELECT ZimmerID, Zimmernummer FROM Zimmer')
    zimmer = cursor.fetchall()  # List of tuples (ZimmerID, Zimmernummer)
    
    connection.close()
    
    return zimmer

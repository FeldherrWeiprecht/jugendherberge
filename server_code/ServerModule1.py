import anvil.files
from anvil.files import data_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server
import sqlite3
from datetime import datetime

@anvil.server.callable
def create_database():
    connection = sqlite3.connect('jugendherberge.db')
    cursor = connection.cursor()

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

    cursor.execute('DELETE FROM MitBuchung')
    cursor.execute('DELETE FROM Buchung')
    cursor.execute('DELETE FROM Gast')
    cursor.execute('DELETE FROM Zimmer')
    cursor.execute('DELETE FROM Jugendherberge')
    cursor.execute('DELETE FROM Preiskategorie')

    preiskategorien = [
        (1, 30.0, 'Einzelzimmer'),
        (2, 50.0, 'Doppelzimmer'),
        (3, 20.0, 'Schlafsaal'),
        (4, 40.0, 'Familienzimmer'),
        (5, 60.0, 'Luxuszimmer')
    ]
    cursor.executemany('INSERT INTO Preiskategorie (PreiskategorieID, Preis, Beschreibung) VALUES (?, ?, ?)', preiskategorien)

    jugendherbergen = [
        (1, 'Jugendherberge A', 'Musterstraße 1, 12345 Musterstadt'),
        (2, 'Jugendherberge B', 'Beispielweg 2, 54321 Beispielstadt'),
        (3, 'Jugendherberge C', 'Teststraße 3, 67890 Teststadt'),
        (4, 'Jugendherberge D', 'Probeplatz 4, 98765 Probestadt'),
        (5, 'Jugendherberge E', 'Demoallee 5, 13579 Demostadt')
    ]
    cursor.executemany('INSERT INTO Jugendherberge (JugendherbergeID, Name, Adresse) VALUES (?, ?, ?)', jugendherbergen)

    zimmer = [
        (1, 101, 1, 1, 1),
        (2, 102, 2, 2, 1),
        (3, 201, 4, 3, 2),
        (4, 202, 2, 4, 3),
        (5, 301, 6, 5, 4)
    ]
    cursor.executemany('INSERT INTO Zimmer (ZimmerID, Zimmernummer, Schlafplaetze, PreiskategorieID, JugendherbergeID) VALUES (?, ?, ?, ?, ?)', zimmer)

    gaeste = [
        (1, 'Max', 'Mustermann', 'max@mustermann.de', 1),
        (2, 'Erika', 'Musterfrau', 'erika@musterfrau.de', 2),
        (3, 'Hans', 'Müller', 'hans@mueller.de', 3),
        (4, 'Laura', 'Schmidt', 'laura@schmidt.de', 4),
        (5, 'Peter', 'Schneider', 'peter@schneider.de', 5)
    ]
    cursor.executemany('INSERT INTO Gast (GastID, Vorname, Nachname, Email, PreiskategorieID) VALUES (?, ?, ?, ?, ?)', gaeste)

    buchungen = [
        (1, '2024-01-01', 1, 1),
        (2, '2024-01-02', 2, 2),
        (3, '2024-01-03', 3, 3),
        (4, '2024-01-04', 4, 4),
        (5, '2024-01-05', 5, 5)
    ]
    cursor.executemany('INSERT INTO Buchung (BuchungID, Buchungsdatum, GastID, ZimmerID) VALUES (?, ?, ?, ?)', buchungen)

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
def get_jugendherbergen():
    connection = sqlite3.connect('jugendherberge.db')
    cursor = connection.cursor()

    cursor.execute('SELECT Name FROM Jugendherberge')
    result = cursor.fetchall()

    connection.close()
    return [row[0] for row in result]


@anvil.server.callable
def get_zimmer_by_jugendherberge(jugendherberge_id):
    connection = sqlite3.connect('jugendherberge.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT Zimmernummer, Preis FROM Zimmer 
        JOIN Preiskategorie ON Zimmer.PreiskategorieID = Preiskategorie.PreiskategorieID
        WHERE JugendherbergeID = ?
    ''', (jugendherberge_id,))
    zimmer = cursor.fetchall()
    connection.close()
    return [(f'Zimmer {zimmernummer} - {preis} €', zimmernummer) for zimmernummer, preis in zimmer]
  
@anvil.server.callable
def get_jugendherberge_id_by_name(jugendherberge_name):
    connection = sqlite3.connect('jugendherberge.db')
    cursor = connection.cursor()
    cursor.execute('SELECT JugendherbergeID FROM Jugendherberge WHERE Name = ?', (jugendherberge_name,))
    jugendherberge_id = cursor.fetchone()[0]
    connection.close()
    return jugendherberge_id

@anvil.server.callable
def get_preiskategorien():
    connection = sqlite3.connect('jugendherberge.db')
    cursor = connection.cursor()
    cursor.execute('SELECT Beschreibung, PreiskategorieID FROM Preiskategorie')
    preiskategorien = cursor.fetchall()
    connection.close()
    return [(beschreibung, preiskategorie_id) for beschreibung, preiskategorie_id in preiskategorien]

@anvil.server.callable
def get_zimmer_by_jugendherberge_and_preiskategorie(jugendherberge_id, preiskategorie_id):
    connection = sqlite3.connect('jugendherberge.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT Zimmernummer, Preis FROM Zimmer 
        JOIN Preiskategorie ON Zimmer.PreiskategorieID = Preiskategorie.PreiskategorieID
        WHERE JugendherbergeID = ? AND Zimmer.PreiskategorieID = ?
    ''', (jugendherberge_id, preiskategorie_id))
    zimmer = cursor.fetchall()
    connection.close()
    return [(f'Zimmer {zimmernummer} - {preis} €', zimmernummer) for zimmernummer, preis in zimmer]

@anvil.server.callable
def get_all_guests():
    connection = sqlite3.connect('jugendherberge.db')
    cursor = connection.cursor()
    cursor.execute('SELECT Vorname, Nachname FROM Gast')
    guests = cursor.fetchall()
    connection.close()
    return guests

@anvil.server.callable
def get_all_guests_with_prices():
    connection = sqlite3.connect('jugendherberge.db')
    cursor = connection.cursor()
    cursor.execute('''
        SELECT Gast.GastID, Gast.Vorname, Gast.Nachname, Preiskategorie.Preis 
        FROM Gast
        JOIN Preiskategorie ON Gast.PreiskategorieID = Preiskategorie.PreiskategorieID
    ''')
    guests = cursor.fetchall()
    connection.close()
    return guests

@anvil.server.callable
def print_database_tables():
    connection = sqlite3.connect('jugendherberge.db')
    cursor = connection.cursor()

    # Abrufen der Daten aus allen relevanten Tabellen
    tables = ['Preiskategorie', 'Gast', 'Zimmer', 'Buchung', 'MitBuchung', 'Jugendherberge']
    table_data = {}

    for table in tables:
        cursor.execute(f'SELECT * FROM {table}')
        rows = cursor.fetchall()
        table_data[table] = rows

    connection.close()
    return table_data

@anvil.server.callable
def create_buchung(guest_ids, room_id):
    connection = sqlite3.connect('jugendherberge.db')
    cursor = connection.cursor()

    # Aktuellen Zeitpunkt für die Buchung
    buchungsdatum = "2024-11-09"  # Zum Beispiel das heutige Datum, kann mit datetime modifiziert werden

    # Buchung für den ersten Gast (Max Mustermann, GastID = 1)
    cursor.execute('''
        INSERT INTO Buchung (Buchungsdatum, GastID, ZimmerID)
        VALUES (?, ?, ?)
    ''', (buchungsdatum, 1, room_id))

    buchung_id = cursor.lastrowid  # Die ID der gerade eingefügten Buchung

    # MitBuchung für alle anderen Gäste
    for guest_id in guest_ids:
        cursor.execute('''
            INSERT INTO MitBuchung (BuchungID, GastID)
            VALUES (?, ?)
        ''', (buchung_id, guest_id))

    connection.commit()
    connection.close()

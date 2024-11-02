import anvil.files
from anvil.files import data_files
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

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
import anvil.server
import sqlite3

@anvil.server.callable
def get_guests():
    print("Connecting to database...")
    try:
        connection = sqlite3.connect('jugendherberge.db')
        print("Database connected.")
        cursor = connection.cursor()
        cursor.execute("SELECT Vorname, Nachname FROM Gast")
        guests = cursor.fetchall()
        connection.close()
        
        print(f"Guests fetched: {guests}")
        return [f"{vorname} {nachname}" for vorname, nachname in guests]
    except Exception as e:
        print(f"Error: {e}")
        return []

def test_db_connection():
    try:
        connection = sqlite3.connect('jugendherberge.db')
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        connection.close()
        
        return tables  # Gibt die Tabellen in der Datenbank zurück
    except Exception as e:
        print(f"Error: {e}")
        return []

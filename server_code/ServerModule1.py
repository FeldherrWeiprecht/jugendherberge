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
def get_zimmer():
    connection = sqlite3.connect('jugendherberge.db')
    cursor = connection.cursor()

    cursor.execute('SELECT ZimmerID, Zimmernummer FROM Zimmer')
    zimmer_liste = cursor.fetchall()

    connection.close()

    return zimmer_liste

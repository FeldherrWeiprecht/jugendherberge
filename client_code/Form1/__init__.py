from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Form1(Form1Template):

    def __init__(self, **properties):
        self.init_components(**properties)

        # Zimmerdaten laden und Dropdown befüllen
        self.load_zimmer()

    def load_zimmer(self):
        try:
            # Abrufen der Zimmerdaten
            zimmer_daten = anvil.server.call('get_zimmer')
            
            # Dropdown mit den Zimmern füllen
            if zimmer_daten:
                self.drop_down_1.items = [(zimmer[0], f"Zimmer {zimmer[1]}") for zimmer in zimmer_daten]
        except Exception as e:
            print(f"Fehler: {str(e)}")  # Fehler in der Konsole ausgeben

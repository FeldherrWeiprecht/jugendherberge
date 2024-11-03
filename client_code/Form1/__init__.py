from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


from ._anvil_designer import Form1Template
from anvil import *

class Form1(Form1Template):
    def __init__(self, **properties):
        self.init_components(**properties)
        
        # Aufruf der Servermethoden
        anvil.server.call('create_database')
        anvil.server.call('fill_database')  # Datenbank erstellen und befüllen
        self.load_zimmer_data()              # Dropdown mit Zimmerdaten befüllen

    def load_zimmer_data(self):
        zimmer_data = anvil.server.call('get_zimmer_numbers')
        # Korrektes Format für Dropdown
        self.drop_down_1.items = [(str(zimmernummer), zimmer_id) for zimmer_id, zimmernummer in zimmer_data]

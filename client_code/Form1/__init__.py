from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables


class Form1(Form1Template):

    def __init__(self, **properties):
        self.init_components(**properties)
        self.load_guests()

    def load_guests(self):
      guests = anvil.server.call('get_guests')
      self.drop_down_1.items = guests  # Hier den richtigen Namen verwenden

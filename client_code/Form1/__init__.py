from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

# in das datagrid neben namen preiskategorie des gastes

class Form1(Form1Template):
    def __init__(self, **properties):
        self.init_components(**properties)
        anvil.server.call('create_database')
        anvil.server.call('fill_database')  
        self.populate_jugendherbergen_dropdown()
        self.populate_preiskategorien_dropdown()
        self.populate_gaeste_dropdown()
        self.gaeste = []

        # Event-Handler für Dropdown-Auswahl
        self.drop_down_jugendherbergen.set_event_handler('change', self.on_jugendherberge_change)
        self.drop_down_preiskategorie.set_event_handler('change', self.on_preiskategorie_change)

        # Zeige die Zimmer basierend auf der Standard-Jugendherberge und der Preiskategorie an
        if self.drop_down_jugendherbergen.selected_value:
            self.update_zimmer_dropdown(self.drop_down_jugendherbergen.selected_value, None)  # Zeige alle Zimmer

    def populate_jugendherbergen_dropdown(self):
        jugendherbergen = anvil.server.call('get_jugendherbergen')
        self.drop_down_jugendherbergen.items = jugendherbergen
        
        if jugendherbergen:
            self.drop_down_jugendherbergen.selected_value = jugendherbergen[0]
            self.update_zimmer_dropdown(jugendherbergen[0], None)  # Zeige alle Zimmer

    def populate_preiskategorien_dropdown(self):
        preiskategorien = anvil.server.call('get_preiskategorien')
        self.drop_down_preiskategorie.items = [('Alle', None)] + preiskategorien  # Füge 'Alle' hinzu
        
        # Setze den Standardwert auf 'Alle'
        self.drop_down_preiskategorie.selected_value = None  

    def on_jugendherberge_change(self, **event_args):
        selected_herberge = self.drop_down_jugendherbergen.selected_value
        if selected_herberge:
            self.update_zimmer_dropdown(selected_herberge, self.drop_down_preiskategorie.selected_value)

    def populate_gaeste_dropdown(self):
        guests = anvil.server.call('get_all_guests')
        self.drop_down_gaeste.items = [f"{vorname} {nachname}" for vorname, nachname in guests]

        if guests:
            self.drop_down_gaeste.selected_value = self.drop_down_gaeste.items[0]  # Setze den Standardwert

    def button_add_click(self, **event_args):
      selected_guest = self.drop_down_gaeste.selected_value
      
      new_entry = {'Name': selected_guest}
      if new_entry not in self.gaeste:
        self.gaeste.append(new_entry)
        self.repeating_panel_gaeste.items = self.gaeste

    def button_remove_click(self, **event_args):
      selected_guest = self.drop_down_gaeste.selected_value

      # Entferne den Gast, wenn er in der Liste ist
      self.gaeste = [guest for guest in self.gaeste if guest['Name'] != selected_guest]

      # Aktualisiere das Repeating Panel
      self.repeating_panel_gaeste.items = self.gaeste
      
          
    def on_preiskategorie_change(self, **event_args):
        selected_preiskategorie = self.drop_down_preiskategorie.selected_value
        selected_herberge = self.drop_down_jugendherbergen.selected_value
        if selected_herberge:
            self.update_zimmer_dropdown(selected_herberge, selected_preiskategorie)

    def update_zimmer_dropdown(self, jugendherberge_name, preiskategorie_id=None):
        # Holen Sie sich die ID der ausgewählten Jugendherberge
        jugendherberge_id = anvil.server.call('get_jugendherberge_id_by_name', jugendherberge_name)

        # Holen Sie sich die Zimmer für die ausgewählte Jugendherberge und Preiskategorie
        if preiskategorie_id is not None:  # Wenn 'Alle' ausgewählt ist, filtere nicht
            zimmer = anvil.server.call('get_zimmer_by_jugendherberge_and_preiskategorie', jugendherberge_id, preiskategorie_id)
        else:
            zimmer = anvil.server.call('get_zimmer_by_jugendherberge', jugendherberge_id)

        if zimmer:
            self.drop_down_zimmer.items = zimmer
            self.drop_down_zimmer.selected_value = zimmer[0][1]  # Setze den Standardwert auf das erste Zimmer
        else:
            self.drop_down_zimmer.items = [('Kein Zimmer', None)]  # Setze auf 'Kein Zimmer', wenn keine Zimmer verfügbar sind
            self.drop_down_zimmer.selected_value = None  # Keine Auswahl

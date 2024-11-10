from ._anvil_designer import Form1Template
from anvil import *
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Form1(Form1Template):
    def __init__(self, **properties):
        self.init_components(**properties)
        anvil.server.call('create_database')
        anvil.server.call('fill_database')  
        self.populate_jugendherbergen_dropdown()
        self.populate_preiskategorien_dropdown()
        self.populate_gaeste_dropdown()
        self.gaeste = []

        self.drop_down_jugendherbergen.set_event_handler('change', self.on_jugendherberge_change)
        self.drop_down_preiskategorie.set_event_handler('change', self.on_preiskategorie_change)

        if self.drop_down_jugendherbergen.selected_value:
            self.update_zimmer_dropdown(self.drop_down_jugendherbergen.selected_value, None) 

    def populate_jugendherbergen_dropdown(self):
      jugendherbergen = anvil.server.call('get_jugendherbergen')
      self.drop_down_jugendherbergen.items = jugendherbergen
      
      if jugendherbergen:
          self.drop_down_jugendherbergen.selected_value = jugendherbergen[0][1]  
          self.update_zimmer_dropdown(jugendherbergen[0][1], None) 

    def populate_preiskategorien_dropdown(self):
      preiskategorien = anvil.server.call('get_preiskategorien')
      self.drop_down_preiskategorie.items = [('Alle', None)] + [
          (f"{beschreibung} ({preis} €)", preiskategorie_id) for beschreibung, preiskategorie_id, preis in preiskategorien
      ]
      self.drop_down_preiskategorie.selected_value = None  

    def on_jugendherberge_change(self, **event_args):
        selected_herberge = self.drop_down_jugendherbergen.selected_value
        if selected_herberge:
            self.update_zimmer_dropdown(selected_herberge, self.drop_down_preiskategorie.selected_value)

    def populate_gaeste_dropdown(self):
      guests = anvil.server.call('get_all_guests_with_prices')
      guests = [guest for guest in guests if guest[0] != 1]
      self.drop_down_gaeste.items = [
          (f"{vorname} {nachname} - {preis} €", gast_id) for gast_id, vorname, nachname, preis in guests
      ]

      if guests:
          self.drop_down_gaeste.selected_value = self.drop_down_gaeste.items[0][1]  

    def button_add_click(self, **event_args):
      selected_guest_id = self.drop_down_gaeste.selected_value
      if not selected_guest_id:
          alert("Bitte wählen Sie einen Gast aus!")
          return
    
      selected_guest = next(
          (item for item in self.drop_down_gaeste.items if item[1] == selected_guest_id), None
      )
  
      if selected_guest:
          guest_name_with_price = selected_guest[0]
          name_part, price_part = guest_name_with_price.rsplit(" - ", 1)
          new_entry = {'GastID': selected_guest_id, 'Name': name_part, 'Preis': price_part}

          if new_entry not in self.gaeste:
              self.gaeste.append(new_entry)
              self.repeating_panel_gaeste.items = self.gaeste

    def button_remove_click(self, **event_args):
        selected_guest_id = self.drop_down_gaeste.selected_value
        selected_guest = next(
            (item for item in self.drop_down_gaeste.items if item[1] == selected_guest_id), None
        )
    
        if selected_guest:
            guest_name_with_price = selected_guest[0] 
            name_part, price_part = guest_name_with_price.rsplit(" - ", 1)
    
            self.gaeste = [
                guest for guest in self.gaeste
                if not (guest['Name'] == name_part and guest['Preis'] == price_part)
            ]
            self.repeating_panel_gaeste.items = self.gaeste
      
    def on_preiskategorie_change(self, **event_args):
        selected_preiskategorie = self.drop_down_preiskategorie.selected_value
        selected_herberge = self.drop_down_jugendherbergen.selected_value
        if selected_herberge:
            self.update_zimmer_dropdown(selected_herberge, selected_preiskategorie)

    def update_zimmer_dropdown(self, jugendherberge_name, preiskategorie_id=None):
        jugendherberge_id = anvil.server.call('get_jugendherberge_id_by_name', jugendherberge_name)

        if preiskategorie_id is not None:  
            zimmer = anvil.server.call('get_zimmer_by_jugendherberge_and_preiskategorie', jugendherberge_id, preiskategorie_id)
        else:
            zimmer = anvil.server.call('get_zimmer_by_jugendherberge', jugendherberge_id)

        if zimmer:
            self.drop_down_zimmer.items = zimmer
            self.drop_down_zimmer.selected_value = zimmer[0][1]
        else:
            self.drop_down_zimmer.items = [('Kein Zimmer', None)]  
            self.drop_down_zimmer.selected_value = None  
          
    def book_click(self, **event_args):
        selected_room = self.drop_down_zimmer.selected_value
        if selected_room is None:
            alert("Bitte wählen Sie ein Zimmer aus!")
            return
      
        selected_guest_ids = [guest['GastID'] for guest in self.gaeste]
        anvil.server.call('create_buchung', selected_guest_ids, selected_room)
        
        data = anvil.server.call('print_database_tables')
        alert("Buchung erfolgreich abgeschlossen!", title="Erfolg", large=True, buttons=[("OK", True)])
        ### !Ausgabe zum schauen ob alles funktioniert hat in der Console ###
        for table, rows in data.items():
            print(f"Table: {table}")
            for row in rows:
                print(row)
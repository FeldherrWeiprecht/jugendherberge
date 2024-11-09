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

    def populate_gaeste_dropdown(self):
      # Rufe alle Gäste mit Preisen ab
      guests = anvil.server.call('get_all_guests_with_prices')
  
      # Filtere den ersten Gast (GastID = 1) heraus
      guests = [guest for guest in guests if guest[0] != 1]  # guest[0] ist die GastID
  
      # Aktualisiere das Dropdown mit den verbleibenden Gästen
      self.drop_down_gaeste.items = [
          (f"{vorname} {nachname} - {preis} €", gast_id) for gast_id, vorname, nachname, preis in guests
      ]
      
      # Setze den ersten Gast als Standardauswahl, wenn es Gäste gibt
      if guests:
          self.drop_down_gaeste.selected_value = self.drop_down_gaeste.items[0][1]  # Setze den Standardwert auf den ersten Gast

    def button_add_click(self, **event_args):
      selected_guest_id = self.drop_down_gaeste.selected_value
      selected_guest = next(
          (item for item in self.drop_down_gaeste.items if item[1] == selected_guest_id), None
      )
      
      if selected_guest:
          guest_name_with_price = selected_guest[0]  # Enthält "Vorname Nachname - Preis €"
          
          # Extrahiere den Namen und den Preis
          name_part, price_part = guest_name_with_price.rsplit(" - ", 1)
          
          # Speichere den Gast mit der ID
          new_entry = {'GastID': selected_guest_id, 'Name': name_part, 'Preis': price_part}
          
          # Stelle sicher, dass der Gast noch nicht hinzugefügt wurde
          if new_entry not in self.gaeste:
              self.gaeste.append(new_entry)
              self.repeating_panel_gaeste.items = self.gaeste

    def button_remove_click(self, **event_args):
        selected_guest_id = self.drop_down_gaeste.selected_value
        selected_guest = next(
            (item for item in self.drop_down_gaeste.items if item[1] == selected_guest_id), None
        )
    
        if selected_guest:
            guest_name_with_price = selected_guest[0]  # Format: "Vorname Nachname - Preis €"
            
            # Split the name and price parts
            name_part, price_part = guest_name_with_price.rsplit(" - ", 1)
    
            # Remove the guest from self.gaeste by matching both name and price
            self.gaeste = [
                guest for guest in self.gaeste
                if not (guest['Name'] == name_part and guest['Preis'] == price_part)
            ]
    
            # Update the Repeating Panel
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

    def book_click(self, **event_args):
      # Hole die ausgewählten Werte
      selected_herberge = self.drop_down_jugendherbergen.selected_value
      selected_preiskategorie = self.drop_down_preiskategorie.selected_value
      selected_zimmer = self.drop_down_zimmer.selected_value
      selected_gaeste = self.gaeste  # Alle Gäste, die mitgebucht werden

      # Validierungen
      if not selected_zimmer:
          alert("Kein Zimmer verfügbar. Bitte wählen Sie ein anderes Zimmer.")
          return
      
      if not selected_herberge:
          alert("Bitte wählen Sie eine Jugendherberge aus.")
          return
      
      if selected_preiskategorie is None:
          alert("Bitte wählen Sie eine Preiskategorie aus.")
          return

      # Buchung des ersten Gastes als Hauptgast
      hauptgast_id = self.drop_down_gaeste.selected_value
      hauptgast = next(guest for guest in self.drop_down_gaeste.items if guest[1] == hauptgast_id)

      # Speichern der Buchung
      buchung_id = anvil.server.call('create_buchung', hauptgast_id, selected_zimmer)

      # Mitbuchungen speichern
      for gast in selected_gaeste:
          mitbuchung_id = anvil.server.call('create_mitbuchung', buchung_id, gast['GastID'])

      # Ausgabe der gesamten Tabelle
      self.print_all_data()

    def print_all_data(self):
      # Alle Buchungen und Gäste ausgeben
      buchungen = anvil.server.call('get_all_buchungen')
      for buchung in buchungen:
          print(f"BuchungID: {buchung[0]}, GastID: {buchung[2]}, ZimmerID: {buchung[3]}")
      
      gaeste = anvil.server.call('get_all_guests')
      for gast in gaeste:
          print(f"GastID: {gast[0]}, Name: {gast[1]} {gast[2]}")




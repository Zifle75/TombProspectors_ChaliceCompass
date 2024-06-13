import os
import sqlite3
import sys
import threading
import tkinter as tk
from tkinter import ttk

# Color array for distinguishing Layers in notes
LAYER_COLORS = {
    'L1': '#add8e6',  # Light blue
    'L1:': '#add8e6',
    'L2': '#90ee90',  # Light green
    'L2:': '#90ee90',
    'L3': '#ffcccb',  # Light red
    'L3:': '#ffcccb',
    'L4': '#ffa500',  # Orange
    'L4:': '#ffa500',
    'L5': '#d3d3d3',  # Light grey
    'L5:': '#d3d3d3'
}


class DungeonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chalice Compass")

        # Set Icon to free use compass online
        self.root.iconbitmap(self.resource_path('compass.ico'))

        # Enable threading
        self.db_lock = threading.Lock()

        # Set up the database connection
        self.db_paths = [self.resource_path('ChaliceCompass.db'), self.resource_path('ChaliceCompass_backup.db')]
        self.conn = None
        self.cursor = None
        self.connect_to_db()

        # Load all equipment types for the equipment type dropdown
        self.equipment_types = self.load_equipment_types()

        # Initialize items for search dropdown
        self.items = []

        # GUI Setup
        self.setup_widgets()

        # Store last search term used
        self.last_search_term = ""

        # Load all dungeons by default
        self.load_all_dungeons()

    def resource_path(self, relative_path):
        """ Get the absolute path to a resource, works for dev and for PyInstaller """
        try:
            # PyInstaller creates a temp folder and stores path in _MEIPASS
            base_path = sys._MEIPASS
        except Exception:
            base_path = os.path.abspath(".")

        return os.path.join(base_path, relative_path)

    def connect_to_db(self):
        """ First connect to primary db, if that doesn't work, use local backup """
        # TODO: Implement live server as primarydb rather than a local copy
        for db_path in self.db_paths:
            try:
                self.conn = sqlite3.connect(db_path, check_same_thread=False)
                self.cursor = self.conn.cursor()
                return
            except sqlite3.Error as e:
                print(f"Failed to connect to {db_path}: {e}")
        if not self.conn:
            raise Exception("Failed to connect to any database.")

    def execute_query(self, query, params=()):
        """ Executes query on db in use"""
        with self.db_lock:
            try:
                self.cursor.execute(query, params)
                self.conn.commit()
                return self.cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Database error: {e}")
                self.connect_to_db()

    def treeview_sort_column(self, col, reverse):
        """ Adds sorting functionality to tables"""
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        l.sort(reverse=reverse, key=lambda t: t[0].lower())

        # Rearrange items in sorted order
        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)

        # Toggle the sorting direction for the next sort operation
        reverse = not reverse
        # Update the header command to sort in the new order
        self.tree.heading(col, command=lambda: self.treeview_sort_column(col, reverse))

    def perform_search(self, event=None):
        """ Performs a String search via SQL LIKE method"""
        search_term = self.item_var.get()
        self.last_search_term = search_term
        query = "SELECT Glyph, Category, Status, Bosses, Notes FROM Dungeon WHERE Notes LIKE ?"
        results = self.execute_query(query, (f'%{search_term}%',))

        self.tree.delete(*self.tree.get_children())
        for row in results:
            formatted_notes = self.format_notes(row[4])
            self.tree.insert('', tk.END, values=(row[0], row[1], row[2], row[3], formatted_notes))

    def perform_item_search(self):
        """ Performs an equipment search from Equipment dropdown, uses relationship table"""
        selected_item = self.item_var.get()
        self.last_search_term = selected_item
        query = """
        SELECT Dungeon.Glyph, Dungeon.Category, Dungeon.Status, Dungeon.Bosses, Dungeon.Notes
        FROM Dungeon
        JOIN Dungeon_Equipment ON Dungeon.Glyph = Dungeon_Equipment.Glyph
        WHERE Dungeon_Equipment.EquipmentName = ?
        """
        results = self.execute_query(query, (selected_item,))

        self.tree.delete(*self.tree.get_children())
        for row in results:
            formatted_notes = self.format_notes(row[4])
            self.tree.insert('', tk.END, values=(row[0], row[1], row[2], row[3], formatted_notes))

    def reset_app(self):
        """ Simple resets most the initial states of the application, does not reset db"""
        self.item_var.set('')
        self.equipment_type_var.set('')
        self.last_search_term = ''
        self.detail_frame.delete('1.0', tk.END)
        self.tree.delete(*self.tree.get_children())  # Clear the treeview
        self.load_all_dungeons()  # Reload all dungeons
        self.tree.tag_configure('highlight', background='white')  # Reset highlights

    def setup_widgets(self):
        """ Sets up basic front end to interact with database"""
        # Dropdown for equipment type search
        self.equipment_type_var = tk.StringVar()
        self.equipment_type_combobox = ttk.Combobox(self.root, textvariable=self.equipment_type_var,
                                                    values=self.equipment_types, width=60)
        self.equipment_type_combobox.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.equipment_type_combobox.bind('<<ComboboxSelected>>', self.update_item_dropdown)

        # Dropdown for item search
        self.item_var = tk.StringVar()
        self.item_combobox = ttk.Combobox(self.root, textvariable=self.item_var, values=self.items, width=60)
        self.item_combobox.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        # Bind Enter key to perform search
        self.item_combobox.bind('<Return>', self.perform_item_search)

        # Search button
        self.search_button = ttk.Button(self.root, text='Search by String', command=self.perform_search)
        self.search_button.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        # Item search button
        self.item_search_button = ttk.Button(self.root, text='Search by Equipment', command=self.perform_item_search)
        self.item_search_button.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

        # Reset button
        self.reset_button = ttk.Button(self.root, text='Reset', command=self.reset_app)
        self.reset_button.grid(row=0, column=4, padx=10, pady=10, sticky="ew")

        # Update status button
        self.update_status_button = ttk.Button(self.root, text='Toggle Status', command=self.update_dungeon_status)
        self.update_status_button.grid(row=0, column=5, padx=10, pady=10, sticky="ew")

        # Treeview for displaying dungeons
        self.tree = ttk.Treeview(self.root, columns=('Glyph', 'Category', 'Status', 'Bosses', 'Notes'), show='headings',
                                 height=15)
        self.tree.heading('Glyph', text='Glyph', command=lambda: self.treeview_sort_column('Glyph', False))
        self.tree.heading('Category', text='Category', command=lambda: self.treeview_sort_column('Category', False))
        self.tree.heading('Status', text='Status', command=lambda: self.treeview_sort_column('Status', False))
        self.tree.heading('Bosses', text='Bosses', command=lambda: self.treeview_sort_column('Bosses', False))
        self.tree.heading('Notes', text='Notes', command=lambda: self.treeview_sort_column('Notes', False))
        self.tree.column('Glyph', width=100)
        self.tree.column('Category', width=100)
        self.tree.column('Status', width=100)
        self.tree.column('Bosses', width=150)
        self.tree.column('Notes', width=500)
        self.tree.grid(row=1, column=0, columnspan=6, sticky='nsew', padx=10, pady=10)

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        # Detail frame for displaying full note on row click
        self.detail_frame = tk.Text(self.root, height=10, wrap='word')
        self.detail_frame.grid(row=2, column=0, columnspan=6, sticky='nsew', padx=10, pady=10)

        # Configure grid column configuration
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)
        self.root.grid_columnconfigure(2, weight=0)
        self.root.grid_columnconfigure(3, weight=0)
        self.root.grid_columnconfigure(4, weight=0)
        self.root.grid_columnconfigure(5, weight=0)

        # Configure grid column configuration
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)
        self.root.grid_columnconfigure(2, weight=0)
        self.root.grid_columnconfigure(3, weight=0)
        self.root.grid_columnconfigure(4, weight=0)

    def load_equipment_types(self):
        """ Finds different categories of equipment from database"""
        query = "SELECT DISTINCT Category FROM Equipment"
        records = self.execute_query(query)
        return [category[0] for category in records]

    def update_item_dropdown(self, event=None):
        """ Populates Equipment dropdown from db based on equipment type selected"""
        selected_type = self.equipment_type_var.get()
        query = "SELECT EquipmentName FROM Equipment WHERE Category = ?"
        records = self.execute_query(query, (selected_type,))
        self.items = [item[0] for item in records]
        self.item_combobox['values'] = self.items

    def load_all_dungeons(self):
        """ Loads all dungeons from db """
        query = "SELECT Glyph, Category, Status, Bosses, Notes FROM Dungeon"
        results = self.execute_query(query)
        self.tree.delete(*self.tree.get_children())
        for row in results:
            formatted_notes = self.format_notes(row[4])
            self.tree.insert('', tk.END, values=(row[0], row[1], row[2], row[3], formatted_notes))

    def format_notes(self, notes):
        """ Adds newlines to key strings for accessibility"""
        for layer in LAYER_COLORS.keys():
            notes = notes.replace(layer, '\n' + layer)
        return notes

    def highlight_text(self, terms_tags):
        """ Simple method used to either highlight search string matches or layers"""
        if not terms_tags:
            return

        for term, tag in terms_tags.items():
            if not term:
                continue
            start = '1.0'
            while True:
                pos = self.detail_frame.search(term, start, stopindex=tk.END, nocase=True)
                if not pos:
                    break
                end = f"{pos}+{len(term)}c"
                self.detail_frame.tag_add(tag, pos, end)
                start = end

    def on_tree_select(self, event):
        """ When an entry is selects, allows us to format the notes and make things more obvious to user"""
        selected_item = self.tree.selection()[0] if self.tree.selection() else None
        if selected_item:
            item_data = self.tree.item(selected_item)['values']
            notes = self.format_notes(item_data[-1])

            self.detail_frame.delete('1.0', tk.END)
            self.detail_frame.insert(tk.END, notes)  # Insert formatted notes

            # Highlight search terms
            self.highlight_text({self.last_search_term: 'search_highlight'})

            # Highlight layer terms
            self.highlight_text({layer: layer for layer in LAYER_COLORS.keys()})

            # Configure tag styles
            self.detail_frame.tag_configure('search_highlight', background='yellow')
            for layer, color in LAYER_COLORS.items():
                self.detail_frame.tag_configure(layer, background=color)
        else:
            self.detail_frame.delete('1.0', tk.END)
            self.detail_frame.insert(tk.END, "No item selected or available.")

    def update_dungeon_status(self):
        """ Allows user to mark dungeons as expired for their local copy"""
        # TODO: Assuming we get a server, this method would have to completely change
        #  bc the current implementation isn't wise for more than one person
        selected_item = self.tree.selection()[0] if self.tree.selection() else None
        if selected_item:
            item_data = self.tree.item(selected_item)['values']
            current_status = item_data[2]
            new_status = 'FLAGGED' if current_status == 'Active' else 'Active'
            query = "UPDATE Dungeon SET Status = ? WHERE Glyph = ?"
            self.execute_query(query, (new_status, item_data[0]))
            self.load_all_dungeons()
            self.detail_frame.insert(tk.END, f"\nStatus updated to {new_status}")

    def on_closing(self):
        """ Closes the application like it should"""
        self.conn.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = DungeonApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()

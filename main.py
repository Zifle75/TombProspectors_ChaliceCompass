import sqlite3
import tkinter as tk
from tkinter import ttk

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

        # Set up the database connection
        self.conn = sqlite3.connect('ChaliceCompass.db')
        self.cursor = self.conn.cursor()

        # Load all equipment types for the type dropdown
        self.equipment_types = self.load_equipment_types()

        # Load all items for the search dropdown
        self.items = []

        # GUI Setup
        self.setup_widgets()

        # Store last search term used
        self.last_search_term = ""

        # Load all dungeons by default
        self.load_all_dungeons()

    def treeview_sort_column(self, col, reverse):
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
        search_term = self.item_var.get()
        self.last_search_term = search_term
        matching_entries = []
        non_matching_entries = []
        query = "SELECT Glyph, Category, Status, Bosses, Notes FROM Dungeon WHERE Notes LIKE ?"
        search_term = f'%{search_term}%'
        self.cursor.execute(query, (search_term,))
        results = self.cursor.fetchall()

        # Re-populate the treeview with search results
        self.tree.delete(*self.tree.get_children())
        for row in results:
            formatted_notes = self.format_notes(row[4])
            self.tree.insert('', tk.END, values=(row[0], row[1], row[2], row[3], formatted_notes))

        # Highlight the entries matching the search term
        for child in self.tree.get_children():
            item_data = self.tree.item(child)['values']
            if search_term.strip('%').lower() in ' '.join(str(v).lower() for v in item_data):
                matching_entries.append((child, item_data))
            else:
                non_matching_entries.append((child, item_data))

        for entry in matching_entries:
            self.tree.item(entry[0], tags=('highlight',))
        self.tree.tag_configure('highlight', background='yellow')

    def perform_item_search(self):
        selected_item = self.item_var.get()
        self.last_search_term = selected_item
        query = """
        SELECT Dungeon.Glyph, Dungeon.Category, Dungeon.Status, Dungeon.Bosses, Dungeon.Notes
        FROM Dungeon
        JOIN Dungeon_Equipment ON Dungeon.Glyph = Dungeon_Equipment.Glyph
        WHERE Dungeon_Equipment.EquipmentName = ?
        """
        self.cursor.execute(query, (selected_item,))
        results = self.cursor.fetchall()

        # Re-populate the treeview with search results
        self.tree.delete(*self.tree.get_children())
        for row in results:
            formatted_notes = self.format_notes(row[4])
            self.tree.insert('', tk.END, values=(row[0], row[1], row[2], row[3], formatted_notes))

        # Highlight the entries matching the search term
        for child in self.tree.get_children():
            item_data = self.tree.item(child)['values']
            if selected_item.lower() in ' '.join(str(v).lower() for v in item_data):
                self.tree.item(child, tags=('highlight',))

        self.tree.tag_configure('highlight', background='#f0f0f0')  # Subtle gray background

    def reset_app(self):
        self.item_var.set('')
        self.equipment_type_var.set('')
        self.last_search_term = ''
        self.detail_frame.delete('1.0', tk.END)
        self.tree.delete(*self.tree.get_children())  # Clear the treeview
        self.load_all_dungeons()  # Reload all dungeons
        self.tree.tag_configure('highlight', background='white')  # Reset highlights

    def setup_widgets(self):
        # Dropdown for equipment type search
        self.equipment_type_var = tk.StringVar()
        self.equipment_type_combobox = ttk.Combobox(self.root, textvariable=self.equipment_type_var, values=self.equipment_types, width=60)
        self.equipment_type_combobox.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.equipment_type_combobox.bind('<<ComboboxSelected>>', self.update_item_dropdown)

        # Dropdown for item search
        self.item_var = tk.StringVar()
        self.item_combobox = ttk.Combobox(self.root, textvariable=self.item_var, values=self.items, width=60)
        self.item_combobox.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        # Bind Enter key to perform search
        self.item_combobox.bind('<Return>', self.perform_item_search)

        # Search button
        self.search_button = ttk.Button(self.root, text='Search', command=self.perform_search)
        self.search_button.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        # Item search button
        self.item_search_button = ttk.Button(self.root, text='Search Item', command=self.perform_item_search)
        self.item_search_button.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

        # Reset button
        self.reset_button = ttk.Button(self.root, text='Reset', command=self.reset_app)
        self.reset_button.grid(row=0, column=4, padx=10, pady=10, sticky="ew")

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
        self.tree.grid(row=1, column=0, columnspan=5, sticky='nsew', padx=10, pady=10)

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        # Detail frame for displaying full note on row click
        self.detail_frame = tk.Text(self.root, height=10, wrap='word')
        self.detail_frame.grid(row=2, column=0, columnspan=5, sticky='nsew', padx=10, pady=10)

        # Configure grid column configuration
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=0)
        self.root.grid_columnconfigure(2, weight=0)
        self.root.grid_columnconfigure(3, weight=0)
        self.root.grid_columnconfigure(4, weight=0)

    def load_equipment_types(self):
        # This function loads all unique equipment types
        query = "SELECT DISTINCT Category FROM Equipment"
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        return [category[0] for category in records]

    def update_item_dropdown(self, event=None):
        selected_type = self.equipment_type_var.get()
        query = "SELECT EquipmentName FROM Equipment WHERE Category = ?"
        self.cursor.execute(query, (selected_type,))
        records = self.cursor.fetchall()
        self.items = [item[0] for item in records]
        self.item_combobox['values'] = self.items

    def load_all_dungeons(self):
        # This function loads all dungeons into the treeview
        query = "SELECT Glyph, Category, Status, Bosses, Notes FROM Dungeon"
        self.cursor.execute(query)
        for row in self.cursor.fetchall():
            formatted_notes = self.format_notes(row[4])
            self.tree.insert('', tk.END, values=(row[0], row[1], row[2], row[3], formatted_notes))

    def format_notes(self, notes):
        # Format notes by adding new lines after certain layers
        for layer in ['L1:', 'L1', 'L2:', 'L2', 'L3:', 'L3', 'L4:', 'L4', 'L5:', 'L5', 'layer', 'Layer']:
            notes = notes.replace(layer, '\n' + layer)
        return notes

    def highlight_text(self, terms_tags):
        """Highlights the search terms in the detailed notes with the specified tags."""
        if not terms_tags:
            return  # If there are no terms, do nothing

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

    def highlight_items(self, event=None):
        selected_item = self.item_var.get()
        matching_entries = []
        non_matching_entries = []
        for child in self.tree.get_children():
            item_data = self.tree.item(child)['values']
            if selected_item.lower() in ' '.join(str(v).lower() for v in item_data):
                matching_entries.append((child, item_data))
            else:
                non_matching_entries.append((child, item_data))

        # Clear the tree and re-insert items with matches first
        self.tree.delete(*self.tree.get_children())
        for entry in matching_entries + non_matching_entries:
            # Determine if it's a match based on whether it's in the matching entries list
            is_match = entry in matching_entries
            tags = ('highlight',) if is_match else ('normal',)
            self.tree.insert('', tk.END, values=entry[1], tags=tags)

        # Update the visual styling for matches
        self.tree.tag_configure('highlight', background='#f0f0f0')  # Subtle gray background
        self.tree.tag_configure('normal', background='white')

        # Refresh the binding to ensure it remains after updating the treeview
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

    def on_tree_select(self, event):
        selected_item = self.tree.selection()[0] if self.tree.selection() else None
        if selected_item:
            item_data = self.tree.item(selected_item)['values']
            notes = self.format_notes(item_data[-1])  # Assuming the last index has the notes

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

    def on_closing(self):
        self.conn.close()
        self.root.destroy()


def main():
    root = tk.Tk()
    app = DungeonApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()


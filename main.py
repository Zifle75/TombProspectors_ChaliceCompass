import sqlite3
import tkinter as tk
from tkinter import ttk


class DungeonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chalice Compass")

        # Set up the database connection
        self.conn = sqlite3.connect('ChaliceCompass.db')
        self.cursor = self.conn.cursor()

        # Load all items for the search dropdown
        self.items = self.load_items()

        # GUI Setup
        self.setup_widgets()

        # Load all dungeons by default
        self.load_all_dungeons()

    def setup_widgets(self):
        # Dropdown for item search
        self.item_var = tk.StringVar()
        self.item_combobox = ttk.Combobox(self.root, textvariable=self.item_var, values=self.items)
        self.item_combobox.pack(side=tk.TOP, fill=tk.X, padx=10)
        self.item_combobox.bind('<<ComboboxSelected>>', self.highlight_items)

        # Treeview for displaying dungeons
        self.tree = ttk.Treeview(self.root, columns=('Glyph', 'Category', 'Status', 'Bosses', 'Notes'), show='headings',
                                 height=15)
        self.tree.heading('Glyph', text='Glyph')
        self.tree.heading('Category', text='Category')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Bosses', text='Bosses')
        self.tree.heading('Notes', text='Notes')
        self.tree.column('Glyph', width=100)
        self.tree.column('Category', width=100)
        self.tree.column('Status', width=100)
        self.tree.column('Bosses', width=150)
        self.tree.column('Notes', width=500)  # Increased width for Notes
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        # Detail frame for displaying full note on row click
        self.detail_frame = tk.Text(self.root, height=10, wrap='word')
        self.detail_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)

    def load_items(self):
        # This function loads all unique items mentioned in the notes
        query = "SELECT DISTINCT EquipmentName FROM Equipment"
        self.cursor.execute(query)
        records = self.cursor.fetchall()
        return [item[0] for item in records]

    def load_all_dungeons(self):
        # This function loads all dungeons into the treeview
        query = "SELECT Glyph, Category, Status, Bosses, Notes FROM Dungeon"
        self.cursor.execute(query)
        for row in self.cursor.fetchall():
            formatted_notes = self.format_notes(row[4])
            self.tree.insert('', tk.END, values=(row[0], row[1], row[2], row[3], formatted_notes))

    def format_notes(self, notes):
        # Format notes by adding new lines after certain layers
        for layer in ['L1:', 'L1', 'L2:', 'L2', 'L3:', 'L3', 'L4:', 'L4', 'L5:', 'L5']:
            notes = notes.replace(layer, '\n' + layer)
        return notes

    def highlight_items(self, event=None):
        # Highlight items in the notes that match the selected item in the dropdown
        selected_item = self.item_var.get()
        matching_entries = []
        non_matching_entries = []
        for child in self.tree.get_children():
            item_data = self.tree.item(child)['values']
            if selected_item.lower() in item_data[4].lower():
                matching_entries.append((child, item_data))
            else:
                non_matching_entries.append((child, item_data))

        self.tree.delete(*self.tree.get_children())
        for entry in matching_entries + non_matching_entries:
            self.tree.insert('', tk.END, values=entry[1],
                             tags=('highlight' if entry in matching_entries else 'normal',))

        self.tree.tag_configure('highlight', background='yellow')
        self.tree.tag_configure('normal', background='white')

    def on_tree_select(self, event):
        # Display detailed notes when a tree row is selected
        selected_item = self.tree.selection()
        item_data = self.tree.item(selected_item)['values']
        self.detail_frame.delete('1.0', tk.END)
        self.detail_frame.insert(tk.END, item_data[-1])

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

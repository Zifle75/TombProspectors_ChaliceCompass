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
        self.tree.column('Notes', width=350)
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

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
            self.tree.insert('', tk.END, values=row)

    def highlight_items(self, event=None):
        # Highlight items in the notes that match the selected item in the dropdown
        selected_item = self.item_var.get()
        for child in self.tree.get_children():
            item_data = self.tree.item(child)['values']
            if selected_item.lower() in item_data[4].lower():  # Assuming the notes are in the fifth column
                self.tree.item(child, tags=('highlight',))
            else:
                self.tree.item(child, tags=('normal',))

        self.tree.tag_configure('highlight', background='yellow')
        self.tree.tag_configure('normal', background='white')

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

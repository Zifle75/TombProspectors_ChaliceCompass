import sqlite3
import tkinter as tk
from tkinter import ttk

class DungeonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Chalice Compass")

        # Setting up the SQLite connection
        self.conn = sqlite3.connect('ChaliceCompass.db')
        self.cursor = self.conn.cursor()

        # Layout configuration
        self.setup_widgets()

    def setup_widgets(self):
        # Search field and button
        self.search_var = tk.StringVar()
        self.entry = ttk.Entry(self.root, textvariable=self.search_var)
        self.entry.pack(side=tk.TOP, padx=10, fill=tk.X)
        self.search_button = ttk.Button(self.root, text="Search", command=self.search_dungeons)
        self.search_button.pack(side=tk.TOP, pady=5)

        # Treeview for displaying the dungeons
        self.tree = ttk.Treeview(self.root, columns=('Glyph', 'Category', 'Status', 'Bosses', 'Notes'), show='headings')
        self.tree.heading('Glyph', text='Glyph')
        self.tree.heading('Category', text='Category')
        self.tree.heading('Status', text='Status')
        self.tree.heading('Bosses', text='Bosses')
        self.tree.heading('Notes', text='Notes')
        self.tree.column('Glyph', width=100)
        self.tree.column('Category', width=120)
        self.tree.column('Status', width=80)
        self.tree.column('Bosses', width=150)
        self.tree.column('Notes', width=300)
        self.tree.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

    def search_dungeons(self):
        # Clear current entries in the treeview
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Fetch dungeons from the database
        search_term = self.search_var.get()
        query = "SELECT Glyph, Category, Status, Bosses, Notes FROM Dungeon WHERE Glyph LIKE ?"
        self.cursor.execute(query, ('%' + search_term + '%',))
        records = self.cursor.fetchall()

        # Populate the treeview with new entries
        for row in records:
            self.tree.insert('', tk.END, values=row)

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

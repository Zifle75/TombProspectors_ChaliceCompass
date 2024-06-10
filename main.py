import sqlite3
import tkinter as tk
from tkinter import ttk
import threading

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

        self.db_lock = threading.Lock()
        self.db_paths = ['ChaliceCompass.db', 'ChaliceCompass_backup.db']
        self.conn = None
        self.cursor = None
        self.connect_to_db()

        # Load all items for the search dropdown
        self.items = self.load_items()

        # GUI Setup
        self.setup_widgets()

        # Store last search term used
        self.last_search_term = ""

        # Load all dungeons by default
        self.load_all_dungeons()

    def connect_to_db(self):
        for db_path in self.db_paths:
            try:
                self.conn = sqlite3.connect(db_path)
                self.cursor = self.conn.cursor()
                break
            except sqlite3.Error as e:
                print(f"Failed to connect to {db_path}: {e}")
        if not self.conn:
            raise Exception("Failed to connect to any database.")

    def execute_query(self, query, params=()):
        with self.db_lock:
            try:
                self.cursor.execute(query, params)
                self.conn.commit()
                return self.cursor.fetchall()
            except sqlite3.Error as e:
                print(f"Database error: {e}")
                self.connect_to_db()

    def treeview_sort_column(self, col, reverse):
        l = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        l.sort(reverse=reverse, key=lambda t: t[0].lower())

        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)

        reverse = not reverse
        self.tree.heading(col, command=lambda: self.treeview_sort_column(col, reverse))

    def perform_search(self, event=None):
        search_term = self.search_var.get()
        self.last_search_term = search_term
        query = "SELECT Glyph, Category, Status, Bosses, Notes FROM Dungeon WHERE Notes LIKE ?"
        results = self.execute_query(query, (f'%{search_term}%',))

        self.tree.delete(*self.tree.get_children())
        for row in results:
            formatted_notes = self.format_notes(row[4])
            self.tree.insert('', tk.END, values=(row[0], row[1], row[2], row[3], formatted_notes))

    def setup_widgets(self):
        self.item_var = tk.StringVar()
        self.search_var = tk.StringVar()

        self.item_combobox = ttk.Combobox(self.root, textvariable=self.item_var, values=self.items, width=60)
        self.item_combobox.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.search_entry = ttk.Entry(self.root, textvariable=self.search_var, width=60)
        self.search_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        self.search_entry.bind('<Return>', self.perform_search)

        self.search_button = ttk.Button(self.root, text='Search', command=self.perform_search)
        self.search_button.grid(row=0, column=2, padx=10, pady=10, sticky="ew")

        self.reset_button = ttk.Button(self.root, text='Reset', command=self.reset)
        self.reset_button.grid(row=0, column=3, padx=10, pady=10, sticky="ew")

        self.tree = ttk.Treeview(self.root, columns=('Glyph', 'Category', 'Status', 'Bosses', 'Notes'), show='headings', height=15)
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
        self.tree.grid(row=1, column=0, columnspan=4, sticky='nsew', padx=10, pady=10)

        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

        self.detail_frame = tk.Text(self.root, height=10, wrap='word')
        self.detail_frame.grid(row=2, column=0, columnspan=4, sticky='nsew', padx=10, pady=10)

        self.update_status_button = ttk.Button(self.root, text='Update Status', command=self.update_dungeon_status)
        self.update_status_button.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="ew")

        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_columnconfigure(3, weight=1)

    def load_items(self):
        query = "SELECT DISTINCT EquipmentName FROM Equipment"
        records = self.execute_query(query)
        return [item[0] for item in records]

    def load_all_dungeons(self):
        query = "SELECT Glyph, Category, Status, Bosses, Notes FROM Dungeon"
        results = self.execute_query(query)
        self.tree.delete(*self.tree.get_children())
        for row in results:
            formatted_notes = self.format_notes(row[4])
            self.tree.insert('', tk.END, values=(row[0], row[1], row[2], row[3], formatted_notes))

    def format_notes(self, notes):
        for layer in LAYER_COLORS.keys():
            notes = notes.replace(layer, '\n' + layer)
        return notes

    def highlight_text(self, terms_tags):
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
        selected_item = self.tree.selection()[0] if self.tree.selection() else None
        if selected_item:
            item_data = self.tree.item(selected_item)['values']
            current_status = item_data[2]
            new_status = 'Expired' if current_status == 'Active' else 'Active'
            query = "UPDATE Dungeon SET Status = ? WHERE Glyph = ?"
            self.execute_query(query, (new_status, item_data[0]))
            self.load_all_dungeons()
            self.detail_frame.insert(tk.END, f"\nStatus updated to {new_status}")

    def reset(self):
        self.search_var.set("")
        self.item_var.set("")
        self.load_all_dungeons()
        self.detail_frame.delete('1.0', tk.END)

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

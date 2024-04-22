import tkinter as tk
from tkinter import ttk
import json
from tkinter import simpledialog


class PermalinkTab:
    def __init__(self, tab):
        self.tab = tab
        self.permalink_data = {}
        self.load_permalinks()
        self.create_table()
        self.add_button = ttk.Button(tab, text="Add Permalink", command=self.add_permalink)
        self.add_button.grid(row=1, column=0, padx=10, pady=10, sticky='sew')
        self.remove_button = ttk.Button(tab, text="Remove Selected", command=self.remove_selected)
        self.remove_button.grid(row=1, column=1, padx=10, pady=10, sticky='sew')
        self.save_button = ttk.Button(tab, text="Discard Changes", command=self.reload)
        self.save_button.grid(row=1, column=2, padx=10, pady=10, sticky='sew')
        self.save_button = ttk.Button(tab, text="Save Changes", command=self.save_changes)
        self.save_button.grid(row=1, column=3, padx=10, pady=10, sticky='sew')

        for i in range(4):
            self.tab.columnconfigure(i, weight=1)
        self.tab.rowconfigure(0, weight=1)

    def load_permalinks(self):
        with open('file/settings/permanent_link.json', 'r') as file:
            self.permalink_data = json.load(file)

    def create_table(self):
        self.tree = ttk.Treeview(self.tab, columns=("permalink"), show="headings")
        self.tree.heading("permalink", text="Permalink")
        self.tree.grid(row=0, column=0, columnspan=4, padx=10, pady=10, sticky='nsew')
        for permalink in self.permalink_data['formats']:
            self.tree.insert("", "end", values=(permalink,))

    def add_permalink(self):
        new_permalink = tk.simpledialog.askstring("Add Permalink", "Enter the permalink:")
        if new_permalink:
            self.permalink_data['formats'].append(new_permalink)
            self.tree.insert("", "end", values=(new_permalink,))
            self.save_button.config(text='Save Changes')

    def remove_selected(self):
        selection = self.tree.selection()
        for item in selection:
            permalink = self.tree.item(item, "values")[0]
            self.tree.delete(item)
            self.permalink_data['formats'].remove(permalink)
            self.save_button.config(text='Save Changes')

    def reload(self):
        self.load_permalinks()
        self.tree.delete(*self.tree.get_children())
        for permalink in self.permalink_data['formats']:
            self.tree.insert("", "end", values=(permalink,))

    def save_changes(self):
        with open('file/settings/permanent_link.json', 'w') as file:
            json.dump(self.permalink_data, file, indent=4)
        self.save_button.config(text='Saved!')

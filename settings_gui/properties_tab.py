import tkinter as tk
from tkinter import ttk
import json
from tkinter import simpledialog


class PropertiesTab:
    def __init__(self, tab):
        self.tab = tab
        self.properties_data = {}
        self.load_properties()
        self.create_widgets()

    def create_widgets(self):
        self.create_key_dropdown()
        self.create_table()
        self.add_button = ttk.Button(self.tab, text="Add Property", command=self.add_property)
        self.add_button.grid(row=1, column=0, padx=10, pady=10, sticky='sew')
        self.remove_button = ttk.Button(self.tab, text="Remove Selected", command=self.remove_selected)
        self.remove_button.grid(row=1, column=1, padx=10, pady=10, sticky='sew')
        self.reload_button = ttk.Button(self.tab, text="Discard Changes", command=self.reload)
        self.reload_button.grid(row=1, column=3, padx=10, pady=10, sticky='sew')
        self.save_button = ttk.Button(self.tab, text="Save Changes", command=self.save_changes)
        self.save_button.grid(row=1, column=4, padx=10, pady=10, sticky='sew')

        for i in range(5):
            self.tab.columnconfigure(i, weight=1)
        self.tab.rowconfigure(0, weight=1)

    def load_properties(self):
        with open('file/settings/properties.json', 'r') as file:
            self.properties_data = json.load(file)

    def create_key_dropdown(self):
        self.key_var = tk.StringVar()
        keys = list(self.properties_data.keys())
        self.key_var.set(keys[0])
        self.key_dropdown = ttk.Combobox(self.tab, values=list(self.properties_data.keys()), textvariable=self.key_var)
        self.key_dropdown.grid(row=0, column=0, padx=10, pady=10, sticky='n')
        self.key_dropdown.bind("<<ComboboxSelected>>", self.update_table)

    def create_table(self):
        key = self.key_var.get()
        self.tree = ttk.Treeview(self.tab, columns=["property", "obligatory level"], show="headings")
        self.tree.heading("property", text="Property")
        self.tree.heading("obligatory level", text="obligatory level")
        self.tree.grid(row=0, column=1, columnspan=4, padx=10, pady=10, sticky='nsew')
        self.tree.bind("<Double-1>", self.on_double_click)

        for prop in self.properties_data[key]:
            values = (prop, self.properties_data[key][prop])
            self.tree.insert("", "end", values=values)

    def update_table(self, event=None):
        self.create_table()

    def on_double_click(self, event):
        item = self.tree.selection()[0]
        row_data = self.tree.item(item, "values")
        if not row_data:
            return

        dialog = tk.Toplevel(self.tab)
        dialog.title("Edit Property")

        labels = list(self.tree["columns"])

        entries = []
        for i, label in enumerate(labels):
            ttk.Label(dialog, text=label).grid(row=i, column=0, padx=5, pady=5)
            if label == "property":
                entry = ttk.Entry(dialog)
                entry.insert(0, row_data[i])
                entry.grid(row=i, column=1, padx=5, pady=5)
                entries.append(entry)
            else:
                values = ['none', "M", "R", "O"]
                initial_value = row_data[i] if row_data[
                                                   i] in values else 'none'
                combo = ttk.Combobox(dialog, values=values)
                combo.set(initial_value)
                combo.grid(row=i, column=1, padx=5, pady=5)
                entries.append(combo)

        def save_changes_():
            new_data = [entry.get() if isinstance(entry, ttk.Entry) else entry.get() for entry in entries]
            self.tree.item(item, values=new_data)
            self.properties_data[self.key_var.get()][new_data[0]] = new_data[1]
            dialog.destroy()
            self.save_button.config(text='Save Changes')

        ttk.Button(dialog, text="Save", command=save_changes_).grid(row=len(labels), columnspan=2, padx=5, pady=5)

    def add_property(self):
        new_property = simpledialog.askstring("Add Property", "Enter the property name:")
        if new_property:
            self.save_button.config(text='Save Changes')
            self.properties_data[new_property] = ''
            self.update_table()
            self.tree.yview_moveto(1.0)

    def remove_selected(self):
        selection = self.tree.selection()
        for item in selection:
            property_to_remove = self.tree.item(item, 'values')[0]
            del self.properties_data[self.key_var.get()][property_to_remove]
            self.tree.delete(item)
            self.save_button.config(text='Save Changes')
        self.update_table()

    def reload(self):
        self.load_properties()
        self.update_table()

    def save_changes(self):
        with open('file/settings/properties.json', 'w') as file:
            json.dump(self.properties_data, file, indent=4)

        self.save_button.config(text='Saved!')

import tkinter as tk
from tkinter import ttk
import json
from tkinter import simpledialog, messagebox


class VocabulariesTab:
    def __init__(self, tab):
        self.tab = tab
        self.vocabularies_data = {}
        self.selected_key = tk.StringVar()
        self.selected_key.set("")
        self.load_vocabularies()
        self.create_widgets()
        self.update_tables()

    def load_vocabularies(self):
        with open('file/settings/vocabularies_ckan.json', 'r') as file:
            self.vocabularies_data = json.load(file)

    def create_widgets(self):
        self.key_dropdown = ttk.Combobox(self.tab, values=list(self.vocabularies_data.keys()),
                                         textvariable=self.selected_key)
        self.key_dropdown.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="ew")
        self.key_dropdown.bind("<<ComboboxSelected>>", self.update_tables)

        self.remove_key_button = ttk.Button(self.tab, text="Remove Key", command=self.remove_key)
        self.remove_key_button.grid(row=0, column=3, padx=10, pady=10, sticky="ew")
        self.add_key_button = ttk.Button(self.tab, text="Add Key", command=self.add_key)
        self.add_key_button.grid(row=0, column=4, padx=10, pady=10, sticky="ew")

        self.vocabulary_table = ttk.Treeview(self.tab, columns=("Vocabulary Format",), show="headings")
        self.vocabulary_table.heading("Vocabulary Format", text="Vocabulary Format")
        self.vocabulary_table.grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        self.add_vocabulary_button = ttk.Button(self.tab, text="Add Vocabulary Format", command=self.add_vocabulary)
        self.add_vocabulary_button.grid(row=1, column=3, padx=10, pady=10, sticky="new")
        self.remove_vocabulary_button = ttk.Button(self.tab, text="Remove Selected Vocabulary Format",
                                                   command=self.remove_vocabulary)
        self.remove_vocabulary_button.grid(row=1, column=4, padx=10, pady=10, sticky="new")

        for i in range(3):
            self.tab.columnconfigure(i, weight=1)

        self.property_table = ttk.Treeview(self.tab, columns=("Property",), show="headings")
        self.property_table.heading("Property", text="Property")
        self.property_table.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")

        self.add_property_button = ttk.Button(self.tab, text="Add Property", command=self.add_property)
        self.add_property_button.grid(row=2, column=3, padx=10, pady=10, sticky="new")
        self.remove_property_button = ttk.Button(self.tab, text="Remove Selected Property",
                                                 command=self.remove_property)
        self.remove_property_button.grid(row=2, column=4, padx=10, pady=10, sticky="new")

        self.reload_button = ttk.Button(self.tab, text="Discard Changes", command=self.reload)
        self.reload_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10, sticky="sew")
        self.save_button = ttk.Button(self.tab, text="Save Changes", command=self.save_changes)
        self.save_button.grid(row=3, column=2, columnspan=3, padx=10, pady=10, sticky="sew")

        for i in range(4):
            self.tab.rowconfigure(i, weight=1)

    def update_tables(self, event=None):
        self.vocabulary_table.delete(*self.vocabulary_table.get_children())
        self.property_table.delete(*self.property_table.get_children())
        self.selected_key.set(self.selected_key.get() if self.selected_key.get() else list(self.vocabularies_data.keys())[0])

        selected_key = self.selected_key.get()

        self.key_dropdown.config(values=list(self.vocabularies_data.keys()),
                                         textvariable=self.selected_key)

        if selected_key in self.vocabularies_data:
            vocabulary_format = self.vocabularies_data[selected_key]["vocabulary_format"]
            for vf in vocabulary_format:
                self.vocabulary_table.insert("", "end", values=(vf,))

            properties = self.vocabularies_data[selected_key]["property"]
            for prop in properties:
                self.property_table.insert("", "end", values=(prop,))

    def add_key(self):
        new_key = simpledialog.askstring("Add Key", "Enter the new key:")
        if new_key:
            if new_key not in self.vocabularies_data:
                self.vocabularies_data[new_key] = {"vocabulary_format": [], "property": []}
                self.key_dropdown.config(values=list(self.vocabularies_data.keys()))
                self.selected_key.set(new_key)
                self.update_tables()
            else:
                messagebox.showwarning("Duplicate Key", "The key already exists in the dictionary.")
        self.save_button.config(text='Save Changes')

    def remove_key(self):
        key_to_remove = self.selected_key.get()
        if key_to_remove:
            self.vocabularies_data.pop(key_to_remove)
            self.key_dropdown.config(values=list(self.vocabularies_data.keys()))
            self.selected_key.set(list(self.vocabularies_data.keys())[0])
            self.update_tables()
        self.save_button.config(text='Save Changes')

    def add_vocabulary(self):
        selected_key = self.selected_key.get()
        if selected_key:
            new_vocabulary = simpledialog.askstring("Add Vocabulary Format", "Enter the new Vocabulary Format:")
            if new_vocabulary:
                self.vocabularies_data[selected_key]["vocabulary_format"].append(new_vocabulary)
                self.update_tables()
        self.save_button.config(text='Save Changes')

    def remove_vocabulary(self):
        selected_key = self.selected_key.get()
        if selected_key:
            selection = self.vocabulary_table.selection()
            if selection:
                for item in selection:
                    index = self.vocabulary_table.index(item)
                    self.vocabularies_data[selected_key]["vocabulary_format"].pop(index)
        self.update_tables()
        self.save_button.config(text='Save Changes')

    def add_property(self):
        selected_key = self.selected_key.get()
        if selected_key:
            new_property = simpledialog.askstring("Add Property", "Enter the new Property:")
            if new_property:
                self.vocabularies_data[selected_key]["property"].append(new_property)
                self.update_tables()
        self.save_button.config(text='Save Changes')

    def remove_property(self):
        selected_key = self.selected_key.get()
        if selected_key:
            selection = self.property_table.selection()
            if selection:
                for item in selection:
                    index = self.property_table.index(item)
                    self.vocabularies_data[selected_key]["property"].pop(index)
                    self.property_table.delete(item)
        self.save_button.config(text='Save Changes')

    def reload(self):
        self.load_vocabularies()
        self.update_tables()
        self.save_button.config(text='Save Changes')

    def save_changes(self):
        with open('file/settings/vocabularies_ckan.json', 'w') as file:
            json.dump(self.vocabularies_data, file, indent=4)
        self.save_button.config(text='Saved!')

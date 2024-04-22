import tkinter as tk
from tkinter import ttk
import json


class FormatTab:
    def __init__(self, tab):
        self.tab = tab
        self.formats = {}
        self.load_formats()
        self.format_var = tk.StringVar()
        self.format_var.set(list(self.formats.keys())[0])
        self.format_dropdown = ttk.Combobox(tab, values=list(self.formats.keys()), textvariable=self.format_var)
        self.format_dropdown.grid(row=0, column=0, padx=10, pady=10)
        self.add_format_button = ttk.Button(tab, text="Add Format", command=self.open_add_format_dialog)
        self.add_format_button.grid(row=0, column=1, padx=10, pady=10)
        self.format_point_label = ttk.Label(self.tab, text="point").grid(row=1, column=0, padx=5, pady=5)
        self.format_point_combobox = ttk.Combobox(self.tab, values=list(range(11)))
        self.format_point_combobox.grid(row=1, column=1, padx=5, pady=5)
        self.format_np_label = ttk.Label(self.tab, text="non-proprietary").grid(row=2, column=0, padx=5, pady=5)
        self.format_np_combobox = ttk.Combobox(self.tab, values=['yes', 'no'])
        self.format_np_combobox.grid(row=2, column=1, padx=5, pady=5)
        self.format_point_label = ttk.Label(self.tab, text="machine-readable").grid(row=3, column=0, padx=5, pady=5)
        self.format_mr_combobox = ttk.Combobox(self.tab, values=['yes', 'no', 'almost'])
        self.format_mr_combobox.grid(row=3, column=1, padx=5, pady=5)
        self.format_mr_combobox.bind("<<ComboboxSelected>>", self.modified)
        self.format_np_combobox.bind("<<ComboboxSelected>>", self.modified)
        self.format_point_combobox.bind("<<ComboboxSelected>>", self.modified)
        self.format_var.trace("w", self.update_format)
        self.reload_button = ttk.Button(self.tab, text="Discard Changes", command=self.reload)
        self.reload_button.grid(row=4, column=0, pady=10, sticky='sew')
        self.save_button = ttk.Button(self.tab, text="Save Changes", command=self.save_changes)
        self.save_button.grid(row=4, column=1, pady=10, sticky='sew')
        for i in range(2):
            self.tab.columnconfigure(i, weight=1)
        for i in range(5):
            self.tab.rowconfigure(i, weight=1)

        self.update_format()

    def modified(self, event):
        self.save_button.config(text='Save Changes')

    def update_format(self, *args):
        self.save_button.config(text='Save Changes')

        format_name = self.format_var.get()
        format_data = self.formats.get(format_name, {})
        self.format_mr_combobox.set(format_data["machine-readable"])
        self.format_np_combobox.set(format_data["non-proprietary"])
        self.format_point_combobox.set(str(format_data["point"]))

    def load_formats(self):
        with open('file/settings/format.json', 'r') as file:
            self.formats = json.load(file)

    def open_add_format_dialog(self):
        self.add_format_dialog = tk.Toplevel(self.tab)
        self.add_format_dialog.title("Add Format")

        ttk.Label(self.add_format_dialog, text="Format Name:").grid(row=0, column=0, padx=5, pady=5)
        self.new_format_name_entry = ttk.Entry(self.add_format_dialog)
        self.new_format_name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.add_format_dialog, text="Point:").grid(row=1, column=0, padx=5, pady=5)
        self.new_format_point_entry = ttk.Entry(self.add_format_dialog)
        self.new_format_point_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(self.add_format_dialog, text="Non-proprietary:").grid(row=2, column=0, padx=5, pady=5)
        self.new_format_non_proprietary_var = tk.StringVar()
        self.new_format_non_proprietary_var.set("yes")
        self.new_format_non_proprietary_dropdown = ttk.Combobox(self.add_format_dialog, values=["yes", "no"], textvariable=self.new_format_non_proprietary_var)
        self.new_format_non_proprietary_dropdown.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(self.add_format_dialog, text="Machine-readable:").grid(row=3, column=0, padx=5, pady=5)
        self.new_format_machine_readable_var = tk.StringVar()
        self.new_format_machine_readable_var.set("yes")
        self.new_format_machine_readable_dropdown = ttk.Combobox(self.add_format_dialog, values=["yes", "no"], textvariable=self.new_format_machine_readable_var)
        self.new_format_machine_readable_dropdown.grid(row=3, column=1, padx=5, pady=5)

        add_button = ttk.Button(self.add_format_dialog, text="Add", command=self.add_new_format)
        add_button.grid(row=4, column=0, columnspan=2, padx=5, pady=5)

    def add_new_format(self):
        self.save_button.config(text='Save Changes')

        new_format_name = self.new_format_name_entry.get()
        new_format_point = int(self.new_format_point_entry.get())
        new_format_non_proprietary = self.new_format_non_proprietary_var.get()
        new_format_machine_readable = self.new_format_machine_readable_var.get()

        new_format_data = {
            "point": new_format_point,
            "non-proprietary": new_format_non_proprietary,
            "machine-readable": new_format_machine_readable,
            "id": max(self.formats.values(), key=lambda x: isinstance(x, dict) and x['id'])['id'] + 1
        }

        self.formats[new_format_name] = new_format_data
        self.format_dropdown['values'] = list(self.formats.keys())
        self.add_format_dialog.destroy()
        self.format_dropdown.set(new_format_name)

    def reload(self):
        self.load_formats()
        self.update_format()

    def save_changes(self):
        selected_format_name = self.format_var.get()

        self.formats[selected_format_name]['point'] = int(self.format_point_combobox.get())
        self.formats[selected_format_name]['machine-readable'] = self.format_mr_combobox.get()
        self.formats[selected_format_name]['non-proprietary'] = self.format_np_combobox.get()
        self.formats.pop('max_point')
        self.formats['max_point'] = max(self.formats.values(), key=lambda x: int(x['point']))['point']
        with open('file/settings/format.json', 'w') as file:
            json.dump(self.formats, file, indent=4)

        self.save_button.config(text='Saved!')
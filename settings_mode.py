import tkinter as tk
from tkinter import ttk

from settings_gui.format_tab import FormatTab
from settings_gui.permalink_tab import PermalinkTab
from settings_gui.properties_tab import PropertiesTab
from settings_gui.vocabularies_tab import VocabulariesTab

def run():
    root = tk.Tk()
    root.title("Settings modifier")

    root.wm_state('zoomed')

    notebook = ttk.Notebook(root)
    notebook.pack(fill='both', expand=True)

    format_tab = ttk.Frame(notebook)
    permalink_tab = ttk.Frame(notebook)
    properties_tab = ttk.Frame(notebook)
    vocabularies_tab = ttk.Frame(notebook)

    notebook.add(format_tab, text='Format')
    notebook.add(permalink_tab, text='Permalink')
    notebook.add(properties_tab, text='Properties')
    notebook.add(vocabularies_tab, text='Vocabularies')

    format_tab_instance = FormatTab(format_tab)
    permalink_tab_instance = PermalinkTab(permalink_tab)
    properties_tab_instance = PropertiesTab(properties_tab)
    vocabularies_tab_instance = VocabulariesTab(vocabularies_tab)

    root.mainloop()

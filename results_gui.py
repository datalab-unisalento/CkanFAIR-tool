import json
import tkinter as tk
from tkinter import ttk

def display_results(results):
    root = tk.Tk()
    dataset_name = list(results.keys())[0]
    root.title(f"Dataset Results for {dataset_name}")

    root.state('zoomed')

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill=tk.BOTH)

    for dataset_id, report in results[dataset_name].items():
        tab = ttk.Frame(notebook)
        notebook.add(tab, text=dataset_id)

        for principle, principle_report in report.items():
            frame = ttk.Frame(tab)
            frame.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
            ttk.Label(frame, text=principle).pack()

            tree = ttk.Treeview(frame, columns=("error",), selectmode="browse")
            tree.heading("#0", text="Metric")
            tree.heading("error", text="Warning")

            # Calcola il numero di righe nella tabella
            num_rows = sum(len(errors) for errors in principle_report.values())

            # Imposta l'altezza minima del widget Treeview
            min_height = min(200, num_rows * 20)  # altezza minima di 200 pixel o sufficiente a contenere tutte le righe
            tree.configure(height=min_height)

            # Aggiungi una barra di scorrimento verticale se necessario
            vsb = ttk.Scrollbar(tree, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=vsb.set)
            vsb.pack(side="right", fill="y")

            tree.pack(side=tk.TOP, padx=10, pady=5, fill=tk.BOTH, expand=True)

            # Ottieni la larghezza della finestra principale e calcola la larghezza della prima colonna
            root.update()
            tree_width = tree.winfo_width()
            first_column_width = int(tree_width * 0.1)

            # Imposta la larghezza della prima colonna
            tree.column("#0", width=first_column_width)

            for subprinciple, errors in principle_report.items():
                for error in errors:
                    tree.insert("", "end", text=subprinciple, values=(error,))

    root.mainloop()

# Carica i risultati dal file JSON
with open('logs/report2.txt') as f:
    results = json.load(f)

# Visualizza i risultati
display_results(results)

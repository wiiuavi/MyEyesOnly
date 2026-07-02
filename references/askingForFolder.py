import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()
selectedFolder = filedialog.askdirectory(title="Select a Folder")

if selectedFolder:
    print(f"User selected: {selectedFolder}")
else:
    print("User cancelled the selection.")

#would use this to decide where to store the db and output folder
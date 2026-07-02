#this was taken from some stackoverflow, how to prompt a user for a txt file

import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()

filePath = filedialog.askopenfilename(
    title="Select a File",
    filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
)

if filePath:
    print(f"User selected: {filePath}")
else:
    print("User cancelled the operation.")

#would ask for zip files to encrypt/decrypt
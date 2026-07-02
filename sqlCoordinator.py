#will run this if user specifies first time running program
import sqlite3
import os
import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk

#will hold the sql db and output folder
def askForDir():
    root = tk.Tk()
    root.withdraw()
    selectedFolder = filedialog.askdirectory(title="Select a Folder to hold your key seed db")

    if selectedFolder:
        print(f"User selected: {selectedFolder}")
        return selectedFolder
    else:
        print("User cancelled the selection.")
        return None

def askForFile():
    root = tk.Tk()
    root.withdraw()
    filePath = filedialog.askopenfilename(
        title="Select a File",
        filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
    )
    if filePath:
        print(f"User selected: {filePath}")
        return filePath
    else:
        print("User cancelled the operation.")
        return None
    
#os.path.getsize("/path/to/file..something") return filesize in bytes
#https://www.sqlite.org/datatype3.html >> "BLOB. The value is a blob of data, stored exactly as it was input." will prolly store the key with this


#will run this if user specifies first time running program
def tableConnection():
    mainFolder = askForDir()
    if mainFolder is None:
        return None, None
    con = sqlite3.connect("importantKeysDontDel.db")
    cur = con.cursor()

#ik the below has errors, its a draft gng alloww meee
    cur.execute('''
            CREATE TABLE IF NOT EXISTS keymap (
                CreateID INTEGER PRIMARY KEY NOT NULL,
                DateOfCreation TEXT NOT NULL,
                FileName TEXT NOT NULL
                Key INTEGER NOT NULL
                Status INTEGER NOT NULL
                )
            ''')
    con.commit()
    return cur, con

cur, con = tableConnection()
if (cur is None) or (con is None):
    print("Could not connect to db, please select a real directory")




    

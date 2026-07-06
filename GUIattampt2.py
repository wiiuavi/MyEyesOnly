import os
import tkinter as tk
from tkinter import messagebox

import ttkbootstrap as ttk
from ttkbootstrap.widgets.scrolled import ScrolledText

from basicallyEverythingRedone import askForFile, askForDir, tableConnection, encryptAndSplitFile, decryptAndMergeFiles

homeBodyWidget = None
decryptBodyWidget = None
rightPlaceholder = None


def formatRecords(records, dbPath=None):
    lines = []
    if dbPath:
        lines.append(f"Database: {dbPath}")
        lines.append("")
    if not records:
        lines.append("No records found.")
    else:
        for record in records:
            lines.append(f"ID: {record[0]} | Date: {record[1]} | File: {record[2]} | Status: {record[3]}")
    return "\n".join(lines)


def refreshHomeText(cur, textWidget, dbPath):
    if textWidget is None or cur is None:
        return
    try:
        cur.execute("SELECT CreateID, DateOfCreation, FileName, Status FROM keymap ORDER BY CreateID")
        records = cur.fetchall()
        textWidget.text.configure(state="normal")
        textWidget.text.delete("1.0", "end")
        textWidget.text.insert("1.0", formatRecords(records, dbPath))
        textWidget.text.configure(state="disabled")

        global rightPlaceholder
        if rightPlaceholder is not None:
            rightPlaceholder.config(text=f"Files encrypted: {len(records)}")
    except Exception as exc:
        messagebox.showerror("Database error", str(exc))


def refreshDecryptText(cur, textWidget, dbPath):
    if textWidget is None or cur is None:
        return
    try:
        cur.execute("SELECT CreateID, DateOfCreation, FileName, Status FROM keymap ORDER BY CreateID DESC LIMIT 5")
        records = cur.fetchall()
        textWidget.text.configure(state="normal")
        textWidget.text.delete("1.0", "end")
        textWidget.text.insert("1.0", formatRecords(records, dbPath))
        textWidget.text.configure(state="disabled")
    except Exception as exc:
        messagebox.showerror("Database error", str(exc))


def makeTab(notebook, title):
    frame = ttk.Frame(notebook)
    titleLabel = ttk.Label(frame, text=title, font=(None, 24, "bold"))
    titleLabel.pack(anchor="nw", padx=20, pady=(20, 5))

    placeholder = ttk.Label(frame, text="placeholder", bootstyle="light", font=(None, 14))
    placeholder.pack(anchor="nw", padx=20, pady=(0, 20))

    separator = ttk.Separator(frame, orient="horizontal")
    separator.pack(fill="x", padx=20, pady=(0, 20))
    return frame


def makeHomeTab(notebook, cur, con, dbPath):
    frame = ttk.Frame(notebook)
    titleLabel = ttk.Label(frame, text="Home", font=(None, 24, "bold"))
    titleLabel.pack(anchor="nw", padx=20, pady=(20, 5))

    placeholderRow = ttk.Frame(frame)
    placeholderRow.pack(anchor="nw", padx=20, pady=(0, 20), fill="x")

    placeholder = ttk.Label(placeholderRow, text="Here, review previous encryptions and delete any un-needed records. See the mainfolder you selected for results", bootstyle="light", font=(None, 14))
    placeholder.pack(side="left")

    rightColumn = ttk.Frame(placeholderRow)
    rightColumn.pack(side="right")

    def openMainFolder():
        try:
            if not dbPath:
                messagebox.showerror("No folder", "No main folder is set.")
                return
            try:
                os.startfile(dbPath)
            except Exception:
                try:
                    import subprocess
                    subprocess.Popen(["explorer", dbPath])
                except Exception as exc:
                    messagebox.showerror("Open folder failed", str(exc))
        except Exception as exc:
            messagebox.showerror("Open folder failed", str(exc))

    openFolderButton = ttk.Button(rightColumn, text="Open Main Folder", bootstyle="secondary", command=openMainFolder)
    openFolderButton.pack(side="top", padx=(6, 0), pady=(0, 4))

    global rightPlaceholder
    rightPlaceholder = ttk.Label(rightColumn, text="Files encrypted: 0", bootstyle="light", font=(None, 14))
    rightPlaceholder.pack(side="top")

    separator = ttk.Separator(frame, orient="horizontal")
    separator.pack(fill="x", padx=20, pady=(0, 20))

    body = ScrolledText(frame, autohide=True)
    body.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    global homeBodyWidget
    homeBodyWidget = body
    refreshHomeText(cur, body, dbPath)

    bottomFrame = ttk.Frame(frame)
    bottomFrame.pack(anchor="nw", padx=20, pady=(0, 20), fill="x")

    spinLabel = ttk.Label(bottomFrame, text="Entry ID:", font=(None, 12))
    spinLabel.pack(side="left")

    valueSpin = ttk.Spinbox(bottomFrame, from_=1, to=999999, width=8)
    valueSpin.set(1)
    valueSpin.pack(side="left", padx=(10, 0))

    def deleteEntry():
        try:
            entry_id = int(valueSpin.get())
        except Exception:
            messagebox.showerror("Invalid ID", "Please enter a valid numeric ID to delete.")
            return

        try:
            cur.execute("SELECT CreateID FROM keymap WHERE CreateID = ?", (entry_id,))
            row = cur.fetchone()
            if not row:
                messagebox.showerror("Not found", f"No database entry with ID {entry_id}.")
                return

            confirm = messagebox.askyesno("Confirm deletion", f"Delete entry ID {entry_id}? This cannot be undone.")
            if not confirm:
                return

            cur.execute("DELETE FROM keymap WHERE CreateID = ?", (entry_id,))
            con.commit()
            messagebox.showinfo("Deleted", f"Entry {entry_id} deleted.")
            # refresh displays
            refreshHomeText(cur, body, dbPath)
            try:
                refreshDecryptText(cur, decryptBodyWidget, dbPath)
            except Exception:
                pass
        except Exception as exc:
            messagebox.showerror("Error deleting entry", str(exc))

    dangerButton = ttk.Button(bottomFrame, text="Delete entry", bootstyle="danger", command=deleteEntry)
    dangerButton.pack(side="left", padx=20)

    return frame


def makeEncryptTab(notebook, mainFolder, cur, con):
    frame = ttk.Frame(notebook)
    titleLabel = ttk.Label(frame, text="Encrypt / Split", font=(None, 24, "bold"))
    titleLabel.pack(anchor="nw", padx=20, pady=(20, 5))

    placeholder = ttk.Label(frame, text="Here, encrypt files and split them if needed. Select a file to begin. NOTE: This will make an encrypted copy of your file.", bootstyle="light", font=(None, 14))
    placeholder.pack(anchor="nw", padx=20, pady=(0, 20))

    separator = ttk.Separator(frame, orient="horizontal")
    separator.pack(fill="x", padx=20, pady=(0, 20))

    buttonRow = ttk.Frame(frame)
    buttonRow.pack(anchor="nw", padx=20)

    selectedFile = {'path': None}
    progressVar = tk.DoubleVar(value=0.0)

    def chooseFile():
        filePath = askForFile()
        if filePath:
            selectedFile['path'] = filePath
            infoText.config(text=f"Selected file: {os.path.basename(filePath)}")

    def updateProgress(progress):
        progressVar.set(progress)
        progressLabel.config(text=f"{progress:.2f}%")
        frame.update_idletasks()

    selectFileButton = ttk.Button(buttonRow, text="Select Source File", bootstyle="info", command=chooseFile)
    selectFileButton.pack(side="left")

    infoText = ttk.Label(buttonRow, text="No file selected.", bootstyle="light", font=(None, 14))
    infoText.pack(side="left", padx=(12, 0))


    def runEncrypt():
        if not selectedFile['path']:
            messagebox.showerror("Missing file", "Please select a source file to encrypt.")
            return
        if not mainFolder['path']:
            messagebox.showerror("Missing main folder", "Please select the main folder before encrypting.")
            return
        try:
            encryptAndSplitFile(selectedFile['path'], int(countSpin.get()), mainFolder['path'], cur, con, progressCallback=updateProgress)
            progressVar.set(100)
            progressLabel.config(text="100.00%")
            messagebox.showinfo("Success", "Encryption complete.")
            infoText.config(text="Encryption complete.")
            refreshHomeText(cur, homeBodyWidget, mainFolder['path'])
            refreshDecryptText(cur, decryptBodyWidget, mainFolder['path'])
        except Exception as exc:
            messagebox.showerror("Error", str(exc))

    controlRow = ttk.Frame(frame)
    controlRow.pack(anchor="nw", padx=20, pady=(12, 0))

    countLabel = ttk.Label(controlRow, text="Splits:", font=(None, 12))
    countLabel.pack(side="left")

    countSpin = ttk.Spinbox(controlRow, from_=1, to=999, width=8)
    countSpin.set(1)
    countSpin.pack(side="left", padx=(10, 0))

    countText = ttk.Label(controlRow, text="Number of encrypted parts", bootstyle="light", font=(None, 14))
    countText.pack(side="left", padx=(12, 0))

    actionRow = ttk.Frame(frame)
    actionRow.pack(fill="x", pady=20)

    primaryButton = ttk.Button(actionRow, text="Encrypt & Split", bootstyle="primary", command=runEncrypt)
    primaryButton.pack(pady=10)
    primaryButton.configure(width=22)

    # Progress bar moved below all controls so it remains visible during long operations
    progressRow = ttk.Frame(frame)
    progressRow.pack(fill="x", padx=20, pady=(10, 0))

    progressBar = ttk.Progressbar(progressRow, bootstyle="info", maximum=100, variable=progressVar)
    progressBar.pack(side="left", fill="x", expand=True)

    progressLabel = ttk.Label(progressRow, text="0.00%", bootstyle="light", font=(None, 14))
    progressLabel.pack(side="left", padx=(12, 0))

    return frame


def makeDecryptTab(notebook, mainFolder, cur):
    frame = ttk.Frame(notebook)
    titleLabel = ttk.Label(frame, text="Decrypt / Merge", font=(None, 24, "bold"))
    titleLabel.pack(anchor="nw", padx=20, pady=(20, 5))

    placeholder = ttk.Label(frame, text="Here, you can decrypt files you previously encrypted. Select the parent directory with all the encrypted files to begin.", bootstyle="light", font=(None, 14))
    placeholder.pack(anchor="nw", padx=20, pady=(0, 20))

    separator = ttk.Separator(frame, orient="horizontal")
    separator.pack(fill="x", padx=20, pady=(0, 20))

    body = ScrolledText(frame, autohide=True, height=16)
    body.pack(fill="both", expand=True, padx=20, pady=(0, 20))
    global decryptBodyWidget
    decryptBodyWidget = body
    refreshDecryptText(cur, body, mainFolder['path'])

    buttonRow = ttk.Frame(frame)
    buttonRow.pack(anchor="nw", padx=20)

    selectedFolder = {'path': None}

    def chooseFolder():
        folderPath = askForDir()
        if folderPath:
            selectedFolder['path'] = folderPath
            infoText.config(text=f"Target folder: {folderPath}")

    infoButton = ttk.Button(buttonRow, text="Select Target Folder", bootstyle="info", command=chooseFolder)
    infoButton.pack(side="left")

    infoText = ttk.Label(buttonRow, text="No folder selected.", bootstyle="light", font=(None, 14))
    infoText.pack(side="left", padx=(12, 0))

    entryId = tk.IntVar(value=1)

    def runDecrypt():
        if not selectedFolder['path']:
            messagebox.showerror("Missing folder", "Please select the folder containing encrypted parts.")
            return
        if not mainFolder['path']:
            messagebox.showerror("Missing main folder", "Please select the main folder before decrypting.")
            return
        try:
            outPath = decryptAndMergeFiles(selectedFolder['path'], int(entryId.get()), cur)
            if outPath:
                messagebox.showinfo("Success", f"Decryption complete. Output: {outPath}")
                infoText.config(text=f"Decryption complete: {os.path.basename(outPath)}")
            else:
                messagebox.showinfo("Success", "Decryption complete.")
                infoText.config(text="Decryption complete.")
        except Exception as exc:
            # show exception type and message for clarity
            try:
                msg = f"{type(exc).__name__}: {exc}"
            except Exception:
                msg = str(exc)
            print("Decryption error:", msg)
            messagebox.showerror("Decryption error", msg)

    selectRow = ttk.Frame(frame)
    selectRow.pack(anchor="nw", padx=20, pady=(10, 0), fill="x")

    ttk.Label(selectRow, text="Entry ID:", font=(None, 12)).pack(side="left")
    entrySpin = ttk.Spinbox(selectRow, from_=1, to=9999, textvariable=entryId, width=8)
    entrySpin.pack(side="left", padx=(6, 0))

    actionRow = ttk.Frame(frame)
    actionRow.pack(fill="x", pady=20)

    primaryButton = ttk.Button(actionRow, text="Decrypt & Merge", bootstyle="primary", command=runDecrypt)
    primaryButton.pack(pady=10)
    primaryButton.configure(width=22)

    return frame


def main():
    app = ttk.Window(themename="darkly", title="MyEyesOnly")
    app.state('zoomed')

    con = None

    def onClose():
        nonlocal con
        if con is not None:
            try:
                con.close()
            except Exception:
                pass
        app.destroy()

    app.protocol("WM_DELETE_WINDOW", onClose)

    mainFolder = {'path': None}
    mainFolder['path'] = askForDir()
    if not mainFolder['path']:
        messagebox.showwarning("Startup cancelled", "Main folder selection is required to run this GUI.")
        return

    notebook = ttk.Notebook(app, bootstyle="dark")
    notebook.pack(fill="both", expand=True)

    cur, con = tableConnection(mainFolder['path'])
    if not cur:
        messagebox.showerror("Database error", "Unable to open the database in the selected main folder.")
        return

    notebook.add(makeHomeTab(notebook, cur, con, mainFolder['path']), text="Home")
    notebook.add(makeEncryptTab(notebook, mainFolder, cur, con), text="Encrypt / Split")
    notebook.add(makeDecryptTab(notebook, mainFolder, cur), text="Decrypt / Merge")

    app.mainloop()


if __name__ == "__main__":
    main()

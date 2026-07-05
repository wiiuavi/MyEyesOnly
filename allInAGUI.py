import math
import os
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.dialogs import Messagebox
from ttkbootstrap.widgets.scrolled import ScrolledText
from basicallyEverythingRedone import (
    askForDir,
    askForFile,
    decryptAndMergeFiles,
    encryptAndSplitFile,
    tableConnection,
)


def setup_gui(master, main_folder, cur, con):
    selected_file_path = ""
    selected_file_size = 0
    target_decrypt_folder = ""

    def style_scrolled_text(widget):
        widget.configure(bootstyle='darkly')
        widget.text.configure(
            background=master.style.colors.bg,
            foreground=master.style.colors.fg,
            insertbackground=master.style.colors.fg,
            selectbackground=master.style.colors.secondary,
            selectforeground=master.style.colors.fg,
            relief='flat',
            borderwidth=0,
        )

    def create_header(parent, title, subtitle):
        header = ttk.Frame(parent, bootstyle='darkly')
        header.pack(fill=X, pady=(0, 10), padx=8)
        ttk.Label(
            header,
            text=title,
            font=("Segoe UI", 20, "bold"),
            bootstyle='inverse-darkly',
        ).pack(anchor=W)
        ttk.Label(
            header,
            text=subtitle,
            bootstyle='inverse-darkly',
        ).pack(anchor=W, pady=(4, 0))

    def create_info_box(parent, text):
        info = ttk.Label(
            parent,
            text=text,
            wraplength=900,
            justify=LEFT,
            bootstyle='inverse-darkly',
            padding=(10, 10),
        )
        info.pack(fill=X, pady=(0, 10), padx=8)
        return info

    notebook = ttk.Notebook(master, bootstyle='darkly')
    notebook.pack(fill=BOTH, expand=YES, padx=10, pady=10)

    tab_home = ttk.Frame(notebook, bootstyle='darkly')
    tab_encrypt = ttk.Frame(notebook, bootstyle='darkly')
    tab_decrypt = ttk.Frame(notebook, bootstyle='darkly')
    tab_review = ttk.Frame(notebook, bootstyle='darkly')

    notebook.add(tab_home, text='Home')
    notebook.add(tab_encrypt, text='Encrypt / Split')
    notebook.add(tab_decrypt, text='Decrypt / Merge')
    notebook.add(tab_review, text='Review')

    create_header(tab_home, 'MyEyesOnly Dashboard', 'Monitor your encrypted files and recent database activity.')
    create_info_box(tab_home, 'Welcome to your secure dashboard. The latest database entries and summary stats appear here in real time.')

    home_content = ttk.Frame(tab_home, bootstyle='darkly')
    home_content.pack(fill=BOTH, expand=YES, padx=8, pady=6)

    recent_frame = ttk.Labelframe(home_content, text='Recent Database Entries', padding=12, bootstyle='darkly')
    recent_frame.pack(side=LEFT, fill=BOTH, expand=YES, padx=(0, 6), pady=0)

    recent_text = ScrolledText(recent_frame, height=12, autohide=True, bootstyle='darkly')
    recent_text.pack(fill=BOTH, expand=YES)
    style_scrolled_text(recent_text)

    summary_frame = ttk.Labelframe(home_content, text='Encryption Summary', padding=12, bootstyle='darkly')
    summary_frame.pack(side=RIGHT, fill=BOTH, expand=YES, padx=(6, 0), pady=0)

    total_label = ttk.Label(
        summary_frame,
        text='Total Files Encrypted:\n0',
        font=("Segoe UI", 18, "bold"),
        justify=CENTER,
        anchor=CENTER,
        bootstyle='inverse-darkly',
    )
    total_label.pack(expand=YES, fill=BOTH)

    create_header(tab_encrypt, 'Encrypt & Split', 'Select a file, choose how many parts, and run the CLI encryption workflow.')
    create_info_box(tab_encrypt, 'Select the source file to encrypt and split. This UI uses the same helper functions as the CLI tool.')

    encrypt_panel = ttk.Labelframe(tab_encrypt, text='Encrypt Settings', padding=12, bootstyle='darkly')
    encrypt_panel.pack(fill=X, pady=6, padx=8)

    split_var = ttk.StringVar(value='1')
    status_label = ttk.Label(tab_encrypt, text='No file selected.', bootstyle='inverse-darkly')
    start_button = ttk.Button(tab_encrypt, text='Start Encryption', bootstyle=(SUCCESS, OUTLINE), state=DISABLED)

    def update_encrypt_status(*args):
        if not selected_file_path:
            return
        size_mb = selected_file_size / (1024 * 1024)
        try:
            splits = int(split_var.get())
            if splits < 1:
                raise ValueError
            max_size = math.ceil(selected_file_size / splits)
            status_label.config(
                text=(
                    f'File: {os.path.basename(selected_file_path)}\n'
                    f'Total Size: {size_mb:.2f} MB ({selected_file_size} bytes)\n'
                    f'Splits: {splits}\n'
                    f'Max part size: {max_size / (1024 * 1024):.2f} MB'
                )
            )
        except ValueError:
            status_label.config(text='Invalid split count. Enter a positive integer.')

    split_var.trace_add('write', update_encrypt_status)

    def choose_file():
        nonlocal selected_file_path, selected_file_size
        file_path = askForFile()
        if file_path and os.path.exists(file_path):
            selected_file_path = file_path
            selected_file_size = os.path.getsize(file_path)
            start_button.config(state=NORMAL)
            update_encrypt_status()

    def run_encrypt():
        if not selected_file_path:
            Messagebox.show_error('Please select a file first.', 'Missing File')
            return
        try:
            splits = int(split_var.get())
            if splits < 1:
                raise ValueError
            encryptAndSplitFile(selected_file_path, splits, main_folder, cur, con)
            Messagebox.show_info('Encryption complete.', 'Success')
            refresh_db()
        except ValueError:
            Messagebox.show_error('Enter a valid split count.', 'Invalid Input')
        except Exception as exc:
            Messagebox.show_error(str(exc), 'Error')

    ttk.Button(encrypt_panel, text='Select File to Encrypt', command=choose_file, bootstyle=(INFO, OUTLINE)).pack(side=LEFT, padx=(0, 10))
    ttk.Label(encrypt_panel, text='Number of splits:', bootstyle='inverse-darkly').pack(side=LEFT, padx=(10, 5))
    ttk.Spinbox(encrypt_panel, from_=1, to=1000, textvariable=split_var, width=6, bootstyle='darkly').pack(side=LEFT)

    stats_frame = ttk.Labelframe(tab_encrypt, text='File Statistics', padding=12, bootstyle='darkly')
    stats_frame.pack(fill=X, pady=6, padx=8)
    status_label.pack(in_=stats_frame, anchor=W)

    start_button.config(command=run_encrypt)
    start_button.pack(pady=10)

    create_header(tab_decrypt, 'Decrypt & Merge', 'Pick the folder with parts and provide the database entry ID.')
    create_info_box(tab_decrypt, 'Use the CLI folder picker and database entry to reconstruct the original file.')

    decrypt_panel = ttk.Labelframe(tab_decrypt, text='Decrypt Settings', padding=12, bootstyle='darkly')
    decrypt_panel.pack(fill=X, pady=6, padx=8)

    decrypt_folder_label = ttk.Label(decrypt_panel, text='No folder selected.', bootstyle='inverse-darkly')

    def choose_decrypt_folder():
        nonlocal target_decrypt_folder
        folder = askForDir()
        if folder:
            target_decrypt_folder = folder
            decrypt_folder_label.config(text=folder)

    ttk.Button(decrypt_panel, text='Select Folder with Parts', command=choose_decrypt_folder, bootstyle=(INFO, OUTLINE)).pack(side=LEFT, padx=(0, 10))
    decrypt_folder_label.pack(side=LEFT)

    entry_frame = ttk.Frame(tab_decrypt, bootstyle='darkly')
    entry_frame.pack(fill=X, pady=10, padx=8)
    ttk.Label(entry_frame, text='Database Entry ID:', bootstyle='inverse-darkly').pack(side=LEFT, padx=(0, 5))
    decrypt_id_var = ttk.StringVar()
    ttk.Entry(entry_frame, textvariable=decrypt_id_var, width=12, bootstyle='darkly').pack(side=LEFT)

    preview_frame = ttk.Labelframe(tab_decrypt, text='Recent Database Entries', padding=12, bootstyle='darkly')
    preview_frame.pack(fill=BOTH, expand=YES, pady=6, padx=8)
    decrypt_preview = ScrolledText(preview_frame, height=6, autohide=True, bootstyle='darkly')
    decrypt_preview.pack(fill=BOTH, expand=YES)
    style_scrolled_text(decrypt_preview)

    def run_decrypt():
        if not target_decrypt_folder:
            Messagebox.show_error('Please choose the folder containing parts first.', 'Missing Folder')
            return
        try:
            entry_id = int(decrypt_id_var.get())
            decryptAndMergeFiles(target_decrypt_folder, entry_id, cur)
            Messagebox.show_info('Decryption complete.', 'Success')
        except ValueError:
            Messagebox.show_error('Enter a valid database ID.', 'Invalid Input')
        except Exception as exc:
            Messagebox.show_error(str(exc), 'Error')

    ttk.Button(tab_decrypt, text='Start Decryption & Merge', command=run_decrypt, bootstyle=(SUCCESS, OUTLINE)).pack(pady=10)

    create_header(tab_review, 'Review Database', 'Inspect every stored encryption record.')
    create_info_box(tab_review, 'This tab displays all records from the SQLite keymap database.')

    review_text = ScrolledText(tab_review, height=16, autohide=True, bootstyle='darkly')
    review_text.pack(fill=BOTH, expand=YES, pady=6, padx=8)
    style_scrolled_text(review_text)

    def refresh_db():
        for widget in (recent_text, decrypt_preview, review_text):
            widget.text.configure(state=NORMAL)
            widget.text.delete('1.0', END)

        cur.execute('SELECT CreateID, DateOfCreation, FileName, Status FROM keymap ORDER BY CreateID DESC LIMIT 5')
        recent_records = cur.fetchall()
        if recent_records:
            for rec in recent_records:
                recent_text.text.insert(END, f'ID: {rec[0]} | Date: {rec[1]} | File: {rec[2]} | Status: {rec[3]}\n')
                decrypt_preview.text.insert(END, f'ID: {rec[0]} | Date: {rec[1]} | File: {rec[2]}\n')
        else:
            recent_text.text.insert(END, 'No records found.')
            decrypt_preview.text.insert(END, 'No database entries exist yet.')

        cur.execute('SELECT CreateID, DateOfCreation, FileName, Status FROM keymap')
        all_records = cur.fetchall()
        if all_records:
            for rec in all_records:
                review_text.text.insert(END, f'ID: {rec[0]} | Date: {rec[1]} | File: {rec[2]} | Status: {rec[3]}\n')
        else:
            review_text.text.insert(END, 'No records found.')

        total_label.config(text=f'Total Files Encrypted:\n{len(all_records)}')
        for widget in (recent_text, decrypt_preview, review_text):
            widget.text.configure(state=DISABLED)

    refresh_db()
    return master


if __name__ == '__main__':
    main_folder = askForDir()
    if not main_folder:
        print('Initialization failed: No folder selected.')
        exit()

    cur, con = tableConnection(main_folder)
    app = ttk.Window(title='MyEyesOnly Dashboard', themename='darkly', size=(980, 700))
    app.minsize(900, 650)
    app.configure(bg=app.style.colors.bg)

    style = app.style
    style.theme_use('darkly')
    style.configure('TNotebook', background=style.colors.bg, foreground=style.colors.fg, bordercolor=style.colors.bg, lightcolor=style.colors.bg, darklycolor=style.colors.bg)
    style.configure('TNotebook.Tab', background=style.colors.bg, foreground=style.colors.fg, padding=(10, 8))
    style.map(
        'TNotebook.Tab',
        background=[('selected', style.colors.secondary), ('active', style.colors.primary), ('!selected', style.colors.bg)],
        foreground=[('selected', style.colors.fg), ('!selected', style.colors.fg)],
    )
    style.configure('TFrame', background=style.colors.bg)
    style.configure('TLabelframe', background=style.colors.bg, foreground=style.colors.fg, bordercolor=style.colors.secondary)
    style.configure('TLabelframe.Label', background=style.colors.bg, foreground=style.colors.fg)
    style.configure('TLabel', background=style.colors.bg, foreground=style.colors.fg)
    style.configure('TEntry', fieldbackground=style.colors.bg, background=style.colors.bg, foreground=style.colors.fg)
    style.configure('TSpinbox', fieldbackground=style.colors.bg, background=style.colors.bg, foreground=style.colors.fg)
    style.configure('TButton', background=style.colors.secondary, foreground=style.colors.fg)

    setup_gui(app, main_folder, cur, con)

    def on_closing():
        con.close()
        app.destroy()

    app.protocol('WM_DELETE_WINDOW', on_closing)
    app.mainloop()

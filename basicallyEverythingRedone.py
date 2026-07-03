import secrets
import sqlite3
import os
import datetime
import tkinter as tk
from tkinter import filedialog
import ttkbootstrap as ttk
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms

def generateKeystreamCryptography(keySeedBytes, offset, length):
    fixedNonce = b'\x00' * 16
    cipher = Cipher(algorithms.ChaCha20(keySeedBytes, fixedNonce), mode=None)
    encryptor = cipher.encryptor()
    if offset > 0:
        _ = encryptor.update(b'\x00' * offset)
    dummyBytes = b'\x00' * length
    return encryptor.update(dummyBytes)


def encryptionToggleMessage(messageBytes, keySeedBytes, offset=0):
    messageLength = len(messageBytes)
    keystream = generateKeystreamCryptography(keySeedBytes, offset, messageLength)
    encryptedBytes = bytearray(b ^ k for b, k in zip(messageBytes, keystream))
    
    return bytes(encryptedBytes)


#dbstuff

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
        filetypes=[("All Files", "*.*")]
    )
    if filePath:
        print(f"User selected: {filePath}")
        return filePath
    else:
        print("User cancelled the operation.")
        return None
    
def tableConnection():
    mainFolder = askForDir()
    if mainFolder is None:
        return None, None
        
    dbPath = os.path.join(mainFolder, "importantKeysDontDel.db")
    con = sqlite3.connect(dbPath)
    cur = con.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS keymap (
            CreateID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            DateOfCreation TEXT NOT NULL,
            FileName TEXT NOT NULL,
            Key BLOB NOT NULL,
            Status INTEGER NOT NULL
        )
    ''')
    con.commit()
    return cur, con



def processAndEncryptFile(filePath, cur, con):
    if not filePath or not os.path.exists(filePath):
        return
        
    uniqueKeySeed = secrets.token_bytes(32)
    
    with open(filePath, 'rb') as f:
        fileBytes = f.read()
        
    encryptedData = encryptionToggleMessage(fileBytes, uniqueKeySeed)
    
    outputPath = os.path.splitext(filePath)[0]
    with open(outputPath, 'wb') as f:
        f.write(encryptedData)
        
    fileNameOnly = os.path.basename(filePath)
    creationDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    activeStatus = 1
    
    cur.execute('''
        INSERT INTO keymap (DateOfCreation, FileName, Key, Status)
        VALUES (?, ?, ?, ?)
    ''', (creationDate, fileNameOnly, uniqueKeySeed, activeStatus))
    con.commit()
    
    print(f"Successfully processed and encrypted: {fileNameOnly}")


#test

def test():
    message = "yooooooo wsg gng we got the encryption thing goin WWWWW"
    messageBytes = message.encode("utf-8")
    
    mySecretKeySeed = secrets.token_bytes(32)
    
    print("Original message text: " + message)
    
    cipherBytes = encryptionToggleMessage(messageBytes, mySecretKeySeed)
    print("Ciphertext output bytes: ", cipherBytes)
    
    decryptedBytes = encryptionToggleMessage(cipherBytes, mySecretKeySeed)
    print("Decrypted back into text: " + decryptedBytes.decode("utf-8"))

if __name__ == "__main__":
    test()
    
    # cur, con = tableConnection()
    # if (cur is not None) and (con is not None):
    #     targetFile = askForFile()
    #     processAndEncryptFile(targetFile, cur, con)
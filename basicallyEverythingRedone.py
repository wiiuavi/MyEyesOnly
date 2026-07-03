import os
import math
import secrets
import sqlite3
import datetime
import tkinter as tk
from tkinter import filedialog
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

def askForDir():
    root = tk.Tk()
    root.withdraw()
    selectedFolder = filedialog.askdirectory(title="Select Folder for Outputs and DB")
    if selectedFolder:
        print(f"Directory set: {selectedFolder}")
        return selectedFolder
    return None

def askForFile():
    root = tk.Tk()
    root.withdraw()
    filePath = filedialog.askopenfilename(
        title="Select a File to Encrypt",
        filetypes=[("All Files", "*.*")]
    )
    if filePath:
        print(f"Target selected: {filePath}")
        return filePath
    return None
    
def tableConnection(mainFolder):
    if not mainFolder:
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

def encryptAndSplitFile(filePath, numSplits, mainFolder, cur, con):
    if not filePath or not os.path.exists(filePath):
        return
        
    totalSize = os.path.getsize(filePath)
    if totalSize == 0:
        print("File is completely empty.")
        return

    uniqueKeySeed = secrets.token_bytes(32)
    targetSplitSize = math.ceil(totalSize / numSplits)
    chunkSize = 1024 * 1024 * 5 

    fileNameOnly = os.path.basename(filePath)
    baseOutputName = os.path.splitext(fileNameOnly)[0]
    
    overallOffset = 0
    currentSplitIndex = 1
    currentSplitBytes = 0
    
    currentOutPath = os.path.join(mainFolder, f"{baseOutputName}_part{currentSplitIndex}")
    outFile = open(currentOutPath, 'wb')

    with open(filePath, 'rb') as inFile:
        while True:
            chunk = inFile.read(chunkSize)
            if not chunk:
                break
                
            encryptedChunk = encryptionToggleMessage(chunk, uniqueKeySeed, overallOffset)
            overallOffset += len(chunk)
            
            chunkOffset = 0
            while chunkOffset < len(encryptedChunk):
                bytesRemainingInSplit = targetSplitSize - currentSplitBytes
                bytesToWrite = min(len(encryptedChunk) - chunkOffset, bytesRemainingInSplit)
                
                outFile.write(encryptedChunk[chunkOffset : chunkOffset + bytesToWrite])
                currentSplitBytes += bytesToWrite
                chunkOffset += bytesToWrite
                
                if currentSplitBytes >= targetSplitSize and currentSplitIndex < numSplits:
                    outFile.close()
                    currentSplitIndex += 1
                    currentSplitBytes = 0
                    currentOutPath = os.path.join(mainFolder, f"{baseOutputName}_part{currentSplitIndex}")
                    outFile = open(currentOutPath, 'wb')
            
            progress = (overallOffset / totalSize) * 100
            print(f"\rEncrypting... {progress:.2f}% complete", end="", flush=True)

    outFile.close()
    print(f"\nSuccessfully processed, encrypted, and split into {numSplits} files.")

    creationDate = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    activeStatus = 1
    
    cur.execute('''
        INSERT INTO keymap (DateOfCreation, FileName, Key, Status)
        VALUES (?, ?, ?, ?)
    ''', (creationDate, fileNameOnly, uniqueKeySeed, activeStatus))
    con.commit()

def runMockCLI():
    print("### CLI Initialization ###")
    mainFolder = askForDir()
    if not mainFolder:
        print("Initialization failed: No folder selected.")
        return
        
    cur, con = tableConnection(mainFolder)
    if not cur:
        return

    while True:
        print("\n### Main Menu ###")
        print("1. Encrypt and Split a File")
        print("2. Review Database Entries")
        print("3. Decrypt files")
        print("4. Exit")
        
        userInput = input("Enter choice (1-4): ")
        
        if userInput == "1":
            targetFile = askForFile()
            if not targetFile:
                continue
            try:
                splitCount = int(input("How many output files to split into? "))
                if splitCount < 1:
                    print("Must split into at least 1 file.")
                    continue
                encryptAndSplitFile(targetFile, splitCount, mainFolder, cur, con)
            except ValueError:
                print("Error: Please enter a valid integer.")
                
        elif userInput == "2":
            cur.execute("SELECT CreateID, DateOfCreation, FileName, Status FROM keymap")
            records = cur.fetchall()
            print("\n### Current Database Records ###")
            for record in records:
                print(f"ID: {record[0]} | Date: {record[1]} | File: {record[2]} | Status: {record[3]}")
            if not records:
                print("No records found.")
        
        elif userInput == "3":
            pass
                
        elif userInput == "4":
            print("Terminating application...")
            con.close()
            break
            
        else:
            print("Invalid selection.")

if __name__ == "__main__":
    runMockCLI()
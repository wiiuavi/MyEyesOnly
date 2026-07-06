# MyEyesOnly
yooo its a demo vid


https://github.com/user-attachments/assets/b5fb1ce6-5574-478a-a677-b5ba5f4fdc25




This program will let you encrypt your files and store their keys in a database! Ensure only your eyes see your files! (note, while this won't stop interceptors accessing files you send over a network, this won't let them access your data)

# Installation
This program has only been tested on windows. Major bugs may be seen on other platforms
Check the releases page for an executable file!(windows only)
Or alternatively, clone the repo, create a virtual enviroment (optional, but recomended), and run:
pip install -r requirements.txt

then run GUIattempt2.py

# Usage
upon running, you will be prompted to select a folder. make a clean empty folder  where you want, This will store your database and keys, as well as the output folder, which holds encryption/decryption results
The home tab will let you review the db and delete unneeded entries
The encrypt/split tab will let you select a file to encrypt, choose how many files to split the result into, and proceed.
The decrypt/merge tab will prompt you to select a folder containing all encrypted files, then let you choose the respective encrypt entry in from the db.

# Context
Made this after my experience trying terrabox and seeing other less known cloud solutions. Terrabox promised 1TB free storage, however this meant constantly watching ads every day, unlocking your storage bit by bit, and no Zerokey encryption (where only you hold the key to access your data, they do too)
While i strongly recomend you DON'T use these services, as there is no garuntee they just refuse to hand over data you store and its inconvinience, if you must, this program will make sure noone else can understand your data.
The split functionality also inspired by Terrabox, which while having upto 1TB, only lets you store 4GB files max, (and they had a limit on how many files you could store, which didn't really help either).

# notes
Ai usage; I used AI partially to help in the GUI (stopping script on window close logic, maintaining themes across tabs) and in the split/merge logic (most of it was still me)
The output folder in the repo was some tests I did, you could try decrypt them yourself!
TODO:
    add images, GUI is dry
    add tooltips (usage and why)


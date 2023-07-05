import os
import subprocess
import sqlite3
from pathlib import Path
from tqdm import tqdm

database_path = r'C:\Users\nichel\Music\FavoriteMusic\AllowedSongs.db'

music_path = r'C:\Users\nichel\Music\FavoriteMusic'

# Connect or create database
con = sqlite3.connect(database_path)

# Create table if it doesn't exist
c = con.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS Songs
                (SongID INTEGER PRIMARY KEY AUTOINCREMENT, Path TEXT, Deleted INTEGER)''')
con.commit()

# Get list of m4a files in folder
files = [file for file in os.listdir(music_path) if file.endswith('.m4a')]

# Create progress bar
pbar = tqdm(total=len(files), desc='Files', unit='files', position=2)

# Iterate through files
for file in files:

    # Create full path to file
    file = str(Path(music_path, file))

    # Check if the file is marked for deletion
    delfile = c.execute('SELECT Deleted FROM Songs WHERE Path == ?', (file,)).fetchall()
    try:
        # Database returns a list of tuples.
        # This means that delfile[0] is a tuple
        # and delfile[0][0] is the first element of the tuple
        # which is the value of the Deleted column
        if delfile[0][0] == 1:
            os.remove(file)
            pbar.total = pbar.total - 1
            pbar.refresh()
            continue

    # If the file is not in the database
    # delfile is empty and an IndexError is raised
    except IndexError:
        pass

    # Check if the file is in the database
    ID = c.execute('SELECT SongID FROM Songs WHERE Path == ?', (file,)).fetchall()
    # if the file in not in the database
    # no tuples will be returned and ID will be empty
    if len(ID) == 0:
        # Play file
        cmd = ['ffplay', file]
        subprocess.Popen(cmd).wait()

        # Display the progress bar
        pbar.refresh()

        # Ask if file should be deleted
        FileDelete = ''
        while FileDelete.casefold() != 'y' and FileDelete.casefold() != 'n':
            FileDelete = input("Delete file? (y/n): ")

        if FileDelete.casefold() == 'y':
            # Add file to database and mark deleted
            c.execute('INSERT INTO Songs (Path) VALUES (?)', (file,))
            c.execute('UPDATE Songs SET Deleted = 1 WHERE Path == ?', (file,))
            con.commit()

            # Delete file and update progress bar
            # with the new total
            os.remove(file)
            pbar.total = pbar.total - 1
            pbar.refresh()
        else:
            # Add file to database and mark not deleted
            c.execute('INSERT INTO Songs (Path) VALUES (?)', (file,))
            c.execute('UPDATE Songs SET Deleted = 0 WHERE Path == ?', (file,))
            con.commit()

            # Update progress bar
            pbar.update(1)

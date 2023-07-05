from os import remove, mkdir, listdir
from subprocess import Run
import sqlite3
from pathlib import Path
from tqdm import tqdm
from shutil import copy2

database_path = r'C:\Users\nichel\Music\FavoriteMusic\AllowedSongs.db'

music_path = r'C:\Users\nichel\Music\FavoriteMusic'

output_path = r'C:\Users\nichel\Music\AllowedMusic'

try:
    mkdir(output_path)
except FileExistsError:
    pass

# Connect or create database
con = sqlite3.connect(database_path)

# Create table if it doesn't exist
c = con.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS Songs
                (SongID INTEGER PRIMARY KEY AUTOINCREMENT, Path TEXT, Allowed INTEGER)''')
con.commit()

# Get list of m4a files in folder
files = [file for file in listdir(music_path) if file.endswith('.m4a')]

# Create progress bar
pbar = tqdm(total=len(files), desc='Files', unit='files', position=2)

# Iterate through files
for file in files:
    full_path = str(Path(music_path, file))
    allowed = c.execute('SELECT Allowed FROM Songs WHERE Path == ?', (full_path,)).fetchall()

    # Check if the file is in the database and marked as allowed
    try:
        # Database returns a list of tuples.
        # This means that allowed[0] is the first tuple in the list
        # and allowed[0][0] is the first element of the first tuple
        # which is the value of the allowed column

        # If the file is marked as allowed
        if allowed[0][0] == 1:
            if not Path(output_path, file).exists():
                copy2(full_path, str(Path(output_path, file)))

        # If the file is marked as not allowed
        elif allowed[0][0] == 0:
            if Path(output_path, file).exists():
                remove(str(Path(output_path, file)))

    # If the file is not in the database
    # moved is empty and an IndexError is raised
    except IndexError:
        pass

    # Play file
    cmd = ['ffplay', full_path]
    Run(cmd)

    # Ask if the file should be allowed
    allowed_input = ''
    while allowed_input.casefold() not in ['y', 'n']:
        allowed_input = input('Allow file? (y/n): ').casefold()
from os import remove, mkdir, listdir
from subprocess import run
import sqlite3
from pathlib import Path
from tqdm import tqdm
from shutil import copy2

# Check if ffmpeg is installed either in the system or in the same folder as this script
try:
    run(['ffplay', '-version'])
except FileNotFoundError:
    try:
        run([str(Path(Path(__file__).parent, 'ffplay.exe')), '-version'])
    except FileNotFoundError:
        print('ffmpeg not found. Please install it and add it to your PATH variable or the folder this script is in.')
        print('You can download it here: https://ffmpeg.org/download.html. Press enter to exit...')
        exit()


def StartupCheck(full_path, allowed, output_path, file):
    """
    Checks if the file is in the database and marked as allowed.
    If the file is marked as allowed and does not exist in the output path, it is copied to the output path.
    If the file is marked as not allowed and exists in the output path, it is removed from the output path.
    Returns True if the file was copied or removed, False otherwise.
    """
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
        return True
    # If the file is not in the database
    # allowed will be empty and an IndexError is raised
    except IndexError:
        pass
    return False


# Ask for database path. If no path is given, use the default path
database_path = input('Database path: ') or str(Path(Path(__file__).parent, 'MusicTester.db'))

# Ask for music folder path. If no path is given, use the default path
music_path = input('Music folder path: ') or str(Path(Path(__file__).parent, 'Music'))

# Ask for output folder path. If no path is given, use the default path
output_path = input('Output folder path: ') or str(Path(Path(__file__).parent, 'Output'))

try:
    mkdir(output_path)
except FileExistsError:
    pass

# Connect or create database
con = sqlite3.connect(database_path)

# Create table if it doesn't exist and make Path case insensitive
c = con.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS Songs
                (SongID INTEGER PRIMARY KEY AUTOINCREMENT, Path TEXT COLLATE NOCASE, Allowed INTEGER)''')
con.commit()

# Get list of m4a files in folder
try:
    files = [file for file in listdir(music_path) if file.endswith('.m4a')]
except FileNotFoundError:
    print('Music folder not found. Please create a folder called Music in the same folder as this script and put your music files in it. Press enter to exit...')
    exit()

if len(files) == 0:
    print('No music files found. Please put your music files in the Music folder. Press enter to exit...')
    exit()

# Create progress bar
pbar = tqdm(total=len(files), desc='Files', unit='files', position=2)

# Iterate through files
for file in files:
    full_path = str(Path(music_path, file))
    allowed = c.execute('SELECT Allowed FROM Songs WHERE Path == ?', (full_path,)).fetchall()

    pbar.update(1)

    # Use StartupCheck to check if any any files need to be copied to or deleted in the output folder
    if StartupCheck(full_path, allowed, output_path, file):
        continue

    # Play the audio file
    cmd = ['ffplay', full_path]
    run(cmd)

    # Ask if the file should be allowed
    allowed_input = ''
    while allowed_input.casefold() not in ['y', 'n']:
        pbar.refresh()
        allowed_input = input('\nAllow file? (y/n): ').casefold()

    # Add file to database
    c.execute('INSERT INTO Songs (Path, Allowed) VALUES (?, ?)', (full_path, 1 if allowed_input == 'y' else 0))
    con.commit()

    # Copy file to output folder if allowed
    if allowed_input == 'y':
        copy2(full_path, str(Path(output_path, file)))

import os
import subprocess
import sqlite3

con = sqlite3.connect(r'C:\Users\nickl\Music\Distance Music\AllowedSongs.db')
files = os.listdir(r'C:\Users\nickl\Music\Distance Music')
c = con.cursor()
for file in files:
    file = 'C:\\Users\\nickl\\Music\\Distance Music\\' + file
    
    ID = c.execute('SELECT SongID FROM Songs WHERE Path == ?', (file,)).fetchall()
    if len(ID) == 0:
        cmd = ['ffplay',file]
        subprocess.Popen(cmd).wait()
        FileDelete = input("Delete file?")
        if FileDelete == 'y':
            os.remove(file)
        else:
            c.execute('INSERT INTO Songs (Path) VALUES (?)', (file,))
            con.commit()
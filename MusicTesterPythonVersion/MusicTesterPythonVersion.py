import os
import subprocess
import sqlite3

con = sqlite3.connect(r'C:\Users\nickl\Music\Distance Music\AllowedSongs.db')
files = os.listdir(r'C:\Users\nickl\Music\Distance Music')
c = con.cursor()
fd = int(0)
fl = int(0)
fl = os.listdir(r'C:\Users\nickl\Music\Distance Music')
fl = len(fl)
for file in files:
    file = 'C:\\Users\\nickl\\Music\\Distance Music\\' + file
    fd = fd + 1
    
    
    ID = c.execute('SELECT SongID FROM Songs WHERE Path == ?', (file,)).fetchall()
    if len(ID) == 0:
        cmd = ['ffplay',file]
        subprocess.Popen(cmd).wait()
        fdiv = fd / fl 
        fmul = fdiv * 100
        fper = round(fmul,2)
        print(f'File {fd} out of {fl} files, or {fper}% done')
        FileDelete = input("Delete file?")
        if FileDelete == 'y':
            os.remove(file)
            fl = os.listdir(r'C:\Users\nickl\Music\Distance Music')
            fl = len(fl)
            fd = fd - 1
        else:
            c.execute('INSERT INTO Songs (Path) VALUES (?)', (file,))
            con.commit()
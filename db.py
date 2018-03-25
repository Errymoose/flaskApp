import sqlite3
from hashlib import sha256
import traceback
import threading

con2 = sqlite3.connect('pokemon2.db')
cur2= con2.cursor()
cur2.execute('begin')


cur2.execute('select * from encounters')
encounters = cur2.fetchall()

print(len(encounters))
for e in encounters:
    lock = threading.Lock()
    lock.acquire()
    con = sqlite3.connect('pokemon.db')
    cur = con.cursor()
    cur.execute('begin')
    m = sha256()
    print(e)
    m.update('{0}{1}{2}{3}{4}{5}{6}'.format(e[0], e[1], e[2],e[3], e[4], e[5], e[6]).encode())
    print(m.hexdigest())
    try:
        cur.execute('insert into encounters values(?, ?, ?, ?, ?, ?, ?, ?)', (e[0], e[1], e[2],e[3], e[4], e[5], e[6], m.hexdigest()))
        con.commit()

    except sqlite3.IntegrityError:
        print(traceback.format_exc())
        pass
    lock.release()


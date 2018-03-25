#!/usr/bin/python3

import discord
import re
import sqlite3
import threading

import logging
import logging.handlers
import sys
import os
from hashlib import sha256

# Deafults
LOG_FILENAME = "/tmp/discordbot.log"
LOG_LEVEL = logging.INFO 

os.chdir('/home/root/discordbot')

logger = logging.getLogger(__name__)
logger.setLevel(LOG_LEVEL)
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight")
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class Logger(object):
    def __init__(self, logger, level):
        self.logger = logger
        self.level = level

    def write(self, message):
        self.logger.log(self.level, message.rstrip())

sys.stdout = Logger(logger, logging.INFO)
sys.stderr = Logger(logger, logging.ERROR)
client = discord.Client()

def writeToDatabase(name, iv, cp, lvl, location, timestamp):
    lock = threading.Lock()
    lock.acquire()
    try:
        con = sqlite3.connect('pokemon.db')
        cur = con.cursor()
        cur.execute('begin')
        try:
            cur.execute('select id from pokemon where name = "%s"' % name.lower())
            id = cur.fetchone()[0]
            m = sha256()
            m.update('{0}{1}{2}{3}{4}{5}{6}'.format(id, timestamp, location[0], location[1], iv, cp, lvl).encode())
            cur.execute('insert into encounters values(?, ?, ?, ?, ?, ?, ?, ?)', (id, timestamp, location[0], location[1], iv, cp, lvl, m.hexdigest()))
        except sqlite3.IntegrityError:
            pass
        con.commit()
    finally:
        lock.release()

def parseMessage(message):
    lines = message.content.split('\n')
    r = re.search(r'\*\*([a-zA-Z]+)\*\*', lines[0])
    pokemon_name = r.group(1)
    iv = 0
    cp = 0
    lvl = 0

    print(lines[0])
    if '%' in  lines[0]:
        iv = re.search(r'([0-9]+)%', lines[0]).group(1)
        print(iv)
    if 'CP:' in lines[0]:
        cp = re.search(r'CP: ([0-9]+)', lines[0]).group(1)
        print(cp)
    if 'Level:' in lines[0]:
        lvl = re.search(r'Level: ([0-9]+)', lines[0]).group(1)
        print(lvl)
    grp = re.search(r'\=([0-9\-\.]+),([0-9\-\.]+)', lines[-2])
    location = (grp.group(1), grp.group(2))

    writeToDatabase(pokemon_name, iv, cp, lvl, location, message.timestamp)
 

@client.event
async def on_message(message):
    # we do not want the bot to reply to itself
    if message.server.name == 'SydneyPogoMap':
        if message.channel.name in ['general', 'info', 'rules', 'raids-chat', 'raid-level-4', 'raid-legendary']:
            return None

        parseMessage(message)

@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print('------')

with open('token.txt', 'r') as token_file:
    token = token_file.read()
    client.run(token, bot=False)
    
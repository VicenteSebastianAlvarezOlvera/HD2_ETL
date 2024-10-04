import requests
import json
import pandas as pd
from datetime import datetime
from datetime import date

import pyodbc

import os 
from dotenv import load_dotenv
load_dotenv()


raw_data = requests.get('https://api.helldivers2.dev/api/v1/planets') #Main source of information
# raw_current_war_status = requests.get('https://api.helldivers2.dev/api/v1/war') # Not that useful right now
# raw_dispatches = requests.get('https://api.helldivers2.dev/api/v1/dispatches') #Get the dispatches
raw_campaigns = requests.get('https://api.helldivers2.dev/api/v1/campaigns') #raw data but only about active planets
# raw_defending_planets = requests.get('https://api.helldivers2.dev/api/v1/planet-events')#Gets info about planets currently under attack - Also appears in campaigns
raw_major_order = requests.get('https://api.helldivers2.dev/api/v1/assignments') #Major order

current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

campaigns = raw_campaigns.json()
active_planets = []
for i in range(len(campaigns)):
    status = ''
    # print(campaigns[i]['planet'].get('event'))
    index = campaigns[i]['planet'].get('index')
    progress = 0
    faction = ''
    if campaigns[i]['planet'].get('event') != None:
        # print('Defense campaign')
        status = 'Defense campaign'
            #      (campaigns[i]['planet'].get('maxHealth') - campaigns[i]['planet'].get('health')) / campaigns[i]['planet'].get('maxHealth') 
        progress = (campaigns[i]['planet'].get('event').get('maxHealth') - campaigns[i]['planet'].get('event').get('health')) / campaigns[i]['planet'].get('event').get('maxHealth')
        faction = campaigns[i]['planet'].get('event').get('faction')
        # print(campaigns[i]['planet'].get('event').get('maxHealth'), " - ", campaigns[i]['planet'].get('event').get('health'), " / ",campaigns[i]['planet'].get('event').get('maxHealth'))
        #(campaigns[i]['planet'].get('event').get('health'))
    else:
        # print('Liberation campaign')
        status = 'Liberation campaign'
        progress = (campaigns[i]['planet'].get('maxHealth') - campaigns[i]['planet'].get('health')) / campaigns[i]['planet'].get('maxHealth') 
        faction = campaigns[i]['planet'].get('currentOwner')
    # print([index, status, progress])
    active_planets.append([index, status, progress, faction, current_date])


major_order = raw_major_order.json()
expires = major_order[0].get('expiration')
timestamp_str = expires[:-1][:26]
dt_object = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%f')
current_major_order = [major_order[0].get('id'), major_order[0].get('briefing'), major_order[0]['reward'].get('amount'), dt_object]



data = raw_data.json()

player_count_list = []
planet_ownership = []
for i in range (len(data)):
    index = data[i].get('index')
    current_owner = data[i].get('currentOwner')
    player_count = data[i]['statistics'].get('playerCount')
    player_count_list.append([current_date, index, player_count])
    planet_ownership.append([current_date, index, current_owner])


ip = os.getenv('IP')
database = os.getenv('DB_NAME')
uid = os.getenv('DB_USER')
password = os.getenv('DB_PASSWORD')

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={ip};'
    f'DATABASE={database};'
    f'UID={uid};'
    f'PWD={password};'
)

cursor = conn.cursor()

insert_query_active_planets = """
    INSERT INTO active_planets (planet_id, planet_status, progress, faction, time_stamp)
    VALUES (?, ?, ?, ?, ?)
"""
for planet in active_planets:
    print(planet)
    cursor.execute(insert_query_active_planets, planet)

# insert_query_major_order = """
#     INSERT INTO major_orders (id, briefing, reward, expiration)
#     VALUES (?, ?, ?, ?)
# """
# cursor.execute(insert_query_major_order, current_major_order)

insert_query_planet_ownership = """
    INSERT INTO planet_ownership (time_stamp, planet_id, current_owner)
    VALUES (?, ?, ?)
"""
for planet in planet_ownership:
    cursor.execute(insert_query_planet_ownership, planet)

insert_query_player_count = """
    INSERT INTO player_count (time_stamp, planet_id, num_players)
    VALUES (?, ?, ?)
"""
for planet in player_count_list:
    cursor.execute(insert_query_player_count, planet)

conn.commit()

cursor.close()
conn.close()
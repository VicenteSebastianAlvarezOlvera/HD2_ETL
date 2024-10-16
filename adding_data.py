import requests
import json
import pandas as pd
from datetime import datetime
from datetime import date
import csv

import pyodbc

import os 
from dotenv import load_dotenv
load_dotenv()

def get_HD2_data():
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
    # expires = major_order[0].get('expiration')
    # timestamp_str = expires[:-1][:26]
    # dt_object = datetime.strptime(timestamp_str, '%Y-%m-%dT%H:%M:%S.%f')
    # current_major_order = []
    # try: 
    #     current_major_order = [major_order[0].get('id'), major_order[0].get('briefing'), major_order[0]['reward'].get('amount'), dt_object]
    # except: 
    #     current_major_order = []


    data = raw_data.json()

    player_count_list = []
    planet_ownership = []
    planet_stats = []
    for i in range (len(data)):
        playable_faction = ''
        index = data[i].get('index')
        current_owner = data[i].get('currentOwner')
        missionsWon = data[i]['statistics'].get('missionsWon')
        missionsLost = data[i]['statistics'].get('missionsLost')
        missionTime = data[i]['statistics'].get('missionTime')
        terminidKills = data[i]['statistics'].get('terminidKills')
        automatonKills = data[i]['statistics'].get('automatonKills')
        illuminateKills = data[i]['statistics'].get('illuminateKills')
        bulletsFired = data[i]['statistics'].get('bulletsFired')
        bulletsHit = data[i]['statistics'].get('bulletsHit')
        deaths = data[i]['statistics'].get('deaths')
        friendlies = data[i]['statistics'].get('friendlies')
        if data[i].get('event') == None:
            playable_faction = current_owner
        else: 
            playable_faction = data[i].get('event').get('faction')
        player_count = data[i]['statistics'].get('playerCount')
        player_count_list.append([current_date, index, player_count, playable_faction])
        planet_ownership.append([current_date, index, current_owner])
        planet_stats.append([current_date, index, terminidKills,automatonKills, illuminateKills, deaths, bulletsFired, bulletsHit, missionsWon, missionsLost, missionTime, friendlies])


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
    print('Terminid Kills on Super Earth', data[0]['statistics'].get('terminidKills'))
    
    if data[0]['statistics'].get('terminidKills') == 1277:
        print('TRUE')
        insert_query_planet_stats = """
            INSERT INTO planet_statistics (time_stamp, planet_id, terminid_kills, automaton_kills, illuminate_kills, deaths, bullets_fired, bullets_hit, missions_won, missions_lost, mission_time, friendlies)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        for planet in planet_stats:
            print(planet)
            cursor.execute(insert_query_planet_stats, planet)
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
        INSERT INTO player_count (time_stamp, planet_id, num_players, playable_faction)
        VALUES (?, ?, ?, ?)
    """
    for planet in player_count_list:
        cursor.execute(insert_query_player_count, planet)

    conn.commit()

    cursor.close()
    conn.close()

    # try:
    #     conn = pyodbc.connect(
    #         'DRIVER={ODBC Driver 17 for SQL Server};'
    #         f'SERVER={ip};'
    #         f'DATABASE={database};'
    #         f'UID={uid};'
    #         f'PWD={password};'
    #     )
    #     cursor = conn.cursor()

    #     insert_query_planet_stats = """
    #         INSERT INTO planet_statistics (time_stamp, planet_id, terminid_kills, automaton_kills, illuminate_kills, deaths, bullets_fired, bullets_hit, missions_won, missions_lost, mission_time, friendlies)
    #         VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    #     """

    #     # Loop through each planet's stats
    #     for planet in planet_stats:
    #         time_stamp, planet_id, terminid_kills, automaton_kills, illuminate_kills, deaths, bullets_fired, bullets_hit, missions_won, missions_lost, mission_time, friendlies = planet

    #         # Check if the row already exists in the table based on unique constraints
    #         cursor.execute("""
    #             SELECT COUNT(*) 
    #             FROM planet_statistics 
    #             WHERE planet_id = ? 
    #             AND terminid_kills = ? 
    #             AND automaton_kills = ? 
    #             AND illuminate_kills = ? 
    #             AND deaths = ? 
    #             AND bullets_fired = ? 
    #             AND bullets_hit = ? 
    #             AND missions_won = ? 
    #             AND missions_lost = ? 
    #             AND mission_time = ? 
    #             AND friendlies = ?
    #         """, 
    #         (planet_id, terminid_kills, automaton_kills, illuminate_kills, deaths, bullets_fired, bullets_hit, missions_won, missions_lost, mission_time, friendlies))

    #         row_count = cursor.fetchone()[0]

    #         # Only insert if no matching row exists
    #         if row_count == 0:
    #             cursor.execute(insert_query_planet_stats, planet)

    #     conn.commit()

    #     cursor.close()
    #     conn.close()

    # except Exception as e: 
    #     # Log the data that failed to insert
    #     df = pd.DataFrame(planet_stats)
    #     df.to_csv('testing.csv', index=False, header=False, mode='a')
    #     print("Can't be done:", str(e))


get_HD2_data()
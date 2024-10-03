import requests
import json
import pandas as pd
from datetime import datetime

import pyodbc

# Establish the connection
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=172.31.96.27;'
    'DATABASE=HD2ETl;'
    'UID=sa;'
    'PWD=giantGr4pe12!'
)

# Create a cursor
cursor = conn.cursor()


raw_data = requests.get('https://api.helldivers2.dev/api/v1/planets') #Main source of information
data = raw_data.json()
planet_data = []
for i in range (len(data)):
    index = data[i].get('index')
    planet_name = data[i].get('name')
    initial_owner = data[i].get('initialOwner')
    biome = data[i]['biome'].get('name')
    sector = data[i].get('sector')
    x_coordinate = data[i]['position'].get('x')
    y_coordinate = data[i]['position'].get('y')
    planet_data.append([index, planet_name, initial_owner, biome, sector, x_coordinate, y_coordinate])

insert_query = """
    INSERT INTO Planet_Data (planet_id, planet_name, initial_owner, biome, sector, x_coordinate, y_coordinate)
    VALUES (?, ?, ?, ?, ?, ?, ?)
"""

for planet in planet_data:
    cursor.execute(insert_query, planet)

# Commit the transaction
conn.commit()

# Close the connection
cursor.close()
conn.close()
# HD2_ETL

The idea that I want for this project is to create an ETL, taking data from the HellDivers public API, downloading it, create a database with it, and finally make both a Tableau and Power Bi dashboards

The current URLs I will be using for this are the following:
> https://api.helldivers2.dev/api/v1/war

> https://api.helldivers2.dev/api/v1/planets

## The idea
I would like to create a dashboard that is similar between both Tableau and Power Bi. The main information I would like to convey is:
* The amount of current players
* A timeline of current players
1. Players per planet
2. Players per faction
3. Players per sector (maybe)

* Most active planets (amount of players)
* Planet progress
* Planets under attack (defending)
* Keep track of the amount of planets each faction has

## The plan
* Get data from the helldivers public api: schedule this using airflow
* Format the data, add time tag: process the data using python
* Save the data to a DB: Probably sqlserver, maybe hosted locally, maybe hosted in (azure/aws) for students
* From the DB, create a dashboard both in Tableau and Power BI.
* Once the database and airflow are set up, migrate them to the cloud.

## The tools 
* Apache Airflow: to schedule gathering the data every set amount of time
* SQL server: To store the data 
* Python: To get and process the data

## The process
### Getting the data
The first step we need to do is submit a request to said URLs. This is how we will be getting our data. Given that we are going to be using Python for this project, the code shown will be Python.

The first step is to make the request to the Helldivers 2 public API.
For the purposes of this project, I've chosen the following as the main source of information: https://api.helldivers2.dev/api/v1/planets

This gives us the information we are looking for, such as: 
* Index
* Name
* Sector
* Biome
* X and Y Coordinates
* Initial and Current Owner
* Player statistics

In order to get the data, we will use the `requests` library: 
```
import requests
requests.get('https://api.helldivers2.dev/api/v1/planets')
```
This will get us the response, which has the following format: 
```
[
  {
    "index": 0,
    "name": "string",
    "sector": "string",
    "biome": {
      "name": "string",
      "description": "string"
    },
    "hazards": [
      {
        "name": "string",
        "description": "string"
      }
    ],
    "hash": 0,
    "position": {
      "x": 0,
      "y": 0
    },
    "waypoints": [
      0
    ],
    "maxHealth": 0,
    "health": 0,
    "disabled": true,
    "initialOwner": "string",
    "currentOwner": "string",
    "regenPerSecond": 0,
    "event": {
      "id": 0,
      "eventType": 0,
      "faction": "string",
      "health": 0,
      "maxHealth": 0,
      "startTime": "2024-09-27T21:37:17.405Z",
      "endTime": "2024-09-27T21:37:17.405Z",
      "campaignId": 0,
      "jointOperationIds": [
        0
      ]
    },
    "statistics": {
      "missionsWon": 0,
      "missionsLost": 0,
      "missionTime": 0,
      "terminidKills": 0,
      "automatonKills": 0,
      "illuminateKills": 0,
      "bulletsFired": 0,
      "bulletsHit": 0,
      "timePlayed": 0,
      "deaths": 0,
      "revives": 0,
      "friendlies": 0,
      "missionSuccessRate": 0,
      "accuracy": 0,
      "playerCount": 0
    },
    "attacking": [
      0
    ]
  }
]
```

We need to process this data first before we are able to use it. To do so, we first convert it to a json object with: `data = raw_data.json()`. Doing this converts the data to a list

This way, we are now able to manipulate the data itself.

### Processing the data

First, we have to decide what we are going to need. Given what I what to accomplish, we will only take the following information into a couple of lists: 

The first list will take into account the data for the planets and their status
```
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

```

Once we have all the data we need, we will then add it to the database, as shown below


### The Database
The data base to be used in this project is SQL Server, first installed in Ubuntu 20.04.5

I've decided to give it the following structure: 

![Database Schema](https://media.discordapp.net/attachments/774336764517023799/1294384923091665006/image.png?ex=670ad166&is=67097fe6&hm=66b175cb6f31461f5fd8ef3bbdc00d378b3c8b1f957ed2a4cd4c6983f46778d3&=&format=webp&quality=lossless&width=992&height=670 "Database Schema")

#### Planet information

This will show static information from each planet, and used mainly to get the planet name, as reference

* Index
* Planet name
* Initial Owner
* Biome
* Sector
* X Coordinate
* Y Coordinate

#### Player Count

This will keep track of the total number of players per planet, and the current playable faction. If the planet has a liberation or defense campaing, it will be marked for the corresponding faction. Otherwise, if there are players in liberated planets, either they logged in after a successful defense/liberation, or they were AFK for some time while this happened.

* Time
* Index
* Player Count
* Playable Faction

#### Active planets

This shows planets that are currently under a liberation or defense campaing, while also mentioning the faction that is present on this planet, as well as the progress for the campaing.

* Index
* Planet Status
* Progress
* Faction
* Time 

#### Planet ownership

This will keep track of the amount of planets each faction has, over time

* Index
* Time
* Current Owner

#### Major orders

This is used to track major orders

* Id
* Briefing
* Reward
* Expiration

#### Planet statistics

This will keep track of planet statistics accross time, with information about enemy kills, helldivers deaths, mission success rate, etc

* ID
* Kda
* Terminid kills
* Automaton kills
* Illuminate kills
* Deaths
* Bullets fired
* Bullets hit
* Mission_success rate
* Missions won
* Missions lost
* Mission success rate
* Time

### Uploading the data

Once the data  has been processed, and the database has been created, we upload the data in the corresponding tables, using the library `pyodbc`, which allows us to interact with the database.

We need to create a connection to the database, like this: 

``` 
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    f'SERVER={ip};'
    f'DATABASE={database};'
    f'UID={uid};'
    f'PWD={password};'
)
cursor = conn.cursor()
```

Then, for each table, we create the corresponding query: 

```
insert_query_active_planets = """
    INSERT INTO active_planets (planet_id, planet_status, progress, faction, time_stamp)
    VALUES (?, ?, ?, ?, ?)
"""
for planet in active_planets:
    print(planet)
    cursor.execute(insert_query_active_planets, planet)
```

Once all queries have been created and executed, we will "commit" the changes:

```
conn.commit()
```

Finally, we will close the connection to the database: 

```
cursor.close()
conn.close()
```

### Analyzing the data

Once we have uploaded some data, we can create some queries to verify that everything is saved as intended. For this, I've used [SQL Server Management Studio](https://learn.microsoft.com/en-us/sql/ssms/download-sql-server-management-studio-ssms?view=sql-server-ver16)

I've created queries to check the data, such as: 

#### Planet information
```
SELECT * FROM Planet_Data;
```
| planet_id | planet_name | initial_owner | biome | sector | x_coordinate |
| --- | --- | --- | --- | --- | --- |
| 0 | SUPER EARTH | Humans | Unknown | Sol | 0 |
| 1 | KLEN DAHTH II | Humans | Mesa | Altus | 0.05373042 |
| 2 | PATHFINDER V | Humans | Highlands | Altus | 0.04664221 |
| 3 | WIDOW'S HARBOR | Humans | Moon | Altus | 0.12536779 |
| 4 | NEW HAVEN | Humans | Rainforest | Altus | 0.10280278 |
| 5 | PILEN V | Humans | Desert | Altus | 0.15988354 |
| 6 | HYDROFALL PRIME | Humans | Canyon | Barnard | 0.13535836 |
| 7 | ZEA RUGOSIA | Humans | Desert | Ferris | 0.36159223 |
| 8 | DARROWSPORT | Humans | Toxic | Barnard | 0.09485684 |
| 9 | FORNSKOGUR II | Humans | Swamp | Barnard | 0.15801243 |
| 10 | MIDASBURG | Humans | Tundra | Barnard | 0.06770126 |



#### Number of players per planet which aren't owned by Super Earth, by the latest date

```
WITH latest_player_count AS (
	SELECT planet_id, MAX(time_stamp) AS "latest_time_stamp"
	FROM player_count
	GROUP BY planet_id
)
SELECT p_d.planet_name, p.num_players AS "Active Helldivers"
FROM player_count p
JOIN latest_player_count lcp
ON p.planet_id = lcp.planet_id
  AND p.time_stamp = lcp.latest_time_stamp
JOIN Planet_Data p_d
ON p.planet_id = p_d.planet_id
WHERE p.num_players != 0 AND p.playable_faction != 'Humans';
```
| planet_name | Active Helldivers |
| --- | --- |
| HELLMIRE | 12 |
| PENTA | 2 |
| ERSON SANDS | 12 |
| DARIUS II | 1684 |
| CHOOHE | 137 |
| CLAORELL | 28272 |
| CLASA | 1659 |
| FORI PRIME | 6 |
| GACRUX | 1145 |
| LESATH | 504 |
| MENKENT | 231 |
| NIVEL 43 | 1 |
| PANDION-XXIV | 4898 |
| PARTION | 5 |
| PEACOCK | 1066 |
| PHACT BAY | 2232 |

#### Number of players on Super Earth controlled planets, not currently in any campaing, by the latest date
```
WITH latest_player_count AS (
	SELECT planet_id, MAX(time_stamp) AS "latest_time_stamp"
	FROM player_count
	GROUP BY planet_id
	--ORDER BY planet_id
)
SELECT SUM(p.num_players) AS "Active Helldivers"
FROM player_count p
JOIN latest_player_count lcp
ON p.planet_id = lcp.planet_id
  AND p.time_stamp = lcp.latest_time_stamp
WHERE p.num_players != 0 AND p.playable_faction = 'Humans';
```

| Active Helldivers |
| --- |
| 1254 |

#### Planets which have a campaing underway, type of campaing, faction and progress

```
SELECT planet_name, planet_status, progress, faction
FROM active_planets 
JOIN Planet_Data pd
ON active_planets.planet_id = pd.planet_id
WHERE time_stamp IN (SELECT max(time_stamp) FROM active_planets);
```

| planet_name | planet_status | progress | faction |
| --- | --- | --- | --- |
| CHOOHE | Liberation campaign | 0 | Automaton |
| GACRUX | Liberation campaign | 0 | Terminids |
| LESATH | Liberation campaign | 0 | Automaton |
| MENKENT | Liberation campaign | 0 | Automaton |
| CLASA | Liberation campaign | 0 | Automaton |
| PEACOCK | Liberation campaign | 0 | Terminids |
| PHACT BAY | Liberation campaign | 0 | Terminids |
| DARIUS II | Liberation campaign | 0 | Terminids |
| CLAORELL | Liberation campaign | 0.669419 | Automaton |
| PANDION-XXIV | Liberation campaign | 0.465891 | Terminids |


### Automating data collection
Once the data has been verified, we need to automate the data collection, which will allow us to track the data. 

A dag was set up to run every 10 minutes using [Apache Airflow](https://airflow.apache.org/). This way, we are able to track consistenly the main changes in activity, while mantaining a balance of valuable information and space used


### Working on the dashboard
Now that some data has been collected, work on Power Bi was started. Given that a relationship was established between the `Planet_data` and the rest of the tables, the labels can be set with the name of the planets, instead of their ids.

We will need to add some measures to calculate some missing values, or add certain conditions for specific graphs

Using the already available data, I was able to create the following graphs:

#### Timeline of total players, per faction (Stacked area chart)
![Timeline of total players, per faction](https://media.discordapp.net/attachments/774336764517023799/1293683694875312229/image.png?ex=67084454&is=6706f2d4&hm=d490f2c3946aa3f630a85ce080351f882c1022dd7c4920814d6c79301b7303bf&=&format=webp&quality=lossless "Timeline of total players, per faction")

#### Timeline of planets owned by enemy faction (Line chart)
![Timeline of planets owned by enemy faction](https://media.discordapp.net/attachments/774336764517023799/1293683596946571325/image.png?ex=6708443c&is=6706f2bc&hm=65e377b9a3ebfd32d08890099df00178cfc4caf78a92fa9cf2254eaa6245c568&=&format=webp&quality=lossless "Timeline of planets owned by enemy faction")

#### Donut chart for the amount of biomes
![Donut chart for the amount of biomes](https://media.discordapp.net/attachments/774336764517023799/1293683483096645683/image.png?ex=67084421&is=6706f2a1&hm=17b37deb7458581fbc03a1d55ce1f5f488b9dc18ceb62bcd3b5e09382a1797a7&=&format=webp&quality=lossless "Amount of biomes")

#### Donut chart for the amount of players by biome
![Donut chart for the amount of players by biome](https://media.discordapp.net/attachments/774336764517023799/1293683389806809200/image.png?ex=6708440b&is=6706f28b&hm=750bde5e6e7d0da858f91274444973c24608aeecefdf54af28eafe878ddfdc90&=&format=webp&quality=lossless "Players by biome")

#### Table of biomes by faction
![Table of biomes by faction](https://media.discordapp.net/attachments/774336764517023799/1293683255396139139/image.png?ex=670843eb&is=6706f26b&hm=343ca98dbcd9dae3eab029ea1681953dad2d9e9bb800cfaadfbf7816e8dcb335&=&format=webp&quality=lossless "Biomes by faction")

#### Table of player count by biomes per faction
![Table of player count by biomes per faction](https://media.discordapp.net/attachments/774336764517023799/1293683119433711676/image.png?ex=670843cb&is=6706f24b&hm=71f5c4d3b5f9c993db15fa22ea3ccf1a34b70efbb6d4e5cf016b9c623c627a01&=&format=webp&quality=lossless "Player count by biomes per faction")

#### Timeline of player count by biome (Stacked area chart)
![Timeline of player count by biome](https://media.discordapp.net/attachments/774336764517023799/1293682894585335848/image.png?ex=67084395&is=6706f215&hm=17b03e728aa1ae8d4cc684fbd3f14ea70dd0549cdf8cdb7ee2fd2586cab15100&=&format=webp&quality=lossless "Timeline of player count by biome")

#### Galaxy map with player count for size
![Galaxy map with player count for size](https://media.discordapp.net/attachments/774336764517023799/1293682312109752392/image.png?ex=6708430a&is=6706f18a&hm=9139200331371bc3976199d5554ca190da56532b9148ca03663bc40fd4da527e&=&format=webp&quality=lossless "Galaxy map")

#### Timeline of player count by planet (Stacked area chart)
![Timeline of player count by planet](https://media.discordapp.net/attachments/774336764517023799/1293682158539505835/image.png?ex=670842e6&is=6706f166&hm=15f10b9151d916666728601fdd447f3d16ef3151d6f5cf3191c5084e617f59ee&=&format=webp&quality=lossless "Timeline of player count by planet")

#### Donut chart for the amount of players by planet
![Donut chart for the amount of players by planet](https://media.discordapp.net/attachments/774336764517023799/1293675653526192168/image.png?ex=67083cd7&is=6706eb57&hm=e0806182773ed8238fc5863fb9874a02b84eb1d4c87d8529f2124c7aaaca57d4&=&format=webp&quality=lossless "Players by planet")

#### Donut chart for amount of players by faction and planet, with the total amount displayed in the middle
![Donut chart for amount of players by faction and planet, with the total amount displayed in the middle](https://media.discordapp.net/attachments/774336764517023799/1293674814397222986/image.png?ex=67083c0f&is=6706ea8f&hm=e858960c90dc8691ce32e2629fe252beee2c743ed8d79818f4b35197d2d9c81e&=&format=webp&quality=lossless&width=1153&height=670 "Players by faction and planet")

#### Timeline of Liberation Campaings per faction (Stacked area chart)
![Timeline of Liberation Campaings per faction](https://media.discordapp.net/attachments/774336764517023799/1293684329725296701/image.png?ex=670844eb&is=6706f36b&hm=c1a2cdb1970b807fca7c47326d1afbf2a873c8ae4757f78260732d6eeaa9a9e3&=&format=webp&quality=lossless "Players by faction and planet")

#### Timeline of Defense Campaings per faction (Stacked area chart)
![Timeline of Defense Campaings per faction](https://media.discordapp.net/attachments/774336764517023799/1293684626237296650/image.png?ex=67084532&is=6706f3b2&hm=85b64f6b81e1ebfd3e4abcec0a21d77691dc13f2d06c60f85c9e8f9bc73de6c9&=&format=webp&quality=lossless "Players by faction and planet")

#### Timeline of Active planets per faction (Stacked area chart)
![Timeline of Active planets per faction](https://media.discordapp.net/attachments/774336764517023799/1293684710094016632/image.png?ex=67084546&is=6706f3c6&hm=a69fa1e9745b9d2257da247fb44cb7e1fc07da2897b244992aff799205dbafa6&=&format=webp&quality=lossless "Players by faction and planet")

#### Timeline of liberation progress per planet (Area chart)
![Timeline of liberation progress per planet](https://media.discordapp.net/attachments/774336764517023799/1293684825777242168/image.png?ex=67084561&is=6706f3e1&hm=6a67ad396c2114cdf39e29c84fb32f86e6e16580f1d04fa408b2a60ce03aa7fb&=&format=webp&quality=lossless "Players by faction and planet")

### Identifying outliers
There seems to be a bug in the API affecting planet statistics at random intervals, which shows consistent numbers every time this bug happens.
I managed to identify this bug while doing a total enemy kills timeline, which showed a very significant outlier, in which a number was always consistent:

> The sum of terminid kills for a specific timestamp always was equal to: 795792 

Running the following query showed me that this bug had happened 45 times while recolecting the data.

```
SELECT time_stamp, SUM(terminid_kills) 
FROM planet_statistics 
GROUP BY time_stamp 
HAVING SUM(terminid_kills) = 795792
```

Given that the sum is always the same when the bug happens, I added a condition to prevent this, checking that the amount of terminid kills is different than the bugged amount:

```
if data[0]['statistics'].get('terminidKills') == 1277:
```

If this condition is met, then the data from planet statisctics will be uploaded, otherwise it will be skipped.

In order to remove the already saved bugged data, I ran this query:

``` 
DELETE FROM planet_statistics 
WHERE time_stamp IN 
(
  SELECT time_stamp 
  FROM planet_statistics 
  GROUP BY time_stamp 
  HAVING SUM(terminid_kills) = 795792
)
```

### Using cloud technologies
(PENDING)
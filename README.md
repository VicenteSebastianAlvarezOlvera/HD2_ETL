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

We need to process this data first before we are able to use it. To do so, we first convert it to a json object with:
`data = raw_data.json()`

This way, we are now able to manipulate the data itself.
### Processing the data

First, we have to decide what we are going to need. Given what I what to accomplish, we will only take the following information into a couple of lists: 

The first list will take into account the data for the planets and their status
```
planet_data = []
for i in range (len(data)):
    index = data[i].get('index')
    planet_name = data[i].get('name')
    current_owner = data[i].get('currentOwner')
    initial_owner = data[i].get('initialOwner')
    biome = data[i]['biome'].get('name')
    sector = data[i].get('sector')
    x_coordinate = data[i]['position'].get('x')
    y_coordinate = data[i]['position'].get('y')
    status = ''
    if data[i].get('health') != 1000000:
        status = 'Liberation campaing'
    elif data[i].get('event') != None:
        status = 'Defense campaing'
    else:
        status = 'Disabled'
    planet_data.append([index, planet_name, current_owner, initial_owner, biome, sector, x_coordinate, y_coordinate, status])
```



### The Database
The data base to be used in this project is ______.

I've decided to give it the following structure: 

#### Planet information
 | Index | Planet name | Current owner | Initial Owner | Biome | Sector | X Coordinate | Y Coordinate | Status | 

#### Player Count
 | Time | Index | Player Count | Owner | 

#### Battle Information
 | Time | Index | Current Owner | Mission Success Rate | Current Kill Death Ratio | Total Deaths | Terminid Kills | Automaton Kills | 
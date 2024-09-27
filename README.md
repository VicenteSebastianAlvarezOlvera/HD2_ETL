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
The first step we need to do is submit a request to said URLs. This is how we will be getting our data


### The Database
The data base to be used in this project is ______.

I've decided to give it the following structure: 

#### Planet information
 | Index | Planet name | Current owner | Initial Owner | Biome | Sector | X Coordinate | Y Coordinate | Status | 

#### Player Count
 | Time | Index | Player Count | Owner | 

#### Battle Information
 | Time | Index | Current Owner | Mission Success Rate | Current Kill Death Ratio | Total Deaths | Terminid Kills | Automaton Kills | 
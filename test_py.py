import pyodbc
import os 
from dotenv import load_dotenv
load_dotenv()

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
cursor.execute("SELECT @@version;")
row = cursor.fetchone()
print(row)

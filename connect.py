import psycopg2
from config import config
import pandas as pd

def connect():
    """ Connect to the PostgreSQL database server """
    conn = None
    try:
        # read connection parameters
        params = config()

        # connect to the PostgreSQL server
        print('Connecting to the PostgreSQL database...')
        conn = psycopg2.connect(**params)
		
        # create a cursor
        cur = conn.cursor()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    return cur

cursor = connect()

# Load data from table V12_Platinum_158_dataset_All_stages
cursor.execute("SELECT * FROM v12_platinum_158_dataset_1")

# Obtain all rows of data table
v12_plat_158 = cursor.fetchall()

# Obtain column names
colnames = [desc[0] for desc in cursor.description]

# Create pandas DataFrame from list of tuples
df = pd.DataFrame(v12_plat_158)

# Add column names to respective columns
df.columns = colnames

# Display first five rows of pandas DataFrame
print(df.head())
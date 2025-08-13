import os
from pathlib import Path

from dotenv import load_dotenv
from psycopg2 import connect, extensions

dotenv_path = Path('.devcontainer/.env')
load_dotenv(dotenv_path=dotenv_path)

netbox_db_name = os.getenv('NETBOX_DB_NAME')
netbox_db_user = os.getenv('NETBOX_DB_USER')
netbox_db_password = os.getenv('NETBOX_DB_PASSWORD')


# Connect to your postgres DB
conn = connect(host='db', user='postgres', password='postgres')

# set the isolation level for the connection's cursors
# will raise ActiveSqlTransaction exception otherwise
autocommit = extensions.ISOLATION_LEVEL_AUTOCOMMIT
conn.set_isolation_level(autocommit)

# Open a cursor to perform database operations
cur = conn.cursor()

# The below 2 lines are required if the database already exists
cur.execute(f"DROP DATABASE {netbox_db_name};")
cur.execute(f"DROP USER {netbox_db_user};")

cur.execute(f'CREATE DATABASE {netbox_db_name};')
cur.execute(f"CREATE USER netbox WITH PASSWORD '{netbox_db_password}';")
cur.execute(f'ALTER DATABASE {netbox_db_name} OWNER TO {netbox_db_user};')

# Required to run unittest as the django user need to create the test db
cur.execute(f'ALTER ROLE {netbox_db_user} CREATEDB;')

# Make the changes to the database persistent
conn.commit()

# Close communication with the database
cur.close()
conn.close()

# required on postgres v15 or later
conn = connect(host='db', user='postgres', password='postgres', database=netbox_db_name)
autocommit = extensions.ISOLATION_LEVEL_AUTOCOMMIT
conn.set_isolation_level(autocommit)
cur = conn.cursor()
cur.execute(f'GRANT CREATE ON SCHEMA public TO {netbox_db_user};')
conn.commit()
cur.close()
conn.close()

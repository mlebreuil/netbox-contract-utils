import os
from pathlib import Path
from dotenv import load_dotenv

from psycopg import connect

dotenv_path = Path('.devcontainer/.env')
load_dotenv(dotenv_path=dotenv_path)

netbox_db = os.getenv('NETBOX_DB_NAME')
netbox_user = os.getenv('NETBOX_DB_USER')
netbox_password = os.getenv('NETBOX_DB_PASSWORD')

host = 'db'
postgres_user = os.getenv('POSTGRES_USER')
postgres_password = os.getenv('POSTGRES_PASSWORD')


# Connect to your postgres DB
conn = connect(host=host, user=postgres_user, password=postgres_password, autocommit=True)

# Open a cursor to perform database operations
cur = conn.cursor()

# The below 2 lines are required if the database already exists
cur.execute(f"DROP DATABASE {netbox_db};")
cur.execute(f"DROP USER {netbox_user};")

cur.execute(f'CREATE DATABASE {netbox_db};')
cur.execute(f"CREATE USER {netbox_user} WITH PASSWORD '{netbox_password}';")
cur.execute(f'ALTER DATABASE {netbox_db} OWNER TO {netbox_user};')

# Required to run unittest as the django user need to create the test db
cur.execute(f'ALTER ROLE {netbox_user} CREATEDB;')

# Make the changes to the database persistent
conn.commit()

# Close communication with the database
cur.close()
conn.close()

# required on postgres v15 or later
conn = connect(host=host, user=postgres_user, password=postgres_password, dbname=netbox_db)
cur = conn.cursor()
cur.execute(f'GRANT CREATE ON SCHEMA public TO {netbox_user};')
conn.commit()
cur.close()
conn.close()

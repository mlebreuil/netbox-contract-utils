"""Create the NetBox database and user, optionally loading a NetBox SQL dump.

Usage (in the dev container):

    python3 database_init.py                       # empty database, NetBox creates the tables
    python3 database_init.py netbox-demo-v4.7.sql  # load the NetBox demo data

The database and user already existing are dropped and re-created.
The settings come from .devcontainer/.env, which docker-compose loads into the
environment of the dev container. Rebuild the container after changing .env.

A dump must be from the same major.minor NetBox version as the NetBox checkout, or older:
'netbox/upgrade.sh' then applies the missing migrations.
"""

import os
import subprocess
import sys
from pathlib import Path

from psycopg import connect, errors

netbox_db = os.getenv('NETBOX_DB_NAME')
netbox_user = os.getenv('NETBOX_DB_USER')
netbox_password = os.getenv('NETBOX_DB_PASSWORD')

# PGHOST is set to the database service in the dev container
host = os.getenv('PGHOST', 'db')
postgres_user = os.getenv('POSTGRES_USER')
postgres_password = os.getenv('POSTGRES_PASSWORD')

missing = [
    name
    for name, value in {
        'NETBOX_DB_NAME': netbox_db,
        'NETBOX_DB_USER': netbox_user,
        'NETBOX_DB_PASSWORD': netbox_password,
        'POSTGRES_USER': postgres_user,
        'POSTGRES_PASSWORD': postgres_password,
    }.items()
    if not value
]
if missing:
    sys.exit(f"Missing environment variables: {', '.join(missing)}. Check .devcontainer/.env and rebuild the container.")

# Optional SQL dump to load (checked before anything is dropped)
dump = None
if len(sys.argv) > 2:
    sys.exit(f'Usage: {sys.argv[0]} [dump.sql]')
if len(sys.argv) == 2:
    dump = Path(sys.argv[1])
    if not dump.is_file():
        sys.exit(f'Dump file not found: {dump}')
    # The NetBox demo data assigns the objects to the "netbox" role
    if netbox_user != 'netbox':
        sys.exit(
            f'The dump assigns the objects to the "netbox" role but NETBOX_DB_USER is "{netbox_user}". '
            'Set NETBOX_DB_USER=netbox in .devcontainer/.env and rebuild the container.'
        )

# Connect to your postgres DB
conn = connect(host=host, user=postgres_user, password=postgres_password, autocommit=True)
cur = conn.cursor()

# Start from scratch if the database and user already exist.
# On a brand-new server they do not exist yet: report it and carry on.
try:
    cur.execute(f'DROP DATABASE {netbox_db};')
except errors.InvalidCatalogName:
    print(f'Database {netbox_db} does not exist, nothing to drop.')

try:
    cur.execute(f'DROP USER {netbox_user};')
except errors.UndefinedObject:
    print(f'User {netbox_user} does not exist, nothing to drop.')

# Database and user, as in the NetBox installation guide (PostgreSQL step)
cur.execute(f'CREATE DATABASE {netbox_db};')
# CREATEDB (not in the guide) is required to run the unit tests: the django user creates the test database
cur.execute(f"CREATE USER {netbox_user} WITH PASSWORD '{netbox_password}' CREATEDB;")
cur.execute(f'ALTER DATABASE {netbox_db} OWNER TO {netbox_user};')
cur.close()
conn.close()

# Required on PostgreSQL 15 or later (the guide runs it after "\connect netbox")
conn = connect(host=host, user=postgres_user, password=postgres_password, dbname=netbox_db, autocommit=True)
cur = conn.cursor()
cur.execute(f'GRANT CREATE ON SCHEMA public TO {netbox_user};')
cur.close()
conn.close()

if dump:
    # The dump is loaded as is, with a single exception. It starts with
    #   SELECT pg_catalog.set_config('search_path', '', false);
    # and creates the ltree extension in the public schema. With an empty search_path the "=" operator of ltree
    # cannot be found when the triggers that compare ltree columns are created
    # ("operator does not exist: public.ltree = public.ltree"). The search_path is therefore set to public
    # for the session that loads the dump. The dump file itself is not modified.
    sql = dump.read_text(encoding='utf-8')
    empty_search_path = "SELECT pg_catalog.set_config('search_path', '', false);"
    if empty_search_path in sql:
        sql = sql.replace(empty_search_path, "SELECT pg_catalog.set_config('search_path', 'public', false);", 1)

    print(f'Loading {dump} ...')
    result = subprocess.run(
        [
            'psql',
            '--host', host,
            '--username', postgres_user,
            '--dbname', netbox_db,
            '--quiet',
            '--set', 'ON_ERROR_STOP=1',
            '--single-transaction',
        ],
        input=sql,
        text=True,
        stdout=subprocess.DEVNULL,
        env={**os.environ, 'PGPASSWORD': postgres_password},
    )
    if result.returncode != 0:
        sys.exit(f'Loading {dump} failed (psql exit code {result.returncode}). Nothing was loaded.')

print(f'Database {netbox_db} ready' + (f' (loaded {dump}).' if dump else '.'))

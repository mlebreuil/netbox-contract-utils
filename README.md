# Netbox contract utils

Files and instructions to set up a development environment for the
[netbox-contract](https://github.com/mlebreuil/netbox-contract) plugin, using a VS Code dev container.

The dev container runs three services with Docker Compose:

| Service | Purpose | Reachable from the app container as |
|---|---|---|
| `app` | Python 3.12, NetBox, the plugin, VS Code server | - |
| `db` | PostgreSQL (version set by `POSTGRES_VERSION`, default 17) | `db` (also `localhost`) |
| `redis` | Redis 7 | `redis` |

## Folder layout

The `netbox` folder is the root of the dev environment. It is the folder you open in VS Code and the only one mounted
in the container (at `/workspaces/netbox`).

```text
netbox/                          <- root folder, opened in VS Code
├── .devcontainer/               <- from this repository (keep your own .env)
├── .claude/settings.json        <- Claude Code permissions (optional, see "Run Claude Code on the Mac")
├── CLAUDE.md                    <- instructions for Claude Code (optional)
├── dc                           <- runs a command in the dev container from the Mac (optional)
├── netbox/                      <- clone of netbox-community/netbox (venv is created in netbox/venv)
├── netbox-contract/             <- clone of the plugin repository
├── netbox-demo-v4.7.sql         <- netbox demo data, same major.minor as the NetBox clone
├── database_init.py
├── requirements.txt
├── configuration_testing.py
├── netbox-configuration-4.7.py
├── netbox-configuration-4.7-final.py
└── netbox.code-workspace
```

## Create the dev container

1. Create the `netbox` root folder.
2. Clone this repository into the root folder (or anywhere else) and copy the dev environment files to the root
   folder:

   ```bash
   cd netbox        # the root folder
   git clone https://github.com/mlebreuil/netbox-contract-utils.git
   cd netbox-contract-utils
   cp -R .devcontainer ..
   cp requirements.txt database_init.py configuration_testing.py \
      netbox-configuration-4.7.py netbox-configuration-4.7-final.py dc ..
   cp claude/CLAUDE.md ../CLAUDE.md
   mkdir -p ../.claude && cp claude/settings.json ../.claude/settings.json
   cd ..
   ```

   If you cloned this repository somewhere else, replace `..` with the path of the root folder.

3. Clone the plugin into the root folder:

   ```bash
   git clone https://github.com/mlebreuil/netbox-contract.git
   ```

4. Create your local environment file. `.env` is ignored by git: it holds passwords and secrets and must never be
   committed.

   ```bash
   cp .devcontainer/.env.example .devcontainer/.env
   ```

   Fill in the database passwords, then generate a value for `NETBOX_SECRET_KEY` and another one for
   `NETBOX_API_TOKEN_PEPPER` (run the command twice; any machine with Python 3 works):

   ```bash
   python3 -c "import secrets, string; print(''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(64)))"
   ```

   Optional: set `POSTGRES_VERSION` to the PostgreSQL major version you want (default 17). If you keep an existing
   `postgres-data` volume, it must match the version that created it.
5. Download the [netbox demo data](https://github.com/netbox-community/netbox-demo-data) file matching the
   major.minor version of NetBox (for NetBox 4.7.x: `netbox-demo-v4.7.sql`) and save it in the root folder.
6. Open the root folder in VS Code and save the workspace definition to the root folder
   (File > Save workspace as `netbox.code-workspace`).
7. Press F1 > `Dev Containers: Rebuild and Reopen in Container`.

The values of `.env` are loaded into the container environment when the container is created: after changing
`.env`, rebuild the container.

On creation, the container installs `requirements.txt` (needed by `database_init.py`). It also sets `PGHOST`, `PGUSER`
and `PGPASSWORD` from `.env`, so `psql`, `pg_dump` and `pg_restore` work without connection options. Port 8000 is
forwarded to your machine.

Notes:

- The PostgreSQL service runs with `fsync` disabled to speed up tests and data loads. Do not keep data you cannot
  recreate from a dump in it.
- The Claude Code configuration (`~/.claude`) is kept in a Docker volume and survives container rebuilds.

## Initialize the database

Run in a terminal of the dev container, from the root folder. The script drops and re-creates the NetBox database and
user defined in `.env`. On a brand-new server there is nothing to drop: the script reports it and continues.

To start with the NetBox demo data (recommended for plugin development):

```bash
python3 database_init.py netbox-demo-v4.7.sql
```

Or, for an empty database:

```bash
python3 database_init.py
```

Notes:

- The demo data file must match the major.minor version of the NetBox checkout (`netbox-demo-v<major>.<minor>.sql`),
  or be older: `upgrade.sh` then applies the missing migrations. A dump from a newer version is not usable.
- The demo data assigns its objects to the `netbox` database role: `NETBOX_DB_NAME` can be anything but
  `NETBOX_DB_USER` must be `netbox`. The script stops before dropping anything if it is not.
- The dump is loaded in a single transaction: if loading fails, nothing is loaded.
- The dump file is not modified. Its first statement sets an empty `search_path`, which makes the load fail with
  `operator does not exist: public.ltree = public.ltree` (the `ltree` extension is installed in the `public` schema).
  The script sets the `search_path` to `public` for the load only.
- The demo data contains the `admin` superuser (see [Superuser](#superuser)).
- To reset the database later, run the script again.

## Install Netbox

[NetBox installation documentation](https://netboxlabs.com/docs/netbox/en/stable/installation/3-netbox/)

### Clone the netbox repository

```bash
git clone https://github.com/netbox-community/netbox.git netbox
```

You do not need to create the NetBox system user.

To work on a specific release, check out its tag (`git -C netbox checkout v4.7.x`).

### Secrets

`SECRET_KEY` and `API_TOKEN_PEPPERS` are never stored in the configuration files: they are read from the
`NETBOX_SECRET_KEY` and `NETBOX_API_TOKEN_PEPPER` environment variables, which come from your local
`.devcontainer/.env` (see [Create the dev container](#create-the-dev-container)). Never write them in a file that is
committed.

### Configure netbox

The configuration file name matches the NetBox version (`netbox-configuration-<major.minor>.py`) and is the NetBox
`configuration_example.py` of that version, adjusted for the dev container (database and Redis hosts, secrets read from
the environment, `DEVELOPER = True`). When you move to a new NetBox version, create the new files from the new example
(see [Upgrade Netbox](#upgrade-netbox)).

Use the first configuration (without the plugin) to install NetBox:

```bash
cp netbox-configuration-4.7.py netbox/netbox/netbox/configuration.py
```

### Run the upgrade script

```bash
cd netbox
./upgrade.sh
cd ..
```

It runs the database migrations: with the demo data loaded they only apply what is newer than the dump.

This creates the virtual environment in `netbox/venv`. Once it exists, run `Developer: Reload Window` in VS Code so the
Python extension selects `netbox/venv/bin/python` automatically.

Activate the environment in every new terminal:

```bash
source netbox/venv/bin/activate
```

### Superuser

With the demo data, the database already contains the `admin` superuser: do not run `createsuperuser`. If you do not
know the password of the demo `admin` user, set one:

```bash
python3 netbox/netbox/manage.py changepassword admin
```

With an empty database, create a superuser instead:

```bash
python3 netbox/netbox/manage.py createsuperuser
```

### Test installation

```bash
python3 netbox/netbox/manage.py runserver 0.0.0.0:8000 --insecure
```

NetBox is available at <http://localhost:8000>.

## Install the plugin

For development, install the plugin in editable mode from the local file system:

```bash
source netbox/venv/bin/activate
python3 -m pip uninstall netbox-contract
python3 -m pip install -e netbox-contract
```

Switch to the configuration that enables the plugin:

```bash
cp netbox-configuration-4.7-final.py netbox/netbox/netbox/configuration.py
```

It differs from the first configuration by the plugin settings:

```python
PLUGINS = ['netbox_contract']
PLUGINS_CONFIG = {
    'netbox_contract': {
        'top_level_menu': True,
    }
}
# plus FIELD_CHOICES for the plugin fields
```

Run the database migrations:

```bash
python3 netbox/netbox/manage.py migrate
```

Install pre-commit:

```bash
cd netbox-contract
python3 -m pip install pre-commit
pre-commit install
cd ..
```

Test the installation:

```bash
python3 netbox/netbox/manage.py runserver 0.0.0.0:8000 --insecure
```

To install the plugin from another source instead of the local folder:

```bash
python3 -m pip uninstall netbox-contract

# from the test PyPI repository
python3 -m pip install --index-url https://test.pypi.org/simple/ --no-deps netbox-contract

# from PyPI
python3 -m pip install netbox-contract
```

## Create demo data

Netbox demo data should be loaded first.

Start the rq worker:

```bash
python3 netbox/netbox/manage.py rqworker high default low
```

Import the `create-demo-data.py` custom script in NetBox (Customization > Scripts) and run it.

## Run unit tests locally

```bash
source netbox/venv/bin/activate
cp configuration_testing.py netbox/netbox/netbox/configuration_testing.py
cd netbox
NETBOX_CONFIGURATION=netbox.configuration_testing python3 netbox/manage.py test netbox_contract.tests --keepdb
```

`--keepdb` keeps the test database between runs. Drop it if you need a fresh test database.

`configuration_testing.py` is the dev container version of the configuration used by CI: the database credentials come
from `.devcontainer/.env`, and the tests use Redis databases 2 and 3 so that a test run does not flush the queue and the
cache of the development server (databases 0 and 1).

### Update the query counts for the tests

Set the `UPDATE_QUERY_COUNTS` environment variable before running the tests, and run them serially (no `--parallel`):

```bash
export UPDATE_QUERY_COUNTS=1
```

## Model changes

Create the migrations:

```bash
source netbox/venv/bin/activate
python3 netbox/netbox/manage.py makemigrations netbox_contract --dry-run
python3 netbox/netbox/manage.py makemigrations netbox_contract
```

Apply the migrations:

```bash
python3 netbox/netbox/manage.py migrate
```

## Upgrade Netbox

Make sure the plugin is listed in the NetBox `local_requirements.txt` (file in the `netbox` repository clone), so that
`upgrade.sh` reinstalls it. Use the editable form: without `-e`, pip builds a wheel and installs a copy of the plugin in
`netbox/venv`, and your source changes are not used until you reinstall it.

```text
-e ../netbox-contract
```

```bash
cd netbox
git checkout main
git pull origin main
./upgrade.sh
cd ..
```

When the new release is a new major.minor version (for example 4.8):

1. Compare the new `netbox/netbox/netbox/configuration_example.py` with the current `netbox-configuration-<x.y>.py`
   and carry over the new or changed settings.
2. Save the result as `netbox-configuration-<new x.y>.py` and `netbox-configuration-<new x.y>-final.py`, and remove the
   old files.
3. Download the matching demo data (`netbox-demo-v<new x.y>.sql`) if you need to reload it.

`upgrade.sh` re-creates the virtual environment. Re-activate it in your terminals, check that the plugin is still
installed in editable mode (see [Install the plugin](#install-the-plugin)) and that the pre-commit hook is in place:

```bash
source netbox/venv/bin/activate
python3 -m pip install pre-commit
pre-commit install
```

## Run Claude Code on the Mac

Claude Code can run in a Mac terminal while the development environment stays in the dev container. The root folder is
shared with the container, so Claude reads and edits the files directly on the Mac, and runs everything that needs
Python, PostgreSQL or Redis in the container through the `dc` script. VS Code keeps the container running (open the root
folder in the container as usual).

Setup, once:

1. Install the dev container command-line tool on the Mac, with Homebrew:

   ```bash
   brew install devcontainer
   ```

   or with npm, in a folder you own (a plain `npm install -g` fails with `EACCES` when Node is installed in
   `/usr/local`; do not use `sudo`):

   ```bash
   mkdir -p ~/.npm-global
   npm config set prefix ~/.npm-global
   echo 'export PATH="$HOME/.npm-global/bin:$PATH"' >> ~/.zshrc
   source ~/.zshrc
   npm install -g @devcontainers/cli
   ```

2. Make sure `dc`, `CLAUDE.md` and `.claude/settings.json` are in the root folder (see
   [Create the dev container](#create-the-dev-container)) and that `dc` is executable (`chmod +x dc`).
3. Check that it works, with the container running:

   ```bash
   cd ~/github/netbox
   ./dc echo hello --version
   ./dc pwd
   ```

   The first command must print `hello --version`, the second `/workspaces/netbox`.

Usage: start `claude` from the root folder.

| Command | What it does |
|---|---|
| `./dc <command> [args]` | Runs the command in the container, in the folder that matches the current one (`../dc` from a repository folder) |
| `./dc test [args]` | Unit tests with the test configuration; without argument the whole suite with `--keepdb` |
| `./dc manage <args>` | `netbox/manage.py` with the NetBox virtual environment |
| `./dc shell` | Interactive shell in the container |
| `./dc up` | Starts the container without VS Code |

What lets later sessions use it:

- `CLAUDE.md` in the root folder tells Claude that it runs on the Mac, that Python, tests and pre-commit run in the
  container through `dc`, and how paths map (`/workspaces/netbox` is the root folder). Claude Code reads it when started
  from the root folder or from a folder below it.
- `.claude/settings.json` allows `./dc` and `../dc` without a prompt and denies reading `netbox/venv`. It lets Claude run
  any command in the container as the `vscode` user, which is what it needs to test; it gives no other access to Docker.
  It is read when `claude` starts in the root folder.
- Commits are made in the container (`./dc git commit …`), where the pre-commit hook is installed: the hook points to the
  virtual environment of the container and does not work on the Mac. VS Code copies your git identity into the
  container when it is attached.
- Paths in tracebacks are container paths: `/workspaces/netbox/...` is the root folder on the Mac.
- The unit tests need `configuration_testing.py` copied into NetBox (see
  [Run unit tests locally](#run-unit-tests-locally)).

## Backup and restore the db

The `PG*` environment variables of the container provide the host and credentials.

```bash
pg_dump netbox > netbox.sql
```

Restore:

```bash
psql -c 'drop database netbox'
psql -c 'create database netbox'
psql netbox < netbox.sql
psql -c "alter database netbox owner to netbox;"
```

If you change `POSTGRES_VERSION`, take a dump first: a PostgreSQL server does not start on a data directory created by
another major version. Restore the dump into the new `postgres-data` volume.

## Releases

Releases are automated with GitHub Actions: each time a GitHub release is created, a package is built and published to
PyPI.

The package version is defined in a single place, `netbox_contract/version.py` (`__version__`); `pyproject.toml` reads it
from there. Increment it before the release.

To build and check the distribution archives manually:

```bash
source netbox/venv/bin/activate
cd netbox-contract
python3 -m pip install --upgrade build
python3 -m build
```

To publish manually (normally not needed):

```bash
python3 -m pip install --upgrade pip twine

# test PyPI
python3 -m twine upload --repository testpypi dist/*

# PyPI
python3 -m twine upload dist/*
```

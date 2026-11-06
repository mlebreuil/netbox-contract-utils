# NetBox dev environment (root folder)

Claude Code runs on the Mac. The development environment (Python, NetBox, PostgreSQL, Redis, pre-commit) lives in the
dev container, which VS Code keeps running. The root folder is mounted in the container as `/workspaces/netbox`, so
files are shared: read, search and edit them directly on the Mac.

## Run everything else in the container with `./dc`

`./dc` is in this folder (use `../dc` from a repository folder). It runs the command in the container, in the folder
that matches the current one.

- `./dc <command> [args]`: any command, e.g. `./dc ruff check`, `./dc git status`
- `./dc test [args]`: the unit tests with the test configuration; no argument runs the whole suite with `--keepdb`
- `./dc manage <args>`: `netbox/manage.py` with the NetBox virtualenv, e.g. `./dc manage makemigrations netbox_contract --check --dry-run`
- `./dc shell`: interactive shell

Rules:

- Never run Python, `manage.py`, tests, `pip`, `pre-commit` or `ruff` on the Mac: there is no usable environment there.
  `netbox/venv` is a Linux virtualenv for the container. Do not read or search it.
- Skills and documents that give commands for "the dev container" (`venv/bin/python netbox/manage.py …`, run-tests,
  AGENTS.md) are run through `./dc`.
- Paths in tracebacks and tool output are container paths: `/workspaces/netbox/...` is `<this folder>/...` on the Mac.
- Commit through the container (`./dc git commit …`), so that the pre-commit hook runs. Never bypass the hook.
- If `./dc` reports that the container is not found, ask the user to open the folder in the container in VS Code
  (or run `./dc up`).

## Repositories

- `netbox/`: clone of netbox-community/netbox (not to be modified)
- `netbox-contract/`: the plugin; follow its `AGENTS.md`, including the AI policy
- `netbox-contract-utils/`: the files of this environment (devcontainer, configuration, README)

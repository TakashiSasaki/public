# file-catalog

Windows desktop inventory app.

## Run

```powershell
uv run python -m file_catalog.main
```

## Current Behavior

- The app does not scan automatically at startup.
- Click `Refresh Desktop Scan` to run an explicit scan.
- Click `Open Data Folder` to open the directory where the SQLite DB is stored.

## Data Storage

- Database file: `desktop_items.sqlite3`
- Base directory: `platformdirs.user_data_dir(appname="file_catalog", appauthor="work.moukaeritai")`



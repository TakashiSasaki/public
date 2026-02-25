# git-lfs-lite

Python only (standard library) minimal Git LFS server implementation.

## Supported features

- Batch API (`POST /info/lfs/objects/batch`)
- Basic transfer adapter
  - upload: `PUT /info/lfs/objects/{oid}`
  - verify: `POST /info/lfs/objects/{oid}/verify`
  - download: `GET /info/lfs/objects/{oid}`
- Locking API
  - create: `POST /info/lfs/locks`
  - list: `GET /info/lfs/locks`
  - verify: `POST /info/lfs/locks/verify`
  - unlock: `POST /info/lfs/locks/{id}/unlock`
- Auth mode:
  - none
  - Basic auth (single user/password)
- Source IP allow-list by CIDR

## Run

```powershell
python .\lfs_server.py --host 0.0.0.0 --port 8080 --storage-dir .\data
```

Basic auth mode:

```powershell
python .\lfs_server.py `
  --host 0.0.0.0 `
  --port 8080 `
  --storage-dir .\data `
  --auth-mode basic `
  --basic-user lfs `
  --basic-pass secret
```

Allow only some source IP ranges:

```powershell
python .\lfs_server.py `
  --allow-net 10.0.0.0/8 `
  --allow-net 192.168.0.0/16 `
  --allow-net 127.0.0.1/32
```

Or by env:

```powershell
$env:LFS_ALLOW_NETS="10.0.0.0/8,192.168.0.0/16,127.0.0.1/32"
python .\lfs_server.py
```

## Config options

- `--base-path` (default: `/info/lfs`)
- `--auth-mode` (`none` or `basic`)
- `--basic-user`
- `--basic-pass`
- `--allow-net` (repeatable CIDR)
- `--allow-nets` (comma-separated CIDR list)

Environment variable alternatives:

- `LFS_HOST`, `LFS_PORT`
- `LFS_BASE_PATH`
- `LFS_STORAGE_DIR`
- `LFS_AUTH_MODE`
- `LFS_BASIC_USER`, `LFS_BASIC_PASS`
- `LFS_ALLOW_NETS`

## Git LFS client example

Repository local config:

```powershell
git config lfs.url http://127.0.0.1:8080/info/lfs
```

If basic auth is used:

```powershell
git config lfs.url http://lfs:secret@127.0.0.1:8080/info/lfs
```

Then track and push:

```powershell
git lfs install
git lfs track "*.bin"
git add .gitattributes large.bin
git commit -m "Add large file"
git push
```

## Notes

- Object files are stored at `data/objects/<oid-prefix>/.../<oid>`.
- Lock metadata is stored in `data/locks.json`.
- This is a minimal implementation for private/self-hosted use. Production deployment should be behind HTTPS reverse proxy and proper credential management.

## Spec references

- Batch API: https://raw.githubusercontent.com/git-lfs/git-lfs/main/docs/api/batch.md
- Basic transfer adapter: https://raw.githubusercontent.com/git-lfs/git-lfs/main/docs/api/basic-transfers.md
- Locking API: https://raw.githubusercontent.com/git-lfs/git-lfs/main/docs/api/locking.md

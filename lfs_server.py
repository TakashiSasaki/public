#!/usr/bin/env python3
import argparse
import base64
import datetime as dt
import hashlib
import ipaddress
import json
import os
import threading
import uuid
from dataclasses import dataclass
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlsplit


JSON_MIME = "application/vnd.git-lfs+json"
DEFAULT_BASE = "/info/lfs"


def utc_now_iso() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class ServerConfig:
    host: str
    port: int
    base_path: str
    storage_dir: Path
    lock_db: Path
    auth_mode: str
    basic_user: str
    basic_pass: str
    allow_networks: list[ipaddress._BaseNetwork]


class LockStore:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._lock = threading.Lock()
        ensure_dir(path.parent)
        if not self.path.exists():
            self._write({"locks": []})

    def _read(self) -> dict[str, Any]:
        with self.path.open("r", encoding="utf-8") as f:
            return json.load(f)

    def _write(self, data: dict[str, Any]) -> None:
        tmp = self.path.with_suffix(".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=True, indent=2)
        tmp.replace(self.path)

    def create_lock(self, path: str, owner: str) -> tuple[bool, dict[str, Any]]:
        with self._lock:
            data = self._read()
            for lock in data["locks"]:
                if lock["path"] == path:
                    return False, lock
            lock = {
                "id": str(uuid.uuid4()),
                "path": path,
                "locked_at": utc_now_iso(),
                "owner": {"name": owner},
            }
            data["locks"].append(lock)
            self._write(data)
            return True, lock

    def find_lock(self, lock_id: str) -> dict[str, Any] | None:
        with self._lock:
            data = self._read()
            for lock in data["locks"]:
                if lock["id"] == lock_id:
                    return lock
            return None

    def list_locks(
        self, path: str | None, lock_id: str | None, cursor: str | None, limit: int
    ) -> tuple[list[dict[str, Any]], str]:
        with self._lock:
            data = self._read()
            locks = data["locks"]
            if path:
                locks = [l for l in locks if l["path"] == path]
            if lock_id:
                locks = [l for l in locks if l["id"] == lock_id]
            start = int(cursor) if cursor else 0
            sliced = locks[start : start + limit]
            next_cursor = str(start + limit) if (start + limit) < len(locks) else ""
            return sliced, next_cursor

    def verify_locks(self, owner: str, cursor: str | None, limit: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]], str]:
        with self._lock:
            data = self._read()
            locks = data["locks"]
            start = int(cursor) if cursor else 0
            sliced = locks[start : start + limit]
            ours = [l for l in sliced if l.get("owner", {}).get("name") == owner]
            theirs = [l for l in sliced if l.get("owner", {}).get("name") != owner]
            next_cursor = str(start + limit) if (start + limit) < len(locks) else ""
            return ours, theirs, next_cursor

    def delete_lock(self, lock_id: str) -> dict[str, Any] | None:
        with self._lock:
            data = self._read()
            for i, lock in enumerate(data["locks"]):
                if lock["id"] == lock_id:
                    removed = data["locks"].pop(i)
                    self._write(data)
                    return removed
            return None


def build_handler(config: ServerConfig):
    storage_root = config.storage_dir
    objects_root = storage_root / "objects"
    ensure_dir(objects_root)
    lock_store = LockStore(config.lock_db)

    class LfsHandler(BaseHTTPRequestHandler):
        server_version = "GitLFSLite/0.1"

        def _json_body(self) -> dict[str, Any]:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length) if length > 0 else b"{}"
            if not raw:
                return {}
            try:
                return json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                self._json_response(HTTPStatus.BAD_REQUEST, {"message": "invalid JSON"})
                return {}

        def _json_response(self, status: HTTPStatus, payload: dict[str, Any]) -> None:
            raw = json.dumps(payload, ensure_ascii=True).encode("utf-8")
            self.send_response(status.value)
            self.send_header("Content-Type", JSON_MIME)
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def _text_response(self, status: HTTPStatus, message: str) -> None:
            raw = message.encode("utf-8")
            self.send_response(status.value)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)

        def _unauthorized(self) -> None:
            self.send_response(HTTPStatus.UNAUTHORIZED.value)
            self.send_header("WWW-Authenticate", 'Basic realm="git-lfs-lite"')
            self.send_header("Content-Length", "0")
            self.end_headers()

        def _client_ip(self) -> ipaddress._BaseAddress | None:
            try:
                return ipaddress.ip_address(self.client_address[0])
            except ValueError:
                return None

        def _check_ip_allowed(self) -> bool:
            if not config.allow_networks:
                return True
            ip = self._client_ip()
            if ip is None:
                return False
            for network in config.allow_networks:
                if ip in network:
                    return True
            return False

        def _authorized_user(self) -> str | None:
            if config.auth_mode == "none":
                return "anonymous"
            header = self.headers.get("Authorization", "")
            if not header.startswith("Basic "):
                return None
            token = header[6:].strip()
            try:
                decoded = base64.b64decode(token).decode("utf-8")
            except Exception:
                return None
            if ":" not in decoded:
                return None
            user, password = decoded.split(":", 1)
            if user == config.basic_user and password == config.basic_pass:
                return user
            return None

        def _build_href(self, path_suffix: str) -> str:
            host = self.headers.get("X-Forwarded-Host") or self.headers.get("Host")
            proto = self.headers.get("X-Forwarded-Proto", "http")
            if not host:
                host = f"{config.host}:{config.port}"
            return f"{proto}://{host}{config.base_path}{path_suffix}"

        def _oid_path(self, oid: str) -> Path:
            return objects_root / oid[:2] / oid[2:4] / oid

        def _read_path_parts(self) -> tuple[str, list[str]]:
            parsed = urlsplit(self.path)
            path = parsed.path
            idx = path.find(config.base_path)
            if idx == -1:
                return "", []
            rel = path[idx + len(config.base_path) :]
            parts = [p for p in rel.split("/") if p]
            return parsed.query, parts

        def _validate_common(self) -> str | None:
            if not self._check_ip_allowed():
                self._text_response(HTTPStatus.FORBIDDEN, "IP not allowed")
                return None
            user = self._authorized_user()
            if user is None:
                self._unauthorized()
                return None
            return user

        def do_GET(self) -> None:
            user = self._validate_common()
            if user is None:
                return
            _, parts = self._read_path_parts()
            if len(parts) == 2 and parts[0] == "objects":
                self._download_object(parts[1])
                return
            if parts and parts[0] == "locks":
                self._locks_list()
                return
            self.send_error(HTTPStatus.NOT_FOUND.value)

        def do_POST(self) -> None:
            user = self._validate_common()
            if user is None:
                return
            _, parts = self._read_path_parts()
            if parts == ["objects", "batch"]:
                self._batch()
                return
            if len(parts) == 3 and parts[0] == "objects" and parts[2] == "verify":
                self._verify_object(parts[1])
                return
            if parts == ["locks"]:
                self._locks_create(user)
                return
            if parts == ["locks", "verify"]:
                self._locks_verify(user)
                return
            if len(parts) == 3 and parts[0] == "locks" and parts[2] == "unlock":
                self._locks_unlock(parts[1], user)
                return
            self.send_error(HTTPStatus.NOT_FOUND.value)

        def do_PUT(self) -> None:
            user = self._validate_common()
            if user is None:
                return
            _, parts = self._read_path_parts()
            if len(parts) == 2 and parts[0] == "objects":
                self._upload_object(parts[1])
                return
            self.send_error(HTTPStatus.NOT_FOUND.value)

        def _batch(self) -> None:
            body = self._json_body()
            if not body:
                return
            operation = body.get("operation")
            objects = body.get("objects")
            if operation not in {"upload", "download"} or not isinstance(objects, list):
                self._json_response(HTTPStatus.BAD_REQUEST, {"message": "invalid batch payload"})
                return
            response_objects = []
            for obj in objects:
                oid = obj.get("oid")
                size = obj.get("size")
                if not isinstance(oid, str) or not isinstance(size, int):
                    continue
                item: dict[str, Any] = {"oid": oid, "size": size}
                path = self._oid_path(oid)
                exists = path.exists()
                if operation == "upload":
                    if not exists:
                        item["actions"] = {
                            "upload": {
                                "href": self._build_href(f"/objects/{oid}"),
                                "header": {"Content-Type": "application/octet-stream"},
                            },
                            "verify": {
                                "href": self._build_href(f"/objects/{oid}/verify"),
                                "header": {"Content-Type": JSON_MIME},
                            },
                        }
                else:
                    if exists:
                        item["actions"] = {
                            "download": {
                                "href": self._build_href(f"/objects/{oid}"),
                                "header": {},
                            }
                        }
                    else:
                        item["error"] = {"code": 404, "message": "Object not found"}
                response_objects.append(item)
            self._json_response(
                HTTPStatus.OK,
                {
                    "transfer": "basic",
                    "objects": response_objects,
                    "hash_algo": "sha256",
                },
            )

        def _upload_object(self, oid: str) -> None:
            try:
                length = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._text_response(HTTPStatus.BAD_REQUEST, "Invalid Content-Length")
                return
            if length < 0:
                self._text_response(HTTPStatus.BAD_REQUEST, "Invalid Content-Length")
                return
            dst = self._oid_path(oid)
            ensure_dir(dst.parent)
            tmp = dst.with_suffix(".uploading")
            h = hashlib.sha256()
            remaining = length
            with tmp.open("wb") as f:
                while remaining > 0:
                    chunk = self.rfile.read(min(1024 * 1024, remaining))
                    if not chunk:
                        break
                    f.write(chunk)
                    h.update(chunk)
                    remaining -= len(chunk)
            if remaining != 0:
                if tmp.exists():
                    tmp.unlink()
                self._text_response(HTTPStatus.BAD_REQUEST, "Incomplete upload body")
                return
            digest = h.hexdigest()
            if digest != oid:
                if tmp.exists():
                    tmp.unlink()
                self._text_response(HTTPStatus.UNPROCESSABLE_ENTITY, "OID mismatch")
                return
            tmp.replace(dst)
            self.send_response(HTTPStatus.OK.value)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def _download_object(self, oid: str) -> None:
            src = self._oid_path(oid)
            if not src.exists():
                self.send_error(HTTPStatus.NOT_FOUND.value)
                return
            size = src.stat().st_size
            self.send_response(HTTPStatus.OK.value)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", str(size))
            self.end_headers()
            with src.open("rb") as f:
                while True:
                    chunk = f.read(1024 * 1024)
                    if not chunk:
                        break
                    self.wfile.write(chunk)

        def _verify_object(self, oid: str) -> None:
            body = self._json_body()
            if not body:
                return
            claimed_oid = body.get("oid")
            claimed_size = body.get("size")
            if claimed_oid != oid or not isinstance(claimed_size, int):
                self._json_response(HTTPStatus.BAD_REQUEST, {"message": "invalid verify payload"})
                return
            path = self._oid_path(oid)
            if not path.exists():
                self._json_response(HTTPStatus.NOT_FOUND, {"message": "object not found"})
                return
            if path.stat().st_size != claimed_size:
                self._json_response(HTTPStatus.UNPROCESSABLE_ENTITY, {"message": "size mismatch"})
                return
            self.send_response(HTTPStatus.OK.value)
            self.send_header("Content-Length", "0")
            self.end_headers()

        def _locks_create(self, user: str) -> None:
            body = self._json_body()
            if not body:
                return
            path = body.get("path")
            if not isinstance(path, str) or not path:
                self._json_response(HTTPStatus.BAD_REQUEST, {"message": "path is required"})
                return
            ok, lock = lock_store.create_lock(path, user)
            if ok:
                self._json_response(HTTPStatus.CREATED, {"lock": lock})
                return
            self._json_response(HTTPStatus.CONFLICT, {"message": "lock already exists", "lock": lock})

        def _locks_list(self) -> None:
            q = parse_qs(urlsplit(self.path).query)
            path = q.get("path", [None])[0]
            lock_id = q.get("id", [None])[0]
            cursor = q.get("cursor", [None])[0]
            limit = int(q.get("limit", ["100"])[0])
            locks, next_cursor = lock_store.list_locks(path, lock_id, cursor, max(1, min(limit, 1000)))
            payload: dict[str, Any] = {"locks": locks}
            if next_cursor:
                payload["next_cursor"] = next_cursor
            self._json_response(HTTPStatus.OK, payload)

        def _locks_verify(self, user: str) -> None:
            body = self._json_body()
            if not isinstance(body, dict):
                self._json_response(HTTPStatus.BAD_REQUEST, {"message": "invalid JSON"})
                return
            cursor = body.get("cursor")
            limit = body.get("limit", 100)
            if not isinstance(limit, int):
                self._json_response(HTTPStatus.BAD_REQUEST, {"message": "limit must be int"})
                return
            ours, theirs, next_cursor = lock_store.verify_locks(user, cursor, max(1, min(limit, 1000)))
            payload: dict[str, Any] = {"ours": ours, "theirs": theirs}
            if next_cursor:
                payload["next_cursor"] = next_cursor
            self._json_response(HTTPStatus.OK, payload)

        def _locks_unlock(self, lock_id: str, user: str) -> None:
            body = self._json_body()
            if not isinstance(body, dict):
                self._json_response(HTTPStatus.BAD_REQUEST, {"message": "invalid JSON"})
                return
            force = bool(body.get("force", False))
            lock = lock_store.find_lock(lock_id)
            if lock is None:
                self._json_response(HTTPStatus.NOT_FOUND, {"message": "lock not found"})
                return
            owner = lock.get("owner", {}).get("name")
            if owner != user and not force:
                self._json_response(HTTPStatus.FORBIDDEN, {"message": "lock held by another user", "lock": lock})
                return
            removed = lock_store.delete_lock(lock_id)
            self._json_response(HTTPStatus.OK, {"lock": removed})

        def log_message(self, fmt: str, *args: Any) -> None:
            now = dt.datetime.now().isoformat(timespec="seconds")
            print(f"[{now}] {self.client_address[0]} {fmt % args}")

    return LfsHandler


def parse_networks(raw_networks: list[str]) -> list[ipaddress._BaseNetwork]:
    networks = []
    for n in raw_networks:
        n = n.strip()
        if not n:
            continue
        networks.append(ipaddress.ip_network(n, strict=False))
    return networks


def normalize_base_path(path: str) -> str:
    if not path.startswith("/"):
        path = "/" + path
    return path.rstrip("/") or DEFAULT_BASE


def build_config() -> ServerConfig:
    parser = argparse.ArgumentParser(description="Minimal Git LFS server with optional Basic auth and IP filtering.")
    parser.add_argument("--host", default=os.getenv("LFS_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.getenv("LFS_PORT", "8080")))
    parser.add_argument("--base-path", default=os.getenv("LFS_BASE_PATH", DEFAULT_BASE))
    parser.add_argument("--storage-dir", default=os.getenv("LFS_STORAGE_DIR", "./data"))
    parser.add_argument("--auth-mode", choices=["none", "basic"], default=os.getenv("LFS_AUTH_MODE", "none"))
    parser.add_argument("--basic-user", default=os.getenv("LFS_BASIC_USER", ""))
    parser.add_argument("--basic-pass", default=os.getenv("LFS_BASIC_PASS", ""))
    parser.add_argument(
        "--allow-net",
        action="append",
        default=[],
        help="Allowed source network (CIDR). Can be used multiple times.",
    )
    parser.add_argument(
        "--allow-nets",
        default=os.getenv("LFS_ALLOW_NETS", ""),
        help="Comma-separated allowed CIDRs (e.g. 10.0.0.0/8,192.168.0.0/16).",
    )
    args = parser.parse_args()

    if args.auth_mode == "basic" and (not args.basic_user or not args.basic_pass):
        parser.error("--auth-mode basic requires --basic-user and --basic-pass")

    combined_nets = list(args.allow_net)
    if args.allow_nets:
        combined_nets.extend([v.strip() for v in args.allow_nets.split(",") if v.strip()])
    networks = parse_networks(combined_nets)

    storage_dir = Path(args.storage_dir).resolve()
    ensure_dir(storage_dir)
    return ServerConfig(
        host=args.host,
        port=args.port,
        base_path=normalize_base_path(args.base_path),
        storage_dir=storage_dir,
        lock_db=storage_dir / "locks.json",
        auth_mode=args.auth_mode,
        basic_user=args.basic_user,
        basic_pass=args.basic_pass,
        allow_networks=networks,
    )


def main() -> None:
    config = build_config()
    handler = build_handler(config)
    server = ThreadingHTTPServer((config.host, config.port), handler)
    nets = ", ".join(str(n) for n in config.allow_networks) if config.allow_networks else "all"
    print(f"Serving Git LFS on http://{config.host}:{config.port}{config.base_path}")
    print(f"Auth mode: {config.auth_mode}")
    print(f"Allowed networks: {nets}")
    print(f"Storage: {config.storage_dir}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()

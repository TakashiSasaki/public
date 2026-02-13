import sqlite3
import json
import logging
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Any, Optional
from platformdirs import PlatformDirs

from .identifiers import APP_NAMESPACE_UUID

logger = logging.getLogger(__name__)

class AppDataStorage:
    _instance: Optional["AppDataStorage"] = None
    
    # Use first 32 bits of APP_NAMESPACE_UUID (c31a2332-...) as Application ID
    # 0xc31a2332 = 3273204530
    APPLICATION_ID = int(APP_NAMESPACE_UUID.hex[:8], 16)
    CURRENT_DB_VERSION = 1

    def __init__(self, db_name: str = "app_data.db", app_name: str = "get-a-grip", app_author: str = "takas"):
        # OS固有のデータディレクトリを取得 (Windows: AppData/Local/...)
        dirs = PlatformDirs(app_name, app_author, roaming=False)
        self.db_dir = Path(dirs.user_data_dir)
        self.db_path = self.db_dir / db_name

        # ディレクトリが存在しない場合は作成
        self.db_dir.mkdir(parents=True, exist_ok=True)
        
        # SQLite接続の初期化
        # check_same_thread=False: 複数のスレッド(GUI/TUI)からのアクセスを許可
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        self._initialize_db()

    @classmethod
    def get_instance(cls) -> "AppDataStorage":
        """シングルトンインスタンスを取得"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def _initialize_db(self):
        """データベースの初期化とマイグレーションを実行"""
        # アプリケーションIDのチェック (ファイルの識別)
        cur = self.conn.execute("PRAGMA application_id")
        app_id = cur.fetchone()[0]

        if app_id == 0:
            # 新規DB または 未設定の場合: IDを設定
            self.conn.execute(f"PRAGMA application_id = {self.APPLICATION_ID}")
        elif app_id != self.APPLICATION_ID:
            # 異なるアプリのDBファイルである可能性があるためエラーにする
            raise ValueError(f"Invalid database application_id: {app_id} (Expected: {self.APPLICATION_ID})")

        # スキーマバージョンのチェック (PRAGMA user_version)
        cur = self.conn.execute("PRAGMA user_version")
        current_version = cur.fetchone()[0]

        if current_version < self.CURRENT_DB_VERSION:
            self._migrate_db(current_version)

    def _migrate_db(self, current_version: int):
        """
        データベースのマイグレーションを実行
        
        Args:
            current_version (int): 現在のDBバージョン
        """
        logger.info(f"Migrating database from version {current_version} to {self.CURRENT_DB_VERSION}")

        try:
            with self.conn:
                # Version 0 -> 1: 初回作成 (テーブル作成)
                if current_version < 1:
                    self._create_tables_v1()
                
                # 将来的なマイグレーション例:
                # if current_version < 2:
                #     self._migrate_v1_to_v2()

                # マイグレーション完了後、バージョン情報を更新 (PRAGMA user_version)
                self.conn.execute(f"PRAGMA user_version = {self.CURRENT_DB_VERSION}")
                
            logger.info(f"Database migration to version {self.CURRENT_DB_VERSION} completed successfully.")
        except Exception as e:
            logger.error(f"Database migration failed: {e}")
            raise

    def _create_tables_v1(self):
        """バージョン1のテーブル構造を作成"""
        # 設定テーブル (Settings)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # キャッシュテーブル (Cache)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS cache (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                expires_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # インデックスによる検索高速化
        self.conn.execute("CREATE INDEX IF NOT EXISTS idx_cache_expires ON cache (expires_at)")

    def close(self):
        """データベース接続を閉じる"""
        if self.conn:
            self.conn.close()

    # --- Settings Methods (永続的設定) ---

    def set(self, key: str, value: Any) -> None:
        """設定値を保存 (JSONシリアライズ)"""
        json_value = json.dumps(value)
        with self.conn:
            self.conn.execute("""
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, ?)
            """, (key, json_value, datetime.now(timezone.utc)))

    def get(self, key: str, default: Any = None) -> Any:
        """設定値を取得 (存在しない場合は default を返す)"""
        cursor = self.conn.execute("SELECT value FROM settings WHERE key = ?", (key,))
        row = cursor.fetchone()
        if row:
            try:
                return json.loads(row["value"])
            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON for setting key: {key}")
                return default
        return default

    def delete(self, key: str) -> None:
        """設定値を削除"""
        with self.conn:
            self.conn.execute("DELETE FROM settings WHERE key = ?", (key,))

    # --- Cache Methods (一時的データ) ---

    def cache_set(self, key: str, value: Any, ttl: float = None) -> None:
        """
        キャッシュを保存
        
        Args:
            key (str): キャッシュキー
            value (Any): 保存する値 (JSONシリアライズ可能なオブジェクト)
            ttl (float, optional): 有効期限 (秒)。指定しない場合は無期限。
        """
        json_value = json.dumps(value)
        expires_at = None
        if ttl is not None:
            expires_at = datetime.now(timezone.utc) + timedelta(seconds=ttl)

        with self.conn:
            self.conn.execute("""
                INSERT OR REPLACE INTO cache (key, value, expires_at, created_at)
                VALUES (?, ?, ?, ?)
            """, (key, json_value, expires_at, datetime.now(timezone.utc)))

    def cache_get(self, key: str, default: Any = None) -> Any:
        """
        有効なキャッシュを取得
        
        有効期限切れのデータは取得されず、クリーンアップの対象になります。
        """
        now = datetime.now(timezone.utc)
        cursor = self.conn.execute("""
            SELECT value, expires_at FROM cache WHERE key = ?
        """, (key,))
        row = cursor.fetchone()

        if row:
            # 期限切れチェック (expires_at が NULL なら無期限)
            expires_at_str = row["expires_at"]
            if expires_at_str:
                # SQLiteのTIMESTAMP型は文字列で返ってくる場合があるためパース
                # (アダプタの設定によるが、念のため安全策)
                try:
                    expires_at = datetime.fromisoformat(expires_at_str)
                    # タイムゾーン情報がない場合はUTCとして扱う
                    if expires_at.tzinfo is None:
                        expires_at = expires_at.replace(tzinfo=timezone.utc)
                    
                    if expires_at < now:
                        # 期限切れ
                        self.delete_cache(key)  # Lazy expiration: 取得時に消す
                        return default
                except ValueError:
                    logger.warning(f"Invalid timestamp format in cache for key: {key}")
            
            try:
                return json.loads(row["value"])
            except json.JSONDecodeError:
                return default

        return default

    def delete_cache(self, key: str) -> None:
        """キャッシュを削除"""
        with self.conn:
            self.conn.execute("DELETE FROM cache WHERE key = ?", (key,))

    def prune_cache(self) -> int:
        """
        期限切れのキャッシュを一括削除
        
        Returns:
            int: 削除されたレコード数
        """
        now = datetime.now(timezone.utc)
        with self.conn as conn:
            cursor = conn.execute("DELETE FROM cache WHERE expires_at < ?", (now,))
            deleted_count = cursor.rowcount
            return deleted_count

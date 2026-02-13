import pytest
import sqlite3
import json
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock
from get_a_grip.storage import AppDataStorage

@pytest.fixture
def mock_storage(tmp_path):
    """
    AppDataStorageのインスタンスを作成するフィクスチャ。
    platformdirsをパッチしてtmp_pathを使用するようにする。
    """
    AppDataStorage._instance = None
    with patch("get_a_grip.storage.PlatformDirs") as mock_dirs:
        mock_dirs.return_value.user_data_dir = str(tmp_path)
        storage = AppDataStorage(db_name="test.db")
        yield storage
        storage.close()
    AppDataStorage._instance = None

def test_singleton(tmp_path):
    """シングルトンパターンのテスト"""
    AppDataStorage._instance = None
    with patch("get_a_grip.storage.PlatformDirs") as mock_dirs:
        mock_dirs.return_value.user_data_dir = str(tmp_path)
        s1 = AppDataStorage.get_instance()
        s2 = AppDataStorage.get_instance()
        assert s1 is s2
    AppDataStorage._instance = None

def test_initialization(mock_storage):
    """初期化、application_idおよびuser_versionのテスト"""
    conn = mock_storage.conn
    
    # application_idの確認
    cur = conn.execute("PRAGMA application_id")
    app_id = cur.fetchone()[0]
    expected_id = mock_storage.APPLICATION_ID
    # SQLite PRAGMA returns signed 32-bit
    signed_expected = expected_id & 0xFFFFFFFF
    if signed_expected > 0x7FFFFFFF:
        signed_expected -= 0x100000000
    assert app_id == signed_expected
    
    # user_versionの確認
    cur = conn.execute("PRAGMA user_version")
    version = cur.fetchone()[0]
    assert version == mock_storage.CURRENT_DB_VERSION

def test_settings_basic(mock_storage):
    """基本的な設定の保存と取得のテスト"""
    mock_storage.set("string_key", "hello")
    mock_storage.set("int_key", 123)
    mock_storage.set("float_key", 45.6)
    mock_storage.set("bool_key", True)
    mock_storage.set("none_key", None)
    
    assert mock_storage.get("string_key") == "hello"
    assert mock_storage.get("int_key") == 123
    assert mock_storage.get("float_key") == 45.6
    assert mock_storage.get("bool_key") is True
    assert mock_storage.get("none_key") is None
    assert mock_storage.get("missing_key", "default") == "default"

def test_settings_nested(mock_storage):
    """ネストされた構造（dict, list）のテスト"""
    data = {
        "user": "takas",
        "scores": [10, 20, 30],
        "meta": {"active": True}
    }
    mock_storage.set("app_state", data)
    retrieved = mock_storage.get("app_state")
    assert retrieved == data
    assert retrieved["scores"][1] == 20

def test_settings_delete(mock_storage):
    """設定の削除テスト"""
    mock_storage.set("temp", "value")
    assert mock_storage.get("temp") == "value"
    mock_storage.delete("temp")
    assert mock_storage.get("temp") is None

def test_cache_basic(mock_storage):
    """キャッシュの基本的な保存と取得のテスト"""
    mock_storage.cache_set("c1", "cached_value")
    assert mock_storage.cache_get("c1") == "cached_value"
    
    mock_storage.cache_set("c2", {"a": 1})
    assert mock_storage.cache_get("c2") == {"a": 1}

def test_cache_expiration(mock_storage):
    """キャッシュの有効期限のテスト"""
    # 1秒のTTL
    mock_storage.cache_set("short_lived", "data", ttl=1)
    assert mock_storage.cache_get("short_lived") == "data"
    
    # タイムスタンプを直接操作して期限を過去にする
    with mock_storage.conn:
        past_time = datetime.now(timezone.utc) - timedelta(seconds=10)
        mock_storage.conn.execute(
            "UPDATE cache SET expires_at = ? WHERE key = ?",
            (past_time.isoformat(), "short_lived")
        )
    
    # 期限切れのためNoneが返るはず
    assert mock_storage.cache_get("short_lived") is None

def test_prune_cache(mock_storage):
    """期限切れキャッシュの一括削除のテスト"""
    mock_storage.cache_set("valid", "ok", ttl=3600)
    mock_storage.cache_set("expired", "fail", ttl=1)
    
    # expiredの方を過去にする
    with mock_storage.conn:
        past_time = datetime.now(timezone.utc) - timedelta(seconds=10)
        mock_storage.conn.execute(
            "UPDATE cache SET expires_at = ? WHERE key = ?",
            (past_time, "expired")
        )
        
    deleted_count = mock_storage.prune_cache()
    # Note: Depending on SQLite version and adapters, this might still be tricky.
    # If it fails, it means the storage.py implementation itself might need more robust timestamp handling.
    assert deleted_count == 1
    assert mock_storage.cache_get("valid") == "ok"
    
    # 実際のテーブルを直接確認
    cursor = mock_storage.conn.execute("SELECT count(*) FROM cache WHERE key = 'expired'")
    assert cursor.fetchone()[0] == 0

def test_invalid_application_id(tmp_path):
    """異なるApplication IDを持つDBファイルに対するエラーのテスト"""
    db_path = tmp_path / "alien.db"
    
    # 別のIDで先に作成
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA application_id = 12345678")
    conn.commit()
    conn.close()
    
    AppDataStorage._instance = None
    with patch("get_a_grip.storage.PlatformDirs") as mock_dirs:
        mock_dirs.return_value.user_data_dir = str(tmp_path)
        with pytest.raises(ValueError, match="Invalid database application_id"):
            AppDataStorage(db_name="alien.db")

def test_json_decode_error(mock_storage, caplog):
    """不正なJSONデータがDBに入っている場合のハンドリング"""
    # 直接不正な文字列を入れる
    with mock_storage.conn:
        mock_storage.conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?)",
            ("bad_json", "{not_a_json}")
        )
    
    assert mock_storage.get("bad_json", "fallback") == "fallback"
    assert "Failed to decode JSON" in caplog.text

def test_cache_delete(mock_storage):
    """キャッシュ削除のテスト"""
    mock_storage.cache_set("to_delete", "val")
    assert mock_storage.cache_get("to_delete") == "val"
    mock_storage.delete_cache("to_delete")
    assert mock_storage.cache_get("to_delete") is None

def test_reinitialization_success(tmp_path):
    """既存の正しいDBファイルでの再初期化テスト"""
    AppDataStorage._instance = None
    with patch("get_a_grip.storage.PlatformDirs") as mock_dirs:
        mock_dirs.return_value.user_data_dir = str(tmp_path)
        
        # 1回目: 新規作成
        s1 = AppDataStorage(db_name="reuse.db")
        s1.set("key", "value")
        s1.close()
        
        # 2回目: 既存ファイルを読み込み
        s2 = AppDataStorage(db_name="reuse.db")
        assert s2.get("key") == "value"
        s2.close()

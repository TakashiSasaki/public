import uuid

# アプリケーション全体で使用する名前空間UUID
# 2026-02-13 13:24:00 (JST) に以下のコマンドで生成:
#   python -c "import uuid; print(uuid.uuid4())"
#   => c31a2332-47da-4ecf-a93a-80880c593533
# アプリケーションの再配布先などで一意の値となるよう、この値は固定で使用します。
APP_NAMESPACE_UUID: uuid.UUID = uuid.UUID("c31a2332-47da-4ecf-a93a-80880c593533")

def generate_id_v5(name: str) -> uuid.UUID:
    """
    アプリケーション固有の名前空間を使用して、指定された名前に対するUUID v5を生成します。
    
    これにより、同じ名前からは常に同じUUIDが生成されますが、
    他のアプリケーションのUUIDと衝突することはありません。

    Args:
        name (str): 識別子の元となる文字列（ファイルパス、ユーザーID、設定キーなど）
        
    Returns:
        uuid.UUID: 生成されたUUID v5
    """
    return uuid.uuid5(APP_NAMESPACE_UUID, name)

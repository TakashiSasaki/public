from typing import List, Dict, Any

"""
cursor_roles.py
Windows の標準カーソルロール定義。

各エントリは以下のキーを持つ dict:
    name         : ロールの表示名（日本語）
    filename     : 出力する .cur ファイル名
    registry_key : レジストリキー名（参考情報）
    shape        : ベースのカーソル形状
    use_overlays : 現在の SVG ベース/バッジ設定を適用するか
"""

CURSOR_ROLES: List[Dict[str, Any]] = [
    {"name": "通常選択", "filename": "arrow.cur", "registry_key": "Arrow", "shape": "arrow", "use_overlays": True},
    {"name": "ヘルプ選択", "filename": "help.cur", "registry_key": "Help", "shape": "arrow", "use_overlays": True},
    {"name": "バックグラウンドで作業中", "filename": "appstarting.cur", "registry_key": "AppStarting", "shape": "arrow", "use_overlays": True},
    {"name": "ビジー", "filename": "wait.cur", "registry_key": "Wait", "shape": "hourglass", "use_overlays": False},
    {"name": "精度選択", "filename": "crosshair.cur", "registry_key": "Crosshair", "shape": "cross", "use_overlays": False},
    {"name": "テキスト選択", "filename": "ibeam.cur", "registry_key": "IBeam", "shape": "ibeam", "use_overlays": False},
    {"name": "手書き (ペン)", "filename": "pen.cur", "registry_key": "Pen", "shape": "arrow", "use_overlays": True},
    {"name": "利用不可", "filename": "no.cur", "registry_key": "No", "shape": "arrow", "use_overlays": True},
    {"name": "垂直サイズ変更", "filename": "sizens.cur", "registry_key": "SizeNS", "shape": "arrow", "use_overlays": True},
    {"name": "水平サイズ変更", "filename": "sizewe.cur", "registry_key": "SizeWE", "shape": "arrow", "use_overlays": True},
    {"name": "斜めサイズ変更 1 (NW-SE)", "filename": "sizenwse.cur", "registry_key": "SizeNWSE", "shape": "arrow", "use_overlays": True},
    {"name": "斜めサイズ変更 2 (NE-SW)", "filename": "sizenesw.cur", "registry_key": "SizeNESW", "shape": "arrow", "use_overlays": True},
    {"name": "移動", "filename": "sizeall.cur", "registry_key": "SizeAll", "shape": "cross", "use_overlays": False},
    {"name": "代替選択", "filename": "uparrow.cur", "registry_key": "UpArrow", "shape": "triangle", "use_overlays": False},
    {"name": "リンク選択", "filename": "hand.cur", "registry_key": "Hand", "shape": "hand", "use_overlays": False},
    {"name": "場所の選択", "filename": "pin.cur", "registry_key": "Pin", "shape": "arrow", "use_overlays": True},
    {"name": "人の選択", "filename": "person.cur", "registry_key": "Person", "shape": "arrow", "use_overlays": True},
]

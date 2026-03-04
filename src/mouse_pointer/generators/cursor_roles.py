from typing import List, Dict, Any

"""
cursor_roles.py
Windows の標準カーソルロール (17種類) の定義。

各エントリは以下のキーを持つ dict:
    name        : ロールの表示名（日本語）
    filename    : 出力する .cur ファイル名
    registry_key: レジストリキー名（参考情報）
    label_mr    : 右中央コーナーに描画する識別ラベル（空文字 = なし）
"""

CURSOR_ROLES: List[Dict[str, Any]] = [
    {
        "name": "通常選択",
        "filename": "arrow.cur",
        "registry_key": "Arrow",
        "label_mr": "",
    },
    {
        "name": "ヘルプ選択",
        "filename": "help.cur",
        "registry_key": "Help",
        "label_mr": "?",
    },
    {
        "name": "バックグラウンドで作業中",
        "filename": "appstarting.cur",
        "registry_key": "AppStarting",
        "label_mr": "…",
    },
    {
        "name": "ビジー",
        "filename": "wait.cur",
        "registry_key": "Wait",
        "label_mr": "⌛",
    },
    {
        "name": "精度選択",
        "filename": "crosshair.cur",
        "registry_key": "Crosshair",
        "label_mr": "+",
    },
    {
        "name": "テキスト選択",
        "filename": "ibeam.cur",
        "registry_key": "IBeam",
        "label_mr": "I",
    },
    {
        "name": "手書き (ペン)",
        "filename": "pen.cur",
        "registry_key": "Pen",
        "label_mr": "✏",
    },
    {
        "name": "利用不可",
        "filename": "no.cur",
        "registry_key": "No",
        "label_mr": "⊘",
    },
    {
        "name": "垂直サイズ変更",
        "filename": "sizens.cur",
        "registry_key": "SizeNS",
        "label_mr": "↕",
    },
    {
        "name": "水平サイズ変更",
        "filename": "sizewe.cur",
        "registry_key": "SizeWE",
        "label_mr": "↔",
    },
    {
        "name": "斜めサイズ変更 1 (NW-SE)",
        "filename": "sizenwse.cur",
        "registry_key": "SizeNWSE",
        "label_mr": "↘",
    },
    {
        "name": "斜めサイズ変更 2 (NE-SW)",
        "filename": "sizenesw.cur",
        "registry_key": "SizeNESW",
        "label_mr": "↙",
    },
    {
        "name": "移動",
        "filename": "sizeall.cur",
        "registry_key": "SizeAll",
        "label_mr": "✥",
    },
    {
        "name": "代替選択",
        "filename": "uparrow.cur",
        "registry_key": "UpArrow",
        "label_mr": "↑",
    },
    {
        "name": "リンク選択",
        "filename": "hand.cur",
        "registry_key": "Hand",
        "label_mr": "🔗",
    },
    {
        "name": "場所の選択",
        "filename": "pin.cur",
        "registry_key": "Pin",
        "label_mr": "📍",
    },
    {
        "name": "人の選択",
        "filename": "person.cur",
        "registry_key": "Person",
        "label_mr": "👤",
    },
]

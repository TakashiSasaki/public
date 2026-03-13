from typing import List, Dict, Any

"""
cursor_roles.py
Windows の標準カーソルロール定義。

各エントリは以下のキーを持つ dict:
    name         : ロールの表示名（日本語）
    filename     : 出力する .cur ファイル名
    registry_key : レジストリキー名（参考情報）
    shape        : ベースのカーソル形状
    tr_text      : 右上テキストの既定値
    mr_text      : 右中央テキストの既定値
    caption_text : キャプションの既定値
    use_overlays : 現在の SVG ベース/バッジ設定を適用するか
"""

CURSOR_ROLES: List[Dict[str, Any]] = [
    {"name": "通常選択", "filename": "arrow.cur", "registry_key": "Arrow", "shape": "arrow", "tr_text": "", "mr_text": "", "caption_text": "", "use_overlays": True},
    {"name": "ヘルプ選択", "filename": "help.cur", "registry_key": "Help", "shape": "arrow", "tr_text": "?", "mr_text": "", "caption_text": "", "use_overlays": True},
    {"name": "バックグラウンドで作業中", "filename": "appstarting.cur", "registry_key": "AppStarting", "shape": "arrow", "tr_text": "", "mr_text": "...", "caption_text": "", "use_overlays": True},
    {"name": "ビジー", "filename": "wait.cur", "registry_key": "Wait", "shape": "hourglass", "tr_text": "", "mr_text": "", "caption_text": "", "use_overlays": False},
    {"name": "精度選択", "filename": "crosshair.cur", "registry_key": "Crosshair", "shape": "cross", "tr_text": "", "mr_text": "", "caption_text": "", "use_overlays": False},
    {"name": "テキスト選択", "filename": "ibeam.cur", "registry_key": "IBeam", "shape": "ibeam", "tr_text": "", "mr_text": "", "caption_text": "", "use_overlays": False},
    {"name": "手書き (ペン)", "filename": "pen.cur", "registry_key": "Pen", "shape": "arrow", "tr_text": "", "mr_text": "pen", "caption_text": "", "use_overlays": True},
    {"name": "利用不可", "filename": "no.cur", "registry_key": "No", "shape": "arrow", "tr_text": "", "mr_text": "no", "caption_text": "", "use_overlays": True},
    {"name": "垂直サイズ変更", "filename": "sizens.cur", "registry_key": "SizeNS", "shape": "arrow", "tr_text": "", "mr_text": "NS", "caption_text": "", "use_overlays": True},
    {"name": "水平サイズ変更", "filename": "sizewe.cur", "registry_key": "SizeWE", "shape": "arrow", "tr_text": "", "mr_text": "WE", "caption_text": "", "use_overlays": True},
    {"name": "斜めサイズ変更 1 (NW-SE)", "filename": "sizenwse.cur", "registry_key": "SizeNWSE", "shape": "arrow", "tr_text": "", "mr_text": "NW", "caption_text": "", "use_overlays": True},
    {"name": "斜めサイズ変更 2 (NE-SW)", "filename": "sizenesw.cur", "registry_key": "SizeNESW", "shape": "arrow", "tr_text": "", "mr_text": "NE", "caption_text": "", "use_overlays": True},
    {"name": "移動", "filename": "sizeall.cur", "registry_key": "SizeAll", "shape": "cross", "tr_text": "", "mr_text": "all", "caption_text": "", "use_overlays": False},
    {"name": "代替選択", "filename": "uparrow.cur", "registry_key": "UpArrow", "shape": "triangle", "tr_text": "", "mr_text": "", "caption_text": "", "use_overlays": False},
    {"name": "リンク選択", "filename": "hand.cur", "registry_key": "Hand", "shape": "hand", "tr_text": "", "mr_text": "", "caption_text": "", "use_overlays": False},
    {"name": "場所の選択", "filename": "pin.cur", "registry_key": "Pin", "shape": "arrow", "tr_text": "", "mr_text": "pin", "caption_text": "", "use_overlays": True},
    {"name": "人の選択", "filename": "person.cur", "registry_key": "Person", "shape": "arrow", "tr_text": "", "mr_text": "usr", "caption_text": "", "use_overlays": True},
]

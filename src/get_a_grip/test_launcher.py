import pytest
import os
import sys

def main():
    # このファイル (src/get_a_grip/test_launcher.py) からプロジェクトルートを特定
    # src/get_a_grip/test_launcher.py -> src/get_a_grip -> src -> project_root
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 作業ディレクトリをプロジェクトルートに変更
    os.chdir(root)
    
    # pytestを実行 (sys.argv[1:]でコマンドライン引数も引き継ぐ)
    sys.exit(pytest.main(sys.argv[1:]))

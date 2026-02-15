import subprocess

def get_event_logs(log_name="System", newest=5):
    """
    PowerShellのGet-WinEventを使用してイベントログを取得します。
    """
    # PowerShellコマンドの構築
    command = [
        "powershell",
        "-Command",
        f"Get-WinEvent -LogName {log_name} -MaxEvents {newest} | Select-Object TimeCreated, Id, LevelDisplayName, Message | Format-List"
    ]
    
    try:
        # 多くのWindows環境でのエンコーディング問題を避けるため、cp932(Shift-JIS)を試行し、失敗したらutf-8
        try:
            result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='cp932')
        except UnicodeDecodeError:
            result = subprocess.run(command, capture_output=True, text=True, check=True, encoding='utf-8')
            
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.stderr}"

if __name__ == "__main__":
    log_name = "System"
    max_events = 5
    print(f"--- '{log_name}' ログの最新 {max_events} 件を取得中 ---")
    output = get_event_logs(log_name, max_events)
    print(output)

import win32evtlog
import win32evtlogutil
import win32con
from typing import List, Dict, Any
from get_a_grip.storage import AppDataStorage

class EventLogCore:
    @staticmethod
    def get_event_type_str(event_type: int) -> str:
        """イベントタイプの数値を文字列に変換します。"""
        types = {
            win32con.EVENTLOG_AUDIT_FAILURE: "AUDIT_FAILURE",
            win32con.EVENTLOG_AUDIT_SUCCESS: "AUDIT_SUCCESS",
            win32con.EVENTLOG_ERROR_TYPE: "ERROR",
            win32con.EVENTLOG_INFORMATION_TYPE: "INFORMATION",
            win32con.EVENTLOG_WARNING_TYPE: "WARNING",
        }
        return types.get(event_type, f"Unknown ({event_type})")

    @staticmethod
    def fetch_logs(log_name: str = "System", limit: int = 100) -> List[Dict[str, Any]]:
        """
        Windows Event Logからログを取得します。
        
        Args:
            log_name (str): ログの名前 (System, Application等)
            limit (int): 取得する最大件数
            
        Returns:
            List[Dict[str, Any]]: 取得したログのリスト
        """
        logs = []
        try:
            handle = win32evtlog.OpenEventLog(None, log_name)
            flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
            
            # ReadEventLogは一度に全てのログを返すわけではないので、ループで取得する必要があるが、
            # ここではシンプルに一度の呼び出しで取得できる分だけ処理し、limitまで繰り返す実装にするか、
            # あるいはAPIの仕様上、オフセットを指定して読み込む。
            # 今回は既存の実装をベースに、limit件数に達するまで読み込む形にする。
            
            while len(logs) < limit:
                events = win32evtlog.ReadEventLog(handle, flags, 0)
                if not events:
                    break
                    
                for event in events:
                    if len(logs) >= limit:
                        break
                        
                    # メッセージのデコード
                    try:
                        message = win32evtlogutil.SafeFormatMessage(event, log_name)
                    except Exception:
                        message = " ".join(event.StringInserts) if event.StringInserts else ""
                        
                    logs.append({
                        "record_number": event.RecordNumber,
                        "event_id": event.EventID & 0x0000FFFF,
                        "event_type": EventLogCore.get_event_type_str(event.EventType),
                        "source_name": event.SourceName,
                        "time_generated": event.TimeGenerated.Format(), 
                        # TimeGeneratedは本来 datetime オブジェクトだが、Format()で文字列にしている。
                        # DB保存時は文字列の方が都合が良い場合もあるが、datetimeオブジェクトのままの方が扱いやすい場合もある。
                        # 既存実装に合わせて Format() した文字列とする。
                        "message": message.strip()
                    })

            win32evtlog.CloseEventLog(handle)
        except Exception as e:
            # エラー処理は呼び出し元に任せるか、ここでログ出力するか。
            # ここでは例外を再送出する。
            raise e
            
        return logs

    @staticmethod
    def save_logs(log_name: str, logs: List[Dict[str, Any]]) -> None:
        """
        取得したログをストレージに保存します。
        
        Args:
            log_name (str): ログの名前
            logs (List[Dict[str, Any]]): 保存するログのリスト
        """
        storage = AppDataStorage.get_instance()
        storage.store_event_logs(log_name, logs)

    @staticmethod
    def get_available_logs() -> List[str]:
        """利用可能なイベントログの一覧を取得します"""
        logs = []
        try:
            import win32api
            # win32con is already imported
            
            flags = win32con.KEY_READ
            # レジストリからイベントログのリストを取得
            path = "SYSTEM\\CurrentControlSet\\Services\\EventLog"
            hkey = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, path, 0, flags)
            
            try:
                num = win32api.RegQueryInfoKey(hkey)[0]
                for i in range(num):
                    name = win32api.RegEnumKey(hkey, i)
                    logs.append(name)
            finally:
                win32api.RegCloseKey(hkey)
                
            # 一般的なログを先頭に持ってくる
            priority = ["System", "Application", "Security"]
            for p in reversed(priority):
                if p in logs:
                    logs.remove(p)
                    logs.insert(0, p)
                    
        except Exception as e:
            # フォールバック
            if not logs:
                logs = ["System", "Application", "Security"]
            print(f"Error listing logs: {e}")
            
        return logs

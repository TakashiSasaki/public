import win32evtlog

def list_event_logs():
    server = None # Local machine
    source_type = "EventLog"
    
    try:
        # accessing the registry is the standard way to find event logs for the old API
        import win32api
        import win32con
        
        flags = win32con.KEY_READ
        hkey = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, "SYSTEM\\CurrentControlSet\\Services\\EventLog", 0, flags)
        num = win32api.RegQueryInfoKey(hkey)[0]
        
        logs = []
        for i in range(num):
            name = win32api.RegEnumKey(hkey, i)
            logs.append(name)
        
        win32api.RegCloseKey(hkey)
        return logs
    except Exception as e:
        print(f"Error: {e}")
        return []

if __name__ == "__main__":
    logs = list_event_logs()
    print("Available Event Logs:")
    for log in logs:
        print(f"- {log}")

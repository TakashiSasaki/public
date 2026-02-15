import sys
import os

# Ensure src is in path
sys.path.append(os.path.join(os.getcwd(), "src"))

from get_a_grip.core.event_log import EventLogCore

def verify_fetch():
    print("Fetching System logs...")
    try:
        logs = EventLogCore.fetch_logs("System", limit=5)
        print(f"Successfully fetched {len(logs)} logs.")
        for log in logs:
            print(f"- [{log['time_generated']}] {log['event_type']} {log['source_name']}: {log['message'][:50]}...")
        return True
    except Exception as e:
        print(f"Failed to fetch logs: {e}")
        return False

if __name__ == "__main__":
    if verify_fetch():
        print("Verification SUCCESS")
    else:
        print("Verification FAILED")

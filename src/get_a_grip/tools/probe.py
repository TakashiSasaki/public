import socket
import json
import sys
import subprocess
import shutil
from get_a_grip.tools.whoami import get_effective_user, get_user_principal_name

def get_windows_hw_info() -> dict:
    """
    Retrieves hardware info on Windows using PowerShell.
    """
    hw_info = {}
    if sys.platform != "win32":
        return hw_info

    try:
        # Get Baseboard and Total Memory
        ps_cmd = (
            "Get-CimInstance -ClassName Win32_BaseBoard | Select-Object -Property Manufacturer, Product | ConvertTo-Json; "
            "Get-CimInstance -ClassName Win32_ComputerSystem | Select-Object -Property TotalPhysicalMemory | ConvertTo-Json"
        )
        process = subprocess.run(
            ["powershell", "-Command", ps_cmd],
            capture_output=True,
            text=True,
            check=False
        )
        
        if process.returncode == 0:
            # PowerShell might return multiple JSON objects concatenated
            parts = process.stdout.strip().split('\n}\n')
            if len(parts) >= 1:
                baseboard = json.loads(parts[0] + '}')
                hw_info["baseboard"] = {
                    "manufacturer": baseboard.get("Manufacturer"),
                    "product": baseboard.get("Product")
                }
            if len(parts) >= 2:
                system = json.loads(parts[1])
                hw_info["totalPhysicalMemory"] = system.get("TotalPhysicalMemory")
    except Exception:
        pass
    
    return hw_info

def get_storage_info() -> list:
    """
    Retrieves basic logical disk information.
    """
    disks = []
    if sys.platform == "win32":
        try:
            ps_cmd = "Get-CimInstance -ClassName Win32_LogicalDisk | Select-Object -Property DeviceID, Size, FreeSpace | ConvertTo-Json"
            process = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                check=False
            )
            if process.returncode == 0:
                data = json.loads(process.stdout)
                if isinstance(data, dict):
                    data = [data]
                for item in data:
                    disks.append({
                        "deviceId": item.get("DeviceID"),
                        "size": item.get("Size"),
                        "freeSpace": item.get("FreeSpace")
                    })
        except Exception:
            pass
    
    # Fallback to shutil for root/current drive if list is empty
    if not disks:
        try:
            usage = shutil.disk_usage("/")
            disks.append({
                "deviceId": "/",
                "size": usage.total,
                "freeSpace": usage.free
            })
        except Exception:
            pass
            
    return disks

def get_probe_data() -> dict:
    """
    Collects environmental and hardware data using standard vocabulary (LDAP/SNMP/AD/CIM).
    """
    hw = get_windows_hw_info()
    
    return {
        "identity": {
            "uid": get_effective_user(),
            "userPrincipalName": get_user_principal_name(),
        },
        "system": {
            "sysName": socket.gethostname(),
            "platform": sys.platform,
            "baseboard": hw.get("baseboard"),
            "totalPhysicalMemory": hw.get("totalPhysicalMemory"),
            "logicalDisks": get_storage_info()
        }
    }

def print_probe_data() -> None:
    """
    Prints the collected environmental data in JSON format.
    """
    data = get_probe_data()
    print(json.dumps(data, indent=2))

def save_probe_data(output_file: str) -> None:
    """
    Saves the collected environmental data to a JSON file.
    """
    data = get_probe_data()
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

import socket
import json
from get_a_grip.tools.whoami import get_effective_user

def get_probe_data() -> dict:
    """
    Collects environmental data like username and hostname.
    """
    return {
        "username": get_effective_user(),
        "hostname": socket.gethostname()
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

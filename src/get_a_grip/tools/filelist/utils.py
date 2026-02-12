import json
from datetime import datetime
from get_a_grip.tools.whoami import get_effective_user, get_user_principal_name
from get_a_grip.tools.filelist.types import FileList

def save_to_json(data: FileList, output_path: str) -> None:
    """
    Saves the scanned data to a JSON-LD file with an external context.
    """
    output_data = {
        "@context": [
            "https://purl.org/gag/schema/filelist.jsonld"
        ],
        "@type": "ItemList",
        "observedAt": datetime.now().isoformat(),
        "observer": {
            "uid": get_effective_user(),
            "userPrincipalName": get_user_principal_name()
        },
        "files": data.get("files", []),
        "dirs": data.get("dirs", [])
    }
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

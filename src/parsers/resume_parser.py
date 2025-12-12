import json
from pathlib import Path

def parse_resume_json(json_path: str) -> dict:
    with open(json_path, 'r') as f:
        return json.load(f)
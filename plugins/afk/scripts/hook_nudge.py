#!/usr/bin/env python3
import json
import os
import sys
import urllib.request

def main():
    url = os.environ.get("AFKLAUDE_URL", "")
    token = os.environ.get("AFKLAUDE_TOKEN", "")

    if not url or not token:
        return

    try:
        input_data = json.load(sys.stdin)
    except:
        input_data = {}

    session_id = input_data.get("session_id", "")
    payload = {"session_id": session_id}

    try:
        req = urllib.request.Request(
            f"{url}/nudge",
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        urllib.request.urlopen(req, timeout=5)
    except:
        pass

if __name__ == "__main__":
    main()

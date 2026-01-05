#!/usr/bin/env python3
import json
import os
import urllib.request
import urllib.error

def main():
    url = os.environ.get("AFKLAUDE_URL", "")
    token = os.environ.get("AFKLAUDE_TOKEN", "")

    if not url or not token:
        print("Not configured. Set AFKLAUDE_URL and AFKLAUDE_TOKEN in your Claude env settings.")
        return

    try:
        req = urllib.request.Request(
            f"{url}/settings",
            headers={"Authorization": f"Bearer {token}"},
            method="GET",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())

        if not result.get("afk"):
            print("Already back.")
            return

        req = urllib.request.Request(
            f"{url}/settings",
            data=json.dumps({"afk": False}).encode(),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            json.loads(resp.read().decode())
        print("Back at your desk. Normal permissions apply.")
    except urllib.error.HTTPError as e:
        print(f"Failed to disable AFK mode: HTTP {e.code}")
    except Exception as e:
        print(f"Failed to disable AFK mode: {e}")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import datetime
import json
import os
import socket
import sys
import urllib.request
import urllib.error

LOGFILE = "/tmp/afklaude-debug.log"

def debug(msg):
    if not os.environ.get("AFKLAUDE_DEBUG"):
        return
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOGFILE, "a") as f:
        f.write(f"[{ts}] [executed] {msg}\n")

def error_message(e):
    if isinstance(e, socket.timeout):
        return "AFKlaude request timed out"
    if isinstance(e, urllib.error.HTTPError):
        if 400 <= e.code < 500:
            return f"AFKlaude client error ({e.code})"
        if 500 <= e.code < 600:
            return f"AFKlaude server error ({e.code})"
        return f"AFKlaude HTTP error ({e.code})"
    if isinstance(e, urllib.error.URLError):
        if isinstance(e.reason, socket.timeout):
            return "AFKlaude request timed out"
        return f"AFKlaude connection failed: {e.reason}"
    return f"AFKlaude error: {e}"

def is_afklaude_command(tool_name, tool_input):
    if tool_name != "Bash":
        return False
    command = tool_input.get("command", "")
    return "scripts/cmd_afk.py" in command or "scripts/cmd_back.py" in command

def main():
    url = os.environ.get("AFKLAUDE_URL", "https://api.afklaude.dev")
    token = os.environ.get("AFKLAUDE_TOKEN", "")

    debug(f"started, url={url}, token={'set' if token else 'unset'}")

    if not url or not token:
        debug("missing env vars, skipping")
        return

    try:
        input_data = json.load(sys.stdin)
        debug(f"input: {json.dumps(input_data)[:500]}")
        tool_use_id = input_data.get("tool_use_id", "")
        tool_name = input_data.get("tool_name", "")
        tool_input = input_data.get("tool_input", {})
    except Exception as e:
        debug(f"failed to parse input: {e}")
        return

    if is_afklaude_command(tool_name, tool_input):
        debug("afklaude command, skipping executed notification")
        return

    if not tool_use_id:
        debug("no tool_use_id, skipping")
        return

    debug(f"tool_use_id={tool_use_id}")

    try:
        req = urllib.request.Request(
            f"{url}/executed",
            data=json.dumps({"tool_use_id": tool_use_id}).encode(),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        debug(f"calling POST {url}/executed")
        resp = urllib.request.urlopen(req, timeout=5)
        debug(f"response: {resp.status}")
    except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout) as e:
        debug(f"request failed: {error_message(e)}")

if __name__ == "__main__":
    main()

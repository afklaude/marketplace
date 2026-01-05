#!/usr/bin/env python3
import datetime
import json
import os
import sys
import time
import urllib.request
import urllib.error

LOGFILE = "/tmp/afklaude-debug.log"
POLL_INTERVAL = 2
POLL_TIMEOUT = 300


def debug(msg):
    if not os.environ.get("AFKLAUDE_DEBUG"):
        return
    ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOGFILE, "a") as f:
        f.write(f"[{ts}] [request] {msg}\n")


def respond(hook_response):
    print(json.dumps(hook_response))
    sys.exit(0)


def passthrough():
    sys.exit(0)


def allow():
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "allow"}}


def is_afklaude_command(tool_name, tool_input):
    if tool_name != "Bash":
        return False
    command = tool_input.get("command", "")
    return "scripts/cmd_afk.py" in command or "scripts/cmd_back.py" in command


def poll_status(url, token, request_id):
    status_url = f"{url}/request/{request_id}/status"
    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        if elapsed >= POLL_TIMEOUT:
            raise TimeoutError("AFKlaude request timed out waiting for response")

        try:
            req = urllib.request.Request(
                status_url,
                headers={"Authorization": f"Bearer {token}"},
                method="GET",
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                result = json.loads(resp.read().decode())

            status = result.get("status", "")
            debug(f"poll result: status={status}")

            if status == "pending":
                time.sleep(POLL_INTERVAL)
                continue

            return result

        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise Exception("Request not found or expired")
            raise


def main():
    url = os.environ.get("AFKLAUDE_URL", "https://api.afklaude.dev")
    token = os.environ.get("AFKLAUDE_TOKEN", "")

    debug(f"started, url={url}, token={'set' if token else 'unset'}")

    if not url or not token:
        debug("missing env vars, passing through to CC")
        passthrough()

    try:
        input_data = json.load(sys.stdin)
        debug(f"input: {json.dumps(input_data)[:500]}")
    except Exception as e:
        debug(f"failed to parse input: {e}")
        return passthrough()

    session_id = input_data.get("session_id", "")
    tool_use_id = input_data.get("tool_use_id", "")
    cwd = input_data.get("cwd", "")
    tool_name = input_data.get("tool_name", "")
    tool_input = input_data.get("tool_input", {})
    hook_event = input_data.get("hook_event_name", "PreToolUse")

    debug(f"tool={tool_name} session={session_id} tool_use_id={tool_use_id} hook={hook_event}")

    if is_afklaude_command(tool_name, tool_input):
        debug("afklaude command script, auto-approving")
        respond(allow())

    payload = {
        "session_id": session_id,
        "tool_use_id": tool_use_id,
        "tool_name": tool_name,
        "tool_input": tool_input,
        "cwd": cwd,
        "hook_event": hook_event,
    }

    try:
        req = urllib.request.Request(
            f"{url}/request",
            data=json.dumps(payload).encode(),
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read().decode())
        debug(f"response: {result}")
    except Exception as e:
        debug(f"request failed: {e}")
        debug("passing through to CC")
        passthrough()

    if result.get("passthrough"):
        debug("server requested passthrough")
        passthrough()

    if result.get("hook_response"):
        debug(f"immediate hook_response: {result['hook_response']}")
        respond(result["hook_response"])

    request_id = result.get("request_id", "")
    if not request_id:
        debug("no request_id and no hook_response, passing through")
        passthrough()

    debug(f"polling status for {request_id}...")

    try:
        result = poll_status(url, token, request_id)
        debug(f"poll complete: {result}")

        if result.get("hook_response"):
            respond(result["hook_response"])

        debug("no hook_response in poll result, passing through")
        passthrough()

    except TimeoutError as e:
        debug(f"timeout: {e}")
        debug("passing through to CC")
        passthrough()
    except Exception as e:
        debug(f"poll failed: {e}")
        debug("passing through to CC")
        passthrough()


if __name__ == "__main__":
    main()

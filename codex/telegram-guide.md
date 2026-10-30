# Telegram text delivery

Read this guide when the user explicitly asks you to send text through Telegram.
Examples include "send this to Telegram" and "send the summary to me on Telegram."
This guide does not authorize a message by itself.

## Before delivery

1. Use only the text or result that the user authorized for delivery.
2. Use `TELEGRAM_BOT_TOKEN` and `TELEGRAM_USER_ID` from the process environment.
3. If either value is absent or empty, load only the missing values from `~/.env` as dotenv data.
4. Preserve each non-empty environment value.
5. Use `TELEGRAM_USER_ID` as the default private `chat_id`.
6. If the user explicitly requests another destination, use that destination for this message only.
7. Never execute or shell-source `~/.env`.
8. Never put credentials, destinations, request URLs, or message contents in command arguments or logs.
9. Keep request data in memory or a temporary file with current-user-only permissions.
10. Remove temporary files after the attempt.

The bot must already have permission to message the selected chat.
If Telegram rejects the request, report the failure without raw response data.
If credentials are missing, report only their variable names and the sources examined.
Never send a test message without an explicit request.

## Dependency-free example

The example uses Python 3 and the [Telegram Bot API](https://core.telegram.org/bots/api#sendmessage).
It sends one plain text message with `sendMessage` and checks the JSON `ok` field.
It does not retry.

1. Save the Python block in a private temporary directory as `send_telegram.py`.
2. Write the authorized text to a private `message.json` file with a `text` string field.
3. Include `chat_id` in that JSON only for an explicitly requested alternate destination.
4. Replace `PRIVATE_DIR` with the private directory path in the command below.
5. Run `python3 PRIVATE_DIR/send_telegram.py < PRIVATE_DIR/message.json` after the user authorizes delivery.

The command contains only file paths.
Do not place actual text or destinations in a shell command to create the JSON.
Write the JSON with a file tool.

The dotenv reader supports single-line assignments, optional `export`, quoted values, and comments.
It does not expand variables, execute substitutions, or support multiline values.
Only the two required names enter the process environment.

```python
import http.client
import json
import os
from pathlib import Path
import re
import shlex
import sys


def main():
    names = ("TELEGRAM_BOT_TOKEN", "TELEGRAM_USER_ID")
    missing = {name for name in names if not os.environ.get(name)}
    try:
        if missing:
            values = {}
            try:
                with (Path.home() / ".env").open(encoding="utf-8-sig") as source:
                    for line in source:
                        line = line.strip()
                        if line.startswith("export "):
                            line = line[7:].lstrip()
                        key, separator, raw = line.partition("=")
                        key = key.strip()
                        if not separator or key not in missing:
                            continue
                        # shortcut: single-line dotenv only, use a dotenv library if this format grows.
                        parts = shlex.split(raw, comments=True, posix=True)
                        if len(parts) > 1:
                            raise ValueError
                        values[key] = parts[0] if parts else ""
            except FileNotFoundError:
                pass
            for name, value in values.items():
                os.environ[name] = value
        missing = [name for name in names if not os.environ.get(name)]
        if missing:
            print("Missing: " + ", ".join(missing) +
                  ". Examined process environment and ~/.env.", file=sys.stderr)
            return 2
        data = json.load(sys.stdin.buffer)
        if not isinstance(data, dict) or not isinstance(data.get("text"), str):
            raise ValueError
        if not 1 <= len(data["text"]) <= 4096:
            raise ValueError
        chat_id = data.get("chat_id", os.environ["TELEGRAM_USER_ID"])
        if "chat_id" not in data:
            if not re.fullmatch(r"[1-9][0-9]*", chat_id):
                raise ValueError
        elif type(chat_id) not in (str, int) or not str(chat_id).strip():
            raise ValueError
        payload = json.dumps({"chat_id": chat_id, "text": data["text"]}).encode("utf-8")
    except Exception:
        print("Cannot read credentials or message input. No request sent.", file=sys.stderr)
        return 2

    connection = None
    try:
        connection = http.client.HTTPSConnection("api.telegram.org", timeout=30)
        connection.request(
            "POST", "/bot" + os.environ["TELEGRAM_BOT_TOKEN"] + "/sendMessage",
            body=payload, headers={"Content-Type": "application/json"},
        )
        response = connection.getresponse()
        result = json.loads(response.read())
        if isinstance(result, dict) and result.get("ok") is False:
            print("Telegram rejected the message. No automatic retry.", file=sys.stderr)
            return 1
        if (200 <= response.status < 300 and isinstance(result, dict)
                and result.get("ok") is True and isinstance(result.get("result"), dict)):
            print("Telegram accepted the message.")
            return 0
    except Exception:
        pass
    finally:
        if connection is not None:
            try:
                connection.close()
            except Exception:
                pass
    print("Delivery status unknown. Do not retry automatically.", file=sys.stderr)
    return 3


if __name__ == "__main__":
    sys.exit(main())
```

## Result

Exit `0` means that Telegram accepted the message.
Acceptance does not prove that the recipient read it.
Exit `1` means that Telegram rejected the request.
Exit `2` means that local validation failed before any request.
Exit `3` means that delivery is uncertain, including a timeout or malformed response.

If delivery is uncertain, report that state and require a new user decision before another attempt.
Never print exceptions, response bodies, tokens, chat identifiers, or message contents to explain a failure.
Keep the final report brief and state the observed delivery result.

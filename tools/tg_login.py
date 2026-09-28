#!/usr/bin/env python3
"""One-time Telegram login for the Season One masters upload.

Run this YOURSELF, in your own terminal, so the phone login code and 2FA
password are never typed into a chat transcript:

    ~/Movies/Radio-ish/.venv-tg/bin/python tools/tg_login.py

It needs api_id / api_hash from https://my.telegram.org (Apps > API development
tools). A user session is required, not a bot: the hosted Bot API caps uploads at
50 MB, and these masters run to 895 MB. The user/MQTT API allows 2 GB.

The session is written OUTSIDE the git repo (to ~/.radio-ish-tg/session.session)
so credentials can never be committed to the public repository.
"""
import os, sys, getpass

SESSION_DIR = os.path.expanduser("~/.radio-ish-tg")
SESSION = os.path.join(SESSION_DIR, "session.session")
CREDS = os.path.join(SESSION_DIR, "creds.txt")

os.makedirs(SESSION_DIR, exist_ok=True)
os.chmod(SESSION_DIR, 0o700)

if os.path.exists(CREDS):
    api_id, api_hash = open(CREDS).read().split()[:2]
    print("using saved api_id / api_hash from", CREDS)
else:
    print("Get these from https://my.telegram.org -> Apps -> API development tools")
    api_id = input("api_id: ").strip()
    api_hash = getpass.getpass("api_hash: ").strip()
    with open(CREDS, "w") as f:
        f.write(f"{api_id} {api_hash}\n")
    os.chmod(CREDS, 0o600)

try:
    from telethon import TelegramClient
except ImportError:
    sys.exit("telethon missing. Install it with:\n"
             "  python3 -m venv .venv-tg && .venv-tg/bin/pip install telethon")

from telethon import functions

client = TelegramClient(SESSION, int(api_id), api_hash)
client.connect()

if not client.is_user_authorized():
    phone = input("phone (international format, e.g. +260...): ").strip()
    client.send_code_request(phone)
    code = input("code from Telegram: ").strip()
    try:
        client.sign_in(phone=phone, code=code)
    except Exception as e:
        if "password" in str(e).lower() or "2FA" in str(e):
            pw = getpass.getpass("2FA password: ")
            client.sign_in(password=pw)
        else:
            raise

me = client.get_me()
print(f"\nlogged in as {me.first_name} {me.last_name or ''} (@{me.username}) id={me.id}")

# show dialogs that look like a channel, so the target can be picked with eyes open
print("\nchannels / groups visible to this account:")
for d in client.get_dialogs(limit=200):
    if d.is_group or d.is_channel:
        print(f"  {d.title!r}  username=@{d.entity.username}  id={d.id}")

client.disconnect()
print(f"\nsession saved to {SESSION}")
print("Do NOT commit that file. It is outside the repo by design.")

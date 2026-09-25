#!/usr/bin/env python3
"""
Script for agent

it set current session as active in telegram and send user message
"""

import argparse
import http
import http.client
import json
import os
import sys
from urllib.parse import urlparse


def parse_args(argv: list[str]):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "chat_id",
        help="chat id is a user't telegram chat id",
    )
    parser.add_argument(
        "message",
        help="text message to user",
    )
    parser.add_argument(
        "await_time",
        help="time in sconds that you message still relevant",
    )
    return parser.parse_args(argv)


def main(argv: list[str]):
    args = parse_args(argv)

    session_id: str = os.getenv("AGENT_SESSION_ID", "")
    if session_id == "":
        print("You can't use this script, because env AGENT_SESSION_ID is empty")
        sys.exit(1)

    telegram_gateway_url: str = os.getenv("TELEGRAM_GATEWAY_URL", "")
    if telegram_gateway_url == "":
        print(
            "telegram gateway is unreachible. because env 'TELEGRAM_GATEWAY_URL' is empty"
        )
        sys.exit(1)

    parsed_url = urlparse(telegram_gateway_url)
    url = parsed_url.netloc
    if url == "":
        print(f"can't parse url: {telegram_gateway_url}")
        sys.exit(1)

    req = {
        "session_id": session_id,
        "chat_id": int(args.chat_id),
        "message": args.message,
        "await_time": int(args.await_time),
    }

    json_data = json.dumps(req).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "Content-Length": str(len(json_data)),
    }

    try:
        conn = http.client.HTTPConnection(url)
        conn.request(
            method="POST",
            url="/attach",
            headers=headers,
            body=json_data,
        )
        response = conn.getresponse()

    except Exception as e:
        print(f"Error: telegram gateway: {e}")
        sys.exit(1)

    data = response.read(4096).decode("utf-8", errors="replace")

    if response.status != http.HTTPStatus.OK:
        raise Exception(f"Gateway return error: {data}")

    print(f"Current session attached succecceful: {data}")


if __name__ == "__main__":
    main(sys.argv[1:])

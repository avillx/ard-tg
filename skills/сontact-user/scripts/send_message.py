#!/usr/bin/env python3
"""
Script for agent

it set current session as active in telegram and send user message
"""

import argparse
import os
import sys

import requests


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
        print("you can't use this script, cause you has no session_id")
        sys.exit(1)

    telegram_gateway_url: str = os.getenv("TELEGRAM_GATEWAY_URL", "")
    if telegram_gateway_url == "":
        print("you can't use this script, cause telegram gateway is unreachible")
        sys.exit(1)

    req = {
        "session_id": session_id,
        "chat_id": int(args.chat_id),
        "message": args.message,
        "await_time": int(args.await_time),
    }

    response = requests.post(url=telegram_gateway_url + "/attach", json=req)

    if response.status_code != 200:
        print(f"Gateway return error: {response.content}")
        sys.exit(1)

    print("message sended succecceful. Await respond")


if __name__ == "__main__":
    main(sys.argv[1:])

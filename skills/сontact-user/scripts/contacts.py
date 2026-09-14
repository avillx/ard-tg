#!/usr/bin/env python3
"""
Script for agent

send get request to the gateway and return list of contacts
"""

import os
import sys

import requests


def main():
    telegram_gateway_url: str = os.getenv("TELEGRAM_GATEWAY_URL", "")
    if telegram_gateway_url == "":
        print("you can't use this script, cause telegram gateway is unreachible")
        sys.exit(1)

    try:
        response = requests.get(telegram_gateway_url + "/contacts", timeout=30)
    except requests.Timeout:
        print("Timeout: telegram gateway is not respond, my be is not working right now")
        sys.exit(1)
    except requests.ConnectionError:
        print("Connection error: telegram gateway unreachible")
        sys.exit(1)

    if response.status_code != 200:
        print(f"Gateway return error: {response.status_code}, {response.content}")
        sys.exit(1)

    print(response.content)


if __name__ == "__main__":
    main()

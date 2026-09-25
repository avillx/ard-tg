#!/usr/bin/env python3
"""
Script for agent

send get request to the gateway and return list of contacts
"""

import http
import http.client
import os
import sys
from urllib.parse import urlparse


def main():

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

    try:
        conn = http.client.HTTPConnection(url)
        conn.request("GET", "/contacts")
        response = conn.getresponse()
    except TimeoutError:
        print(
            "Timeout: telegram gateway is not respond, my be is not working right now"
        )
        sys.exit(1)

    except Exception as e:
        print(f"Error: telegram gateway {e}")
        sys.exit(1)

    if response.status != http.HTTPStatus.OK:
        print(f"Gateway respond with bad status: {response.status}")

    data = response.read(4096).decode("utf-8", errors="replace")
    print(data)


if __name__ == "__main__":
    main()

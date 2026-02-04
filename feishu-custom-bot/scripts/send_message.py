import requests
import argparse
from typing import Dict
import json


def send_feushu_message(webhook_url, data: Dict):
    response = requests.post(webhook_url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    response.raise_for_status()


# Parse command line arguments
parser = argparse.ArgumentParser(description="Send feishu custom boot message")
parser.add_argument(
    "-u", "--webhook_url", required=True, help="URL of custom bot webhook"
)
parser.add_argument(
    "-f",
    "--file",
    required=True,
    help="Text file for saving json of message",
)
args = parser.parse_args()
with open(args.file, "r", encoding="utf-8") as f:
    data = json.loads(f.read())
send_feushu_message(webhook_url=args.webhook_url, data=data)

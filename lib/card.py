import os
import requests

CARD_API_URL = os.getenv("CARD_API_URL")


def get_card_name():
    resp = requests.get(CARD_API_URL)
    resp.raise_for_status()
    data = resp.json()
    name = data["name"]
    print(f"Got name from card API: {name}")
    return name

import os
import requests

CARD_API_URL = os.getenv("CARD_API_URL")


def get_card_data():
    resp = requests.get(CARD_API_URL)
    resp.raise_for_status()
    data = resp.json()
    print(f"Got card data: name={data.get('name')}, school={data.get('schoolName')}")
    return data


def get_card_name():
    data = get_card_data()
    return data["name"]

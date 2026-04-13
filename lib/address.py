import requests

ADDRESS_API = "https://mocloc.com/api/v1/addresses/ID?count=1"


def get_random_address():
    resp = requests.get(ADDRESS_API)
    resp.raise_for_status()
    data = resp.json()
    if isinstance(data, list) and len(data) > 0:
        return data[0]
    raise Exception("No address data returned from API")


def split_name(full_name):
    words = full_name.strip().split()
    first_name = words[0] if words else ""
    last_name = " ".join(words[1:]) if len(words) > 1 else ""
    return first_name, last_name

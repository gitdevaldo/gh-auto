import json


def load_cookies(path="cookies.json"):
    with open(path, "r") as f:
        return json.load(f)


def get_username(cookies):
    for cookie in cookies:
        if cookie["name"] == "dotcom_user":
            return cookie["value"]
    raise Exception("Could not find dotcom_user cookie")


def format_cookies(cookies):
    formatted = []
    for cookie in cookies:
        c = {
            "name": cookie["name"],
            "value": cookie["value"],
            "domain": cookie["domain"],
            "path": cookie.get("path", "/"),
        }
        if cookie.get("secure"):
            c["secure"] = True
        if cookie.get("httpOnly"):
            c["httpOnly"] = True
        if cookie.get("sameSite"):
            site = cookie["sameSite"]
            if site == "no_restriction":
                c["sameSite"] = "None"
            elif site in ("lax", "Lax"):
                c["sameSite"] = "Lax"
            elif site in ("strict", "Strict"):
                c["sameSite"] = "Strict"
        formatted.append(c)
    return formatted

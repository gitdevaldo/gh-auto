import os
import json
import time
import re
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from camoufox.sync_api import Camoufox

load_dotenv()

CARD_API_URL = os.getenv("CARD_API_URL")


def get_card_name():
    resp = requests.get(CARD_API_URL)
    resp.raise_for_status()
    data = resp.json()
    name = data["name"]
    print(f"Got name from card API: {name}")
    return name


def load_cookies():
    with open("cookies.json", "r") as f:
        return json.load(f)


def get_username(cookies):
    for cookie in cookies:
        if cookie["name"] == "dotcom_user":
            return cookie["value"]
    raise Exception("Could not find dotcom_user cookie")


def get_profile_dir(username):
    profiles_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profiles")
    profile_path = os.path.join(profiles_dir, username)
    if not os.path.exists(profile_path):
        os.makedirs(profile_path, exist_ok=True)
        print(f"Created new browser profile: {profile_path}")
    else:
        print(f"Using existing browser profile: {profile_path}")
    return profile_path


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


def build_session(cookies):
    session = requests.Session()
    session.headers.update({
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
    })
    for cookie in cookies:
        session.cookies.set(
            cookie["name"],
            cookie["value"],
            domain=cookie.get("domain", ".github.com"),
            path=cookie.get("path", "/"),
        )
    return session


def scrape_profile_data(session):
    resp = session.get("https://github.com/settings/profile")
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    token_el = soup.find("input", {"name": "authenticity_token"})
    if not token_el:
        raise Exception("Could not find authenticity_token on the page")
    token = token_el["value"]
    print(f"Got authenticity_token: {token[:20]}...")

    ts_el = soup.find("input", {"name": "timestamp_secret"})
    if not ts_el:
        raise Exception("Could not find timestamp_secret on the page")
    timestamp_secret = ts_el["value"]
    print(f"Got timestamp_secret: {timestamp_secret[:20]}...")

    honeypot_el = soup.find("input", {"name": re.compile(r"^required_field_")})
    honeypot_name = honeypot_el["name"] if honeypot_el else "required_field_1b05"
    print(f"Got honeypot field: {honeypot_name}")

    return {
        "token": token,
        "timestamp_secret": timestamp_secret,
        "honeypot_name": honeypot_name,
    }


def update_github_profile(session, name, profile_data, username):
    payload = [
        ("_method", "put"),
        ("authenticity_token", profile_data["token"]),
        ("user[profile_name]", name),
        ("user[profile_email]", ""),
        ("user[profile_bio]", ""),
        ("user[profile_pronouns]", ""),
        ("user[profile_blog]", ""),
        ("user[profile_social_accounts][][key]", "generic"),
        ("user[profile_social_accounts][][url]", ""),
        ("user[profile_social_accounts][][key]", "generic"),
        ("user[profile_social_accounts][][url]", ""),
        ("user[profile_social_accounts][][key]", "generic"),
        ("user[profile_social_accounts][][url]", ""),
        ("user[profile_social_accounts][][key]", "generic"),
        ("user[profile_social_accounts][][url]", ""),
        ("user[profile_company]", ""),
        ("user[profile_location]", ""),
        ("user[profile_local_time_zone_name]", "International Date Line West"),
        (profile_data["honeypot_name"], ""),
        ("timestamp", str(int(time.time() * 1000))),
        ("timestamp_secret", profile_data["timestamp_secret"]),
    ]

    headers = {
        "cache-control": "max-age=0",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://github.com",
        "referer": "https://github.com/settings/profile",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
    }

    resp = session.post(
        f"https://github.com/users/{username}",
        data=payload,
        headers=headers,
        allow_redirects=False,
    )

    print(f"Profile update status: {resp.status_code}")
    if resp.status_code == 302:
        print("Profile updated successfully.")
    else:
        print(f"Unexpected response: {resp.status_code}")
        print(resp.text[:500])


def main():
    name = get_card_name()
    cookies = load_cookies()
    username = get_username(cookies)
    print(f"Got username: {username}")

    session = build_session(cookies)
    profile_data = scrape_profile_data(session)
    update_github_profile(session, name, profile_data, username)


if __name__ == "__main__":
    main()

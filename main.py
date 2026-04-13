import os
import json
import requests
from dotenv import load_dotenv
from camoufox.sync_api import Camoufox

load_dotenv()

CARD_API_URL = os.getenv("CARD_API_URL")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME")


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


def get_authenticity_token(cookies):
    with Camoufox(headless=True) as browser:
        context = browser.new_context()

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
            context.add_cookies([c])

        page = context.new_page()
        page.goto("https://github.com/settings/profile")
        page.wait_for_load_state("domcontentloaded")

        token_el = page.query_selector('input[name="authenticity_token"]')
        if not token_el:
            raise Exception("Could not find authenticity_token on the page")

        token = token_el.get_attribute("value")
        print(f"Got authenticity_token: {token[:20]}...")

        context.close()

    return token


def update_github_profile(name, token, cookies):
    cookie_str = "; ".join(f"{c['name']}={c['value']}" for c in cookies)

    payload = {
        "_method": "put",
        "authenticity_token": token,
        "user[profile_name]": name,
        "user[profile_email]": "",
        "user[profile_bio]": "",
        "user[profile_pronouns]": "",
        "user[profile_blog]": "",
        "user[profile_social_accounts][][key]": "generic",
        "user[profile_social_accounts][][url]": "",
        "user[profile_company]": "",
        "user[profile_location]": "",
        "user[profile_local_time_zone_name]": "International Date Line West",
    }

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "accept-language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "cache-control": "max-age=0",
        "content-type": "application/x-www-form-urlencoded",
        "origin": "https://github.com",
        "referer": "https://github.com/settings/profile",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "cookie": cookie_str,
    }

    resp = requests.post(
        f"https://github.com/users/{GITHUB_USERNAME}",
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
    token = get_authenticity_token(cookies)
    update_github_profile(name, token, cookies)


if __name__ == "__main__":
    main()

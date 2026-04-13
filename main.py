import os
import json
import time
import requests
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


def scrape_profile_data(cookies):
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

        timestamp_secret_el = page.query_selector('input[name="timestamp_secret"]')
        if not timestamp_secret_el:
            raise Exception("Could not find timestamp_secret on the page")
        timestamp_secret = timestamp_secret_el.get_attribute("value")
        print(f"Got timestamp_secret: {timestamp_secret[:20]}...")

        honeypot_el = page.query_selector('input[name^="required_field_"]')
        honeypot_name = honeypot_el.get_attribute("name") if honeypot_el else "required_field_1b05"
        print(f"Got honeypot field: {honeypot_name}")

        username = None
        meta_el = page.query_selector('meta[name="user-login"]')
        if meta_el:
            username = meta_el.get_attribute("content")
        if not username:
            form_el = page.query_selector('form.edit_user')
            if form_el:
                action = form_el.get_attribute("action")
                if action and "/users/" in action:
                    username = action.split("/users/")[-1].split("/")[0].split("?")[0]
        if not username:
            link_el = page.query_selector('a[href*="github.com/"][data-hydro-click]')
            if link_el:
                href = link_el.get_attribute("href")
                username = href.rstrip("/").split("/")[-1]
        if not username:
            raise Exception("Could not determine GitHub username from page")
        print(f"Got username: {username}")

        session_cookies = context.cookies("https://github.com")
        print(f"Got {len(session_cookies)} session cookies")

        context.close()

    return {
        "token": token,
        "timestamp_secret": timestamp_secret,
        "honeypot_name": honeypot_name,
        "username": username,
        "session_cookies": session_cookies,
    }


def update_github_profile(name, profile_data):
    cookie_str = "; ".join(f"{c['name']}={c['value']}" for c in profile_data["session_cookies"])

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
        f"https://github.com/users/{profile_data['username']}",
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
    profile_data = scrape_profile_data(cookies)
    update_github_profile(name, profile_data)


if __name__ == "__main__":
    main()

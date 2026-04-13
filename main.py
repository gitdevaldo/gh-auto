import os
import json
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


def update_profile_via_browser(name, cookies, username):
    profile_dir = get_profile_dir(username)

    with Camoufox(headless=True, persistent_context=True, user_data_dir=profile_dir) as context:
        context.add_cookies(format_cookies(cookies))

        page = context.new_page()
        page.goto("https://github.com/settings/profile")
        page.wait_for_load_state("domcontentloaded")

        name_input = page.query_selector('input[name="user[profile_name]"]')
        if not name_input:
            raise Exception("Could not find name input on the page")

        name_input.fill("")
        name_input.type(name)
        print(f"Filled name field with: {name}")

        submit_btn = page.query_selector('button[type="submit"] .Button-label')
        if not submit_btn:
            submit_btn = page.query_selector('button[type="submit"]')
        if not submit_btn:
            raise Exception("Could not find submit button on the page")

        page.wait_for_timeout(500)

        with page.expect_navigation(wait_until="domcontentloaded", timeout=15000):
            submit_btn.click()

        final_url = page.url
        print(f"After submit, landed on: {final_url}")

        if "settings/profile" in final_url:
            flash = page.query_selector('.flash-success, .flash-notice')
            if flash:
                print(f"Profile updated successfully! Message: {flash.inner_text().strip()}")
            else:
                print("Profile updated successfully!")
        else:
            print(f"Unexpected result. Current URL: {final_url}")


def main():
    name = get_card_name()
    cookies = load_cookies()
    username = get_username(cookies)
    print(f"Got username: {username}")
    update_profile_via_browser(name, cookies, username)


if __name__ == "__main__":
    main()

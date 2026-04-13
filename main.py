import argparse
import os
import shutil
from dotenv import load_dotenv

load_dotenv()

from lib.card import get_card_data
from lib.cookies import load_cookies, get_username
from lib.address import get_random_address, split_name
from lib.browser import open_browser, open_browser_fresh
from lib.github import update_profile_name, update_billing_address, apply_education, ensure_2fa, login_github


PROFILES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "profiles")


def log(msg):
    print(f"  {msg}")


def _rename_profile(old_name, new_name):
    old_path = os.path.join(PROFILES_DIR, old_name)
    new_path = os.path.join(PROFILES_DIR, new_name)
    if old_path == new_path:
        return
    if os.path.exists(new_path):
        shutil.rmtree(new_path)
    if os.path.exists(old_path):
        shutil.move(old_path, new_path)
        log(f"Profile saved as: {new_name}")


def header(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["faculty", "student"], default="faculty",
                        help="Education application type: faculty (teacher) or student")
    parser.add_argument("--login", type=str, default=None,
                        help="Login with email/username and password: email/username password")
    args, remaining = parser.parse_known_args()

    header("Preparing Data")

    card_data = get_card_data()
    name = card_data["name"]
    first_name, last_name = split_name(name)
    log(f"Name: {first_name} {last_name}")

    address = get_random_address()
    log(f"Address: {address.get('address_line')}, {address.get('city')}")

    if args.login:
        email = args.login
        if remaining:
            password = remaining[0]
        else:
            raise Exception("Password is required after --login email/username")

        temp_profile = "_tmp_login"

        header("Opening Browser")
        context, ctx = open_browser_fresh(temp_profile)
        try:
            page = ctx.new_page()

            header("Logging In")
            username = login_github(page, email, password)
        finally:
            context.__exit__(None, None, None)

        _rename_profile(temp_profile, username)

        header("Opening Browser")
        log(f"User: {username}")
        context, ctx = open_browser_fresh(username)
        try:
            page = ctx.new_page()

            header("Two-Factor Authentication")
            ensure_2fa(page, username)

            header("Updating Profile")
            update_profile_name(page, name)

            header("Updating Billing Address")
            update_billing_address(page, first_name, last_name, address)

            header("Applying for Education Benefits")
            apply_education(page, card_data, app_type=args.type)
        finally:
            context.__exit__(None, None, None)
    else:
        cookies = load_cookies()
        username = get_username(cookies)

        header("Opening Browser")
        log(f"User: {username}")
        context, ctx = open_browser(username, cookies)
        try:
            page = ctx.new_page()

            header("Two-Factor Authentication")
            ensure_2fa(page, username)

            header("Updating Profile")
            update_profile_name(page, name)

            header("Updating Billing Address")
            update_billing_address(page, first_name, last_name, address)

            header("Applying for Education Benefits")
            apply_education(page, card_data, app_type=args.type)
        finally:
            context.__exit__(None, None, None)

    header("Complete")
    log("All tasks finished successfully!")
    print()


if __name__ == "__main__":
    main()

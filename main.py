import argparse
import os
import shutil
from dotenv import load_dotenv

load_dotenv()

from lib.card import get_card_data
from lib.cookies import load_cookies, get_username
from lib.address import get_random_address, split_name
from lib.browser import open_browser, open_browser_fresh, get_profile_dir
from lib.github import update_profile_name, update_billing_address, apply_education, ensure_2fa, login_github
from lib.mailer import send_report


def log(msg):
    print(msg)


def header(title):
    print(f"\n[{title}]")


def cleanup_profile(profile_name):
    profile_dir = get_profile_dir(profile_name)
    if os.path.exists(profile_dir):
        shutil.rmtree(profile_dir)
        log(f"Profile cleaned up: {profile_name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["faculty", "student"], default="faculty",
                        help="Education application type: faculty (teacher) or student")
    parser.add_argument("--login", type=str, default=None,
                        help="Login with email/username and password: email/username password")
    parser.add_argument("--report", type=str, default=None,
                        help="Send success report to this email address")
    args, remaining = parser.parse_known_args()

    header("Preparing")

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

        profile_name = email

        header("Login")
        context, ctx = open_browser_fresh(profile_name)
        try:
            page = ctx.new_page()

            username = login_github(page, email, password)

            header("Setup")
            ensure_2fa(page, username)
            update_profile_name(page, name)
            update_billing_address(page, first_name, last_name, address)

            header("Application")
            apply_education(page, card_data, app_type=args.type)
        finally:
            context.__exit__(None, None, None)

        if args.report:
            header("Report")
            if send_report(args.report, username, card_data, address, args.type):
                log(f"Report sent → {args.report}")

        cleanup_profile(profile_name)
    else:
        cookies = load_cookies()
        username = get_username(cookies)
        profile_name = username
        log(f"User: {username}")

        header("Setup")
        context, ctx = open_browser(username, cookies)
        try:
            page = ctx.new_page()

            ensure_2fa(page, username)
            update_profile_name(page, name)
            update_billing_address(page, first_name, last_name, address)

            header("Application")
            apply_education(page, card_data, app_type=args.type)
        finally:
            context.__exit__(None, None, None)

        if args.report:
            header("Report")
            if send_report(args.report, username, card_data, address, args.type):
                log(f"Report sent → {args.report}")

        cleanup_profile(profile_name)

    print("\nDone!\n")


if __name__ == "__main__":
    main()

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
    print(f"  {msg}")


def header(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")


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

        profile_name = email

        header("Opening Browser")
        log(f"Profile: {profile_name}")
        context, ctx = open_browser_fresh(profile_name)
        try:
            page = ctx.new_page()

            header("Logging In")
            username = login_github(page, email, password)

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

        if args.report:
            header("Sending Report")
            if send_report(args.report, username, card_data, address, args.type):
                log(f"Report sent to: {args.report}")
            else:
                log("Report could not be sent")

        cleanup_profile(profile_name)
    else:
        cookies = load_cookies()
        username = get_username(cookies)
        profile_name = username

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

        if args.report:
            header("Sending Report")
            if send_report(args.report, username, card_data, address, args.type):
                log(f"Report sent to: {args.report}")
            else:
                log("Report could not be sent")

        cleanup_profile(profile_name)

    header("Complete")
    log("All tasks finished successfully!")
    print()


if __name__ == "__main__":
    main()

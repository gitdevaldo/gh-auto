import argparse
from dotenv import load_dotenv

load_dotenv()

from lib.card import get_card_data
from lib.cookies import load_cookies, get_username
from lib.address import get_random_address, split_name
from lib.browser import open_browser, open_browser_fresh
from lib.github import update_profile_name, update_billing_address, apply_education, ensure_2fa, login_github


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["faculty", "student"], default="faculty",
                        help="Education application type: faculty (teacher) or student")
    parser.add_argument("--login", type=str, default=None,
                        help="Login with email/username and password: email/username password")
    args, remaining = parser.parse_known_args()

    card_data = get_card_data()
    name = card_data["name"]

    first_name, last_name = split_name(name)
    print(f"Split name: first='{first_name}', last='{last_name}'")

    address = get_random_address()

    if args.login:
        email = args.login
        if remaining:
            password = remaining[0]
        else:
            raise Exception("Password is required after --login email/username")

        profile_name = email.split("@")[0] if "@" in email else email
        context, ctx = open_browser_fresh(profile_name)
        try:
            page = ctx.new_page()

            username = login_github(page, email, password)

            ensure_2fa(page, username)

            update_profile_name(page, name)

            update_billing_address(page, first_name, last_name, address)

            apply_education(page, card_data, app_type=args.type)
        finally:
            context.__exit__(None, None, None)
    else:
        cookies = load_cookies()
        username = get_username(cookies)
        print(f"Got username: {username}")

        context, ctx = open_browser(username, cookies)
        try:
            page = ctx.new_page()

            ensure_2fa(page, username)

            update_profile_name(page, name)

            update_billing_address(page, first_name, last_name, address)

            apply_education(page, card_data, app_type=args.type)
        finally:
            context.__exit__(None, None, None)

    print("All done!")


if __name__ == "__main__":
    main()

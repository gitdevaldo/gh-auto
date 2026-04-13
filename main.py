from dotenv import load_dotenv

load_dotenv()

from lib.card import get_card_name
from lib.cookies import load_cookies, get_username
from lib.address import get_random_address, split_name
from lib.browser import open_browser
from lib.github import update_profile_name, update_billing_address


def main():
    name = get_card_name()
    cookies = load_cookies()
    username = get_username(cookies)
    print(f"Got username: {username}")

    first_name, last_name = split_name(name)
    print(f"Split name: first='{first_name}', last='{last_name}'")

    address = get_random_address()

    context, ctx = open_browser(username, cookies)
    try:
        page = ctx.new_page()

        update_profile_name(page, name)

        update_billing_address(page, first_name, last_name, address)
    finally:
        context.__exit__(None, None, None)

    print("All done!")


if __name__ == "__main__":
    main()

from dotenv import load_dotenv

load_dotenv()

from lib.card import get_card_name
from lib.cookies import load_cookies, get_username
from lib.github import update_profile_name


def main():
    name = get_card_name()
    cookies = load_cookies()
    username = get_username(cookies)
    print(f"Got username: {username}")
    update_profile_name(name, cookies, username)


if __name__ == "__main__":
    main()

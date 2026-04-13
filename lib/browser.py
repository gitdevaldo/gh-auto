import os
from camoufox.sync_api import Camoufox
from lib.cookies import format_cookies

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILES_DIR = os.path.join(BASE_DIR, "profiles")


def get_profile_dir(username):
    profile_path = os.path.join(PROFILES_DIR, username)
    if not os.path.exists(profile_path):
        os.makedirs(profile_path, exist_ok=True)
        print(f"Created new browser profile: {profile_path}")
    else:
        print(f"Using existing browser profile: {profile_path}")
    return profile_path


def open_browser(username, cookies):
    profile_dir = get_profile_dir(username)
    context = Camoufox(headless=True, persistent_context=True, user_data_dir=profile_dir)
    ctx = context.__enter__()
    ctx.add_cookies(format_cookies(cookies))
    return context, ctx

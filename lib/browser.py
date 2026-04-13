import os
from camoufox.sync_api import Camoufox
from lib.cookies import format_cookies

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILES_DIR = os.path.join(BASE_DIR, "profiles")

INDO_GEO = {"latitude": -7.781354691702329, "longitude": 112.12809680508624}


def get_profile_dir(username):
    profile_path = os.path.join(PROFILES_DIR, username)
    if not os.path.exists(profile_path):
        os.makedirs(profile_path, exist_ok=True)
        print(f"Created new browser profile: {profile_path}")
    else:
        print(f"Using existing browser profile: {profile_path}")
    return profile_path


def open_browser(username, cookies, geolocation=None):
    profile_dir = get_profile_dir(username)
    geo = geolocation or INDO_GEO
    context = Camoufox(
        headless=True,
        persistent_context=True,
        user_data_dir=profile_dir,
        geoip=True,
        locale="id-ID",
        geolocation=geo,
        permissions=["geolocation"],
    )
    ctx = context.__enter__()
    ctx.add_cookies(format_cookies(cookies))
    return context, ctx

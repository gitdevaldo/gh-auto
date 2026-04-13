import os
from camoufox.sync_api import Camoufox
from browserforge.fingerprints import Screen
from lib.cookies import format_cookies

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILES_DIR = os.path.join(BASE_DIR, "profiles")

INDO_GEO = {"latitude": -7.781354691702329, "longitude": 112.12809680508624}


def get_profile_dir(profile_name):
    profile_path = os.path.join(PROFILES_DIR, profile_name)
    if not os.path.exists(profile_path):
        os.makedirs(profile_path, exist_ok=True)
    return profile_path


def open_browser(profile_name, cookies=None, geolocation=None, headless=False):
    profile_dir = get_profile_dir(profile_name)
    geo = geolocation or INDO_GEO
    context = Camoufox(
        headless=headless,
        persistent_context=True,
        user_data_dir=profile_dir,
        geoip=True,
        humanize=True,
        os='windows',
        screen=Screen(max_width=1521, max_height=695),
        locale="id-ID",
        geolocation=geo,
        permissions=["geolocation"],
    )
    ctx = context.__enter__()
    ctx.clear_cookies()
    if cookies:
        ctx.add_cookies(format_cookies(cookies))
    return context, ctx

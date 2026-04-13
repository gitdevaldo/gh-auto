import os
from camoufox.sync_api import Camoufox
from browserforge.fingerprints import Screen
from lib.cookies import format_cookies

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROFILES_DIR = os.path.join(BASE_DIR, "profiles")

INSTITUTION_GEO = {
    "smkn1ngawi": {"latitude": -7.4079, "longitude": 111.4492},
    "ubsi": {"latitude": -6.1753, "longitude": 106.8272},
    "iainkediri": {"latitude": -7.8160, "longitude": 112.0107},
    "unesa": {"latitude": -7.3019, "longitude": 112.7272},
    "uny": {"latitude": -7.7713, "longitude": 110.3863},
    "ui": {"latitude": -6.3616, "longitude": 106.8270},
    "ugm": {"latitude": -7.7713, "longitude": 110.3776},
    "itb": {"latitude": -6.8915, "longitude": 107.6107},
    "its": {"latitude": -7.2819, "longitude": 112.7953},
    "undip": {"latitude": -7.0496, "longitude": 110.4381},
    "unair": {"latitude": -7.2700, "longitude": 112.7600},
    "um": {"latitude": -7.9556, "longitude": 112.6148},
    "unj": {"latitude": -6.2088, "longitude": 106.8456},
    "upi": {"latitude": -6.8625, "longitude": 107.5942},
    "uns": {"latitude": -7.5580, "longitude": 110.8566},
    "unpad": {"latitude": -6.9271, "longitude": 107.7699},
    "unej": {"latitude": -8.1681, "longitude": 113.7168},
    "unsri": {"latitude": -2.9845, "longitude": 104.7340},
    "unhas": {"latitude": -5.1313, "longitude": 119.4881},
    "unand": {"latitude": -0.9139, "longitude": 100.4600},
    "ub": {"latitude": -7.9527, "longitude": 112.6146},
    "usu": {"latitude": 3.5632, "longitude": 98.6563},
}

DEFAULT_GEO = {"latitude": -7.2756, "longitude": 112.7526}


def get_geo_for_institution(institution):
    if not institution:
        return DEFAULT_GEO
    inst = institution.lower().strip()
    if inst in INSTITUTION_GEO:
        return INSTITUTION_GEO[inst]
    for key in INSTITUTION_GEO:
        if key in inst or inst in key:
            return INSTITUTION_GEO[key]
    return DEFAULT_GEO


def get_profile_dir(profile_name):
    profile_path = os.path.join(PROFILES_DIR, profile_name)
    if not os.path.exists(profile_path):
        os.makedirs(profile_path, exist_ok=True)
    return profile_path


def open_browser(profile_name, cookies=None, geolocation=None, headless=True, institution=None):
    profile_dir = get_profile_dir(profile_name)
    geo = geolocation or get_geo_for_institution(institution)
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

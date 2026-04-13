import base64
import json
import os
import re
from urllib.parse import parse_qs, urlencode

import pyotp

from lib.browser import open_browser

LOGIN_URL = "https://github.com/login"
PROFILE_URL = "https://github.com/settings/profile"
BILLING_URL = "https://github.com/settings/billing/payment_information"
EDUCATION_URL = "https://github.com/settings/education/benefits"
SECURITY_URL = "https://github.com/settings/security"
TWO_FA_SETUP_URL = "https://github.com/settings/two_factor_authentication/setup/intro"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OTP_DIR = os.path.join(BASE_DIR, "otp")

DELAY = 2000


def _log(msg):
    print(msg)


def _err(msg):
    print(f"[ERROR] {msg}")
    raise Exception(msg)


def _goto(page, url):
    page.goto(url)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(DELAY)


def login_github(page, email, password):
    _goto(page, LOGIN_URL)

    current_url = page.url
    if "github.com/login" not in current_url and "sessions/two-factor" not in current_url:
        _log("Already logged in — login skipped")
        return _get_username_from_page(page)

    if "sessions/two-factor" in current_url:
        _handle_login_2fa(page, email)
        username = _get_username_from_page(page)
        _log(f"Logged in as: {username}")
        return username

    login_field = page.locator('input#login_field')
    login_field.wait_for(state="visible", timeout=10000)
    page.wait_for_timeout(DELAY)
    login_field.fill(email)
    page.wait_for_timeout(DELAY)

    password_field = page.locator('input#password')
    password_field.fill(password)
    page.wait_for_timeout(DELAY)

    sign_in_btn = page.locator('input[name="commit"][value="Sign in"]')
    sign_in_btn.click()

    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)

    current_url = page.url
    if "sessions/two-factor" in current_url:
        _handle_login_2fa(page, email)
        username = _get_username_from_page(page)
        _log(f"Logged in as: {username}")
        return username

    if "github.com/login" in current_url:
        error_el = page.locator('.js-flash-alert, .flash-error, #js-flash-container .flash-error')
        if error_el.count() > 0:
            error_text = error_el.first.inner_text().strip()
            _err(f"Login failed — {error_text}")
        _err("Login failed — incorrect email/username or password")

    username = _get_username_from_page(page)
    _log(f"Logged in as: {username}")
    return username


def _find_otp_secret(login_identifier):
    if not os.path.exists(OTP_DIR):
        _err(
            f"OTP folder not found — no 2FA secrets saved yet. "
            f"Run the full flow first to set up 2FA for this account."
        )

    for folder_name in os.listdir(OTP_DIR):
        secret_path = os.path.join(OTP_DIR, folder_name, "secret.txt")
        if os.path.exists(secret_path):
            if login_identifier.lower() in folder_name.lower() or folder_name.lower() in login_identifier.lower():
                with open(secret_path, "r") as f:
                    return f.read().strip()

    exact_path = os.path.join(OTP_DIR, login_identifier, "secret.txt")
    if os.path.exists(exact_path):
        with open(exact_path, "r") as f:
            return f.read().strip()

    available = [d for d in os.listdir(OTP_DIR) if os.path.isdir(os.path.join(OTP_DIR, d))]
    _err(
        f"No OTP secret found for '{login_identifier}'. "
        f"Available accounts: {available if available else 'none'}. "
        f"Run the full flow first to set up 2FA and save the secret."
    )


def _handle_login_2fa(page, login_identifier):
    secret = _find_otp_secret(login_identifier)

    totp = pyotp.TOTP(secret)
    otp_code = totp.now()

    otp_input = page.locator('input#app_totp')
    otp_input.wait_for(state="visible", timeout=10000)
    page.wait_for_timeout(DELAY)
    otp_input.fill("")
    otp_input.type(otp_code, delay=100)

    page.wait_for_timeout(3000)

    current_url = page.url
    if "sessions/two-factor" not in current_url:
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(DELAY)
        return

    verify_btn = page.locator('button[type="submit"]:has-text("Verify")')
    if verify_btn.count() > 0 and verify_btn.first.is_visible():
        verify_btn.first.click(timeout=5000)
        page.wait_for_timeout(5000)
        page.wait_for_load_state("domcontentloaded")
        page.wait_for_timeout(DELAY)

    current_url = page.url
    if "sessions/two-factor" in current_url:
        _err("2FA verification failed — OTP code was rejected. Check if the saved secret is still valid.")


def _get_username_from_page(page):
    username = None
    cookies = page.context.cookies()
    for cookie in cookies:
        if cookie["name"] == "dotcom_user":
            username = cookie["value"]
            break

    if not username:
        meta = page.locator('meta[name="user-login"]')
        if meta.count() > 0:
            username = meta.get_attribute("content")

    if not username:
        page.wait_for_timeout(DELAY)
        page.goto("https://github.com")
        page.wait_for_load_state("networkidle")
        page.wait_for_timeout(DELAY)

        cookies = page.context.cookies()
        for cookie in cookies:
            if cookie["name"] == "dotcom_user":
                username = cookie["value"]
                break

        if not username:
            meta = page.locator('meta[name="user-login"]')
            if meta.count() > 0:
                username = meta.get_attribute("content")

    if not username:
        _err("Could not determine username — no 'dotcom_user' cookie or user meta tag found")

    return username


def ensure_2fa(page, username):
    _goto(page, SECURITY_URL)

    not_enabled = page.query_selector('h2.blankslate-heading')
    if not_enabled and "not enabled yet" in not_enabled.inner_text().strip().lower():
        return _setup_2fa(page, username)
    else:
        _log("2FA already set up")
        return None


def _setup_2fa(page, username):
    user_otp_dir = os.path.join(OTP_DIR, username)
    os.makedirs(user_otp_dir, exist_ok=True)

    enable_btn = page.locator('a[href="/settings/two_factor_authentication/setup/intro"]')
    enable_btn.wait_for(state="visible", timeout=10000)
    page.wait_for_timeout(DELAY)
    enable_btn.click()

    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(DELAY)

    setup_key_btn = page.locator('span.Button-label:has-text("setup key")')
    setup_key_btn.wait_for(state="visible", timeout=15000)
    page.wait_for_timeout(DELAY)
    setup_key_btn.click()

    page.wait_for_timeout(DELAY)

    secret_el = page.locator('[data-target="two-factor-setup-verification.mashedSecret"]')
    secret_el.wait_for(state="visible", timeout=10000)
    page.wait_for_timeout(DELAY)
    secret = secret_el.inner_text().strip()

    secret_path = os.path.join(user_otp_dir, "secret.txt")
    with open(secret_path, "w") as f:
        f.write(secret)
    _log(f"TOTP secret saved")

    page.wait_for_timeout(DELAY)

    page.keyboard.press("Escape")

    page.wait_for_timeout(DELAY)

    totp = pyotp.TOTP(secret)
    otp_code = totp.now()

    otp_input = page.locator('input[data-target="two-factor-setup-verification.appOtpInput"]')
    otp_input.wait_for(state="visible", timeout=10000)
    page.wait_for_timeout(DELAY)
    otp_input.fill("")
    otp_input.type(otp_code, delay=100)

    page.wait_for_timeout(3000)

    download_btn = page.locator('button[data-action="click:two-factor-setup-recovery-codes#onDownloadClick"]')
    download_btn.wait_for(state="visible", timeout=30000)

    page.wait_for_timeout(DELAY)

    recovery_codes_text = _scrape_recovery_codes(page)
    page.wait_for_timeout(DELAY)

    recovery_path = os.path.join(user_otp_dir, "recovery_codes.txt")
    try:
        with page.expect_download(timeout=10000) as download_info:
            download_btn.click()
        download = download_info.value
        page.wait_for_timeout(DELAY)
        download.save_as(recovery_path)
    except Exception:
        with open(recovery_path, "w") as f:
            f.write(recovery_codes_text)

    _log("Recovery codes saved")

    page.wait_for_timeout(DELAY)

    continue_btn = page.get_by_role("button", name="I have saved my recovery codes")
    continue_btn.wait_for(state="visible", timeout=10000)
    page.wait_for_timeout(DELAY)
    continue_btn.click()

    page.wait_for_timeout(5000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(DELAY)

    _log("2FA enabled")
    return secret


def _scrape_recovery_codes(page):
    code_elements = page.locator('li.recovery-code, .recovery-codes li, [class*="recovery"] li')
    codes = []
    for i in range(code_elements.count()):
        text = code_elements.nth(i).inner_text().strip()
        if text:
            codes.append(text)
    if codes:
        return "\n".join(codes)

    container = page.locator('.recovery-codes, [data-target*="recovery"], pre, code')
    for i in range(container.count()):
        text = container.nth(i).inner_text().strip()
        if text and len(text) > 20:
            return text

    return ""


def update_profile_name(page, name):
    _goto(page, PROFILE_URL)

    name_input = page.query_selector('input[name="user[profile_name]"]')
    if not name_input:
        _err("Profile update failed — name input field not found on the page")

    name_input.fill("")
    page.wait_for_timeout(DELAY)
    name_input.type(name)
    page.wait_for_timeout(DELAY)

    submit_btn = page.query_selector('button[type="submit"] .Button-label')
    if not submit_btn:
        submit_btn = page.query_selector('button[type="submit"]')
    if not submit_btn:
        _err("Profile update failed — submit button not found on the page")

    submit_btn.click()

    page.wait_for_timeout(3000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(DELAY)

    _log(f"Profile updated: {name}")


def update_billing_address(page, first_name, last_name, address):
    _goto(page, BILLING_URL)

    form_already_visible = page.locator('#billing_contact_first_name').is_visible()

    if not form_already_visible:
        edit_btn = page.locator('button.js-edit-user-personal-profile')
        if edit_btn.count() > 0:
            edit_btn.first.evaluate("btn => btn.click()")
            page.wait_for_timeout(DELAY)

    page.wait_for_selector('#billing_contact_first_name', state="visible", timeout=15000)
    page.wait_for_timeout(DELAY)

    def fill_input(selector, value):
        el = page.query_selector(selector)
        if el:
            el.fill("")
            page.wait_for_timeout(500)
            el.type(value)
            page.wait_for_timeout(500)

    fill_input('#billing_contact_first_name', first_name)
    fill_input('#billing_contact_last_name', last_name)
    fill_input('#billing_contact_address1', address['address_line'])
    fill_input('#billing_contact_city', address['city'])

    country_select = page.query_selector('#billing_contact_country_code')
    if country_select:
        page.select_option('#billing_contact_country_code', 'ID')
        page.wait_for_timeout(DELAY)

    fill_input('#region_region', address['state_province'])
    fill_input('#billing_contact_postal_code', address['postal_code'])

    page.wait_for_timeout(DELAY)

    save_btn = page.query_selector('button[value="Save billing information"]')
    if not save_btn:
        save_btn = page.query_selector('button[type="submit"].Button--primary')
    if not save_btn:
        _err("Billing update failed — save button not found on the page")

    save_btn.click()

    page.wait_for_timeout(3000)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(DELAY)

    _log(f"Billing updated: {address['city']}, {address['state_province']}")


def _build_photo_proof(image_b64):
    mime_match = re.match(r'^data:(image/\w+);', image_b64)
    if mime_match:
        mime_type = mime_match.group(1)
        data_url = image_b64
    else:
        mime_type = "image/jpeg"
        data_url = f"data:{mime_type};base64,{image_b64}"

    ext = mime_type.split("/")[1]
    return json.dumps({
        "image": data_url,
        "metadata": {
            "filename": f"camera.{ext}",
            "type": "camera",
            "mimeType": mime_type,
            "deviceLabel": "USB2.0 HD UVC WebCam (322e:2103)",
        },
    })


def _make_intercept_handler(photo_proof_json):
    def handle(route):
        request = route.request
        body = request.post_data or ""
        params = parse_qs(body, keep_blank_values=True)

        key = "dev_pack_form[photo_proof]"
        if key in params:
            params[key] = [photo_proof_json]

        new_body = urlencode(params, doseq=True)
        route.continue_(post_data=new_body)

    return handle


def apply_education(page, card_data, app_type="faculty"):
    school_name = card_data.get("schoolName", "")
    image_b64 = card_data.get("imageBase64", "")

    if not school_name:
        _err("Education application failed — card data missing 'schoolName'")
    if not image_b64:
        _err("Education application failed — card data missing 'imageBase64'")

    photo_proof_json = _build_photo_proof(image_b64)

    page.route("**/settings/education/developer_pack_applications", _make_intercept_handler(photo_proof_json))

    _goto(page, EDUCATION_URL)

    start_btn = page.wait_for_selector('#dialog-show-education-benefits-dialog', state="visible", timeout=15000)
    page.wait_for_timeout(DELAY)
    start_btn.click()

    page.wait_for_timeout(DELAY)

    if app_type == "faculty":
        radio_id = "#dev_pack_form_application_type_faculty"
    else:
        radio_id = "#dev_pack_form_application_type_student"

    radio = page.wait_for_selector(radio_id, state="visible", timeout=10000)
    page.wait_for_timeout(DELAY)
    radio.click()

    page.wait_for_timeout(DELAY)

    school_input = page.wait_for_selector('#js-school-name-search', state="visible", timeout=10000)
    page.wait_for_timeout(DELAY)
    school_input.fill("")
    school_input.type(school_name, delay=100)

    page.wait_for_timeout(3000)

    page.wait_for_selector(
        '#js-school-name-list .ActionListItem.js-school-autocomplete-result-selection',
        state="visible",
        timeout=15000,
    )
    page.wait_for_timeout(DELAY)

    all_options = page.query_selector_all(
        '#js-school-name-list .ActionListItem.js-school-autocomplete-result-selection'
    )

    best_match = None
    school_name_lower = school_name.strip().lower()
    for opt in all_options:
        opt_name = opt.get_attribute('data-school-name') or opt.inner_text().strip()
        if opt_name.strip().lower() == school_name_lower:
            best_match = opt
            break

    if not best_match:
        best_match = all_options[0]

    selected_name = best_match.get_attribute('data-school-name') or best_match.inner_text().strip()
    best_match.click()

    page.wait_for_timeout(DELAY)

    input_val = school_input.input_value()
    if not input_val.strip():
        _err("Education application failed — school selection didn't register, input is empty")

    share_btn = page.query_selector('button:has-text("Share Location")')
    if share_btn and share_btn.is_visible():
        page.wait_for_timeout(DELAY)
        share_btn.click()
        page.wait_for_timeout(3000)

    page.wait_for_timeout(DELAY)

    continue_btn = page.wait_for_selector('#js-developer-pack-application-submit-button', state="visible", timeout=10000)

    if continue_btn.is_disabled():
        _err("Education application failed — continue button is disabled, step 1 requirements not met")

    page.wait_for_timeout(DELAY)
    continue_btn.click()

    page.wait_for_timeout(5000)

    if app_type == "student":
        proof_btn = page.wait_for_selector('button:has-text("Select...")', state="visible", timeout=10000)
        page.wait_for_timeout(DELAY)
        proof_btn.click()

        page.wait_for_timeout(DELAY)
        id_card_option = page.wait_for_selector('[role="option"]:has-text("ID")', state="visible", timeout=10000)
        id_card_option.click()

        page.wait_for_timeout(DELAY)

    submit_btn = page.wait_for_selector('#js-developer-pack-application-submit-button', state="visible", timeout=15000)

    if submit_btn.is_disabled():
        _err("Education application failed — submit button is disabled, step 2 requirements not met")

    page.wait_for_timeout(DELAY)
    submit_btn.click()

    page.wait_for_timeout(5000)

    location_mismatch = page.query_selector('#dev_pack_form_far_from_campus_reason_distant_course_work')
    if location_mismatch and location_mismatch.is_visible():

        page.wait_for_timeout(DELAY)
        distance_radio = page.query_selector('#dev_pack_form_far_from_campus_reason_distant_course_work')
        distance_radio.click()

        page.wait_for_timeout(DELAY)

        reason_input = page.query_selector('#dev_pack_form_other_reason_text')
        if reason_input and reason_input.is_visible():
            reason_input.fill("")
            page.wait_for_timeout(DELAY)
            reason_input.type("My education program uses a distance learning method", delay=50)
            page.wait_for_timeout(DELAY)

        final_submit = page.wait_for_selector('#js-developer-pack-application-submit-button', state="visible", timeout=15000)

        if final_submit.is_disabled():
            _err("Education application failed — submit button is disabled, step 3 requirements not met")

        page.wait_for_timeout(DELAY)
        final_submit.click()

        page.wait_for_timeout(5000)

    banner = page.query_selector('.Banner-message .Banner-title')
    if banner and "Your application has been submitted" in banner.inner_text().strip():
        _log("Application submitted")
    else:
        _log(f"Application status unclear — {page.url}")

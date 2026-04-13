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


def _log(msg):
    print(f"  {msg}")


def login_github(page, email, password):
    page.goto(LOGIN_URL)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)

    current_url = page.url
    if "github.com/login" not in current_url and "sessions/two-factor" not in current_url:
        _log("Already logged in — login skipped")
        return _get_username_from_page(page)

    if "sessions/two-factor" in current_url:
        _log("2FA verification required — session resuming")
        _handle_login_2fa(page, email)
        username = _get_username_from_page(page)
        _log(f"Logged in as: {username}")
        return username

    login_field = page.locator('input#login_field')
    login_field.wait_for(state="visible", timeout=10000)
    page.wait_for_timeout(500)
    login_field.fill(email)

    password_field = page.locator('input#password')
    page.wait_for_timeout(500)
    password_field.fill(password)

    page.wait_for_timeout(1000)

    sign_in_btn = page.locator('input[name="commit"][value="Sign in"]')
    sign_in_btn.click()

    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)

    current_url = page.url
    if "sessions/two-factor" in current_url:
        _log("2FA verification required after login")
        _handle_login_2fa(page, email)
        username = _get_username_from_page(page)
        _log(f"Logged in as: {username}")
        return username

    if "github.com/login" in current_url:
        error_el = page.locator('.js-flash-alert, .flash-error, #js-flash-container .flash-error')
        if error_el.count() > 0:
            error_text = error_el.first.inner_text().strip()
            raise Exception(f"Login failed: {error_text}")
        raise Exception("Login failed: still on login page")

    username = _get_username_from_page(page)
    _log(f"Logged in as: {username}")
    return username


def _find_otp_secret(login_identifier):
    otp_dir = OTP_DIR
    if not os.path.exists(otp_dir):
        raise Exception(f"OTP folder not found at {otp_dir} — cannot verify 2FA. Run 2FA setup first.")

    for folder_name in os.listdir(otp_dir):
        secret_path = os.path.join(otp_dir, folder_name, "secret.txt")
        if os.path.exists(secret_path):
            if login_identifier.lower() in folder_name.lower() or folder_name.lower() in login_identifier.lower():
                with open(secret_path, "r") as f:
                    return f.read().strip()

    exact_path = os.path.join(otp_dir, login_identifier, "secret.txt")
    if os.path.exists(exact_path):
        with open(exact_path, "r") as f:
            return f.read().strip()

    available = [d for d in os.listdir(otp_dir) if os.path.isdir(os.path.join(otp_dir, d))]
    raise Exception(
        f"No OTP secret found for '{login_identifier}'. "
        f"Available OTP folders: {available}. "
        f"Run the full flow first to set up 2FA and save the secret."
    )


def _handle_login_2fa(page, login_identifier):
    secret = _find_otp_secret(login_identifier)

    totp = pyotp.TOTP(secret)
    otp_code = totp.now()

    otp_input = page.locator('input#app_totp')
    otp_input.wait_for(state="visible", timeout=10000)
    page.wait_for_timeout(1000)
    otp_input.fill("")
    otp_input.type(otp_code, delay=100)

    page.wait_for_timeout(1000)

    verify_btn = page.locator('button[type="submit"]:has-text("Verify")')
    verify_btn.click()
    _log("OTP verified")

    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(3000)

    current_url = page.url
    if "sessions/two-factor" in current_url:
        raise Exception("2FA verification failed — still on verification page")


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
        raise Exception("Could not determine username")

    return username


def ensure_2fa(page, username):
    page.goto(SECURITY_URL)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)

    not_enabled = page.query_selector('h2.blankslate-heading')
    if not_enabled and "not enabled yet" in not_enabled.inner_text().strip().lower():
        _log("2FA not enabled — setting up...")
        return _setup_2fa(page, username)
    else:
        _log("2FA already enabled — skipping")
        return None


def _setup_2fa(page, username):
    user_otp_dir = os.path.join(OTP_DIR, username)
    os.makedirs(user_otp_dir, exist_ok=True)

    enable_btn = page.locator('a[href="/settings/two_factor_authentication/setup/intro"]')
    enable_btn.wait_for(state="visible", timeout=10000)
    page.wait_for_timeout(1000)
    enable_btn.click()

    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)

    setup_key_btn = page.locator('span.Button-label:has-text("setup key")')
    setup_key_btn.wait_for(state="visible", timeout=15000)
    page.wait_for_timeout(1000)
    setup_key_btn.click()

    page.wait_for_timeout(2000)

    secret_el = page.locator('[data-target="two-factor-setup-verification.mashedSecret"]')
    secret_el.wait_for(state="visible", timeout=10000)
    secret = secret_el.inner_text().strip()

    secret_path = os.path.join(user_otp_dir, "secret.txt")
    with open(secret_path, "w") as f:
        f.write(secret)
    _log(f"TOTP secret saved to {secret_path}")

    page.wait_for_timeout(1000)

    page.keyboard.press("Escape")

    page.wait_for_timeout(1500)

    totp = pyotp.TOTP(secret)
    otp_code = totp.now()

    otp_input = page.locator('input[data-target="two-factor-setup-verification.appOtpInput"]')
    otp_input.wait_for(state="visible", timeout=10000)
    page.wait_for_timeout(1000)
    otp_input.fill("")
    otp_input.type(otp_code, delay=100)
    _log("OTP code entered — waiting for verification...")

    page.wait_for_timeout(3000)

    download_btn = page.locator('button[data-action="click:two-factor-setup-recovery-codes#onDownloadClick"]')
    download_btn.wait_for(state="visible", timeout=30000)

    page.wait_for_timeout(2000)

    recovery_codes_text = _scrape_recovery_codes(page)
    page.wait_for_timeout(1000)

    try:
        with page.expect_download(timeout=10000) as download_info:
            download_btn.click()
        download = download_info.value
        page.wait_for_timeout(2000)
        recovery_path = os.path.join(user_otp_dir, "recovery_codes.txt")
        download.save_as(recovery_path)
    except Exception:
        recovery_path = os.path.join(user_otp_dir, "recovery_codes.txt")
        with open(recovery_path, "w") as f:
            f.write(recovery_codes_text)

    _log(f"Recovery codes saved to {recovery_path}")

    page.wait_for_timeout(1500)

    continue_btn = page.get_by_role("button", name="I have saved my recovery codes")
    continue_btn.wait_for(state="visible", timeout=10000)
    page.wait_for_timeout(1000)
    continue_btn.click()

    page.wait_for_timeout(5000)

    _log("2FA enabled successfully")
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
    page.goto(PROFILE_URL)
    page.wait_for_load_state("domcontentloaded")

    name_input = page.query_selector('input[name="user[profile_name]"]')
    if not name_input:
        raise Exception("Could not find name input on the page")

    name_input.fill("")
    name_input.type(name)

    submit_btn = page.query_selector('button[type="submit"] .Button-label')
    if not submit_btn:
        submit_btn = page.query_selector('button[type="submit"]')
    if not submit_btn:
        raise Exception("Could not find submit button on the page")

    page.wait_for_timeout(500)

    with page.expect_navigation(wait_until="domcontentloaded", timeout=15000):
        submit_btn.click()

    _log(f"Profile name set to: {name}")


def update_billing_address(page, first_name, last_name, address):
    page.goto(BILLING_URL)
    page.wait_for_load_state("domcontentloaded")

    edit_btn = page.query_selector('button.js-edit-user-personal-profile')
    if not edit_btn:
        edit_btn = page.query_selector('button.js-add-billing-information-btn')
    if not edit_btn:
        raise Exception("Could not find Edit billing button on the page")

    edit_btn.click()

    page.wait_for_selector('#billing_contact_first_name', state="visible", timeout=10000)

    def fill_input(selector, value):
        el = page.query_selector(selector)
        if el:
            el.fill("")
            el.type(value)

    fill_input('#billing_contact_first_name', first_name)
    fill_input('#billing_contact_last_name', last_name)
    fill_input('#billing_contact_address1', address['address_line'])
    fill_input('#billing_contact_city', address['city'])

    country_select = page.query_selector('#billing_contact_country_code')
    if country_select:
        page.select_option('#billing_contact_country_code', 'ID')
        page.wait_for_timeout(500)

    fill_input('#region_region', address['state_province'])
    fill_input('#billing_contact_postal_code', address['postal_code'])

    page.wait_for_timeout(500)

    save_btn = page.query_selector('button[value="Save billing information"]')
    if not save_btn:
        save_btn = page.query_selector('button[type="submit"].Button--primary')
    if not save_btn:
        raise Exception("Could not find Save billing button")

    save_btn.click()

    page.wait_for_timeout(2000)

    _log(f"Billing address updated — {address['city']}, {address['state_province']}")


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
        raise Exception("Card API did not return school_name")
    if not image_b64:
        raise Exception("Card API did not return image")

    photo_proof_json = _build_photo_proof(image_b64)

    page.route("**/settings/education/developer_pack_applications", _make_intercept_handler(photo_proof_json))

    page.goto(EDUCATION_URL)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)

    start_btn = page.wait_for_selector('#dialog-show-education-benefits-dialog', state="visible", timeout=15000)
    page.wait_for_timeout(1000)
    start_btn.click()

    page.wait_for_timeout(2000)

    if app_type == "faculty":
        radio_id = "#dev_pack_form_application_type_faculty"
    else:
        radio_id = "#dev_pack_form_application_type_student"

    radio = page.wait_for_selector(radio_id, state="visible", timeout=10000)
    page.wait_for_timeout(1000)
    radio.click()
    _log(f"Application type: {app_type}")

    page.wait_for_timeout(1500)

    school_input = page.wait_for_selector('#js-school-name-search', state="visible", timeout=10000)
    page.wait_for_timeout(500)
    school_input.fill("")
    school_input.type(school_name, delay=100)

    page.wait_for_timeout(2000)

    page.wait_for_selector(
        '#js-school-name-list .ActionListItem.js-school-autocomplete-result-selection',
        state="visible",
        timeout=15000,
    )
    page.wait_for_timeout(1000)

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
    _log(f"School selected: {selected_name}")

    page.wait_for_timeout(2000)

    input_val = school_input.input_value()
    if not input_val.strip():
        raise Exception("School selection failed — input is empty after clicking option")

    share_btn = page.query_selector('button:has-text("Share Location")')
    if share_btn and share_btn.is_visible():
        page.wait_for_timeout(1000)
        share_btn.click()
        _log("Location shared")
        page.wait_for_timeout(3000)

    page.wait_for_timeout(1000)

    continue_btn = page.wait_for_selector('#js-developer-pack-application-submit-button', state="visible", timeout=10000)

    if continue_btn.is_disabled():
        raise Exception("Continue button is disabled. Step 1 requirements not met.")

    page.wait_for_timeout(1000)
    continue_btn.click()
    _log("Step 1 completed — continuing...")

    page.wait_for_timeout(5000)

    if app_type == "student":
        proof_btn = page.wait_for_selector('button:has-text("Select...")', state="visible", timeout=10000)
        page.wait_for_timeout(1000)
        proof_btn.click()

        page.wait_for_timeout(1000)
        id_card_option = page.wait_for_selector('[role="option"]:has-text("ID")', state="visible", timeout=10000)
        id_card_option.click()
        _log("Proof type: ID Card")

        page.wait_for_timeout(1500)

    submit_btn = page.wait_for_selector('#js-developer-pack-application-submit-button', state="visible", timeout=15000)

    if submit_btn.is_disabled():
        raise Exception("Submit button is disabled. Step 2 requirements not met.")

    page.wait_for_timeout(1000)
    submit_btn.click()
    _log("Step 2 completed — submitting...")

    page.wait_for_timeout(5000)

    location_mismatch = page.query_selector('#dev_pack_form_far_from_campus_reason_distant_course_work')
    if location_mismatch and location_mismatch.is_visible():
        _log("Location mismatch detected — handling step 3...")

        page.wait_for_timeout(1000)
        distance_radio = page.query_selector('#dev_pack_form_far_from_campus_reason_distant_course_work')
        distance_radio.click()

        page.wait_for_timeout(1000)

        reason_input = page.query_selector('#dev_pack_form_other_reason_text')
        if reason_input and reason_input.is_visible():
            reason_input.fill("")
            reason_input.type("My education program uses a distance learning method", delay=50)
            page.wait_for_timeout(1000)

        final_submit = page.wait_for_selector('#js-developer-pack-application-submit-button', state="visible", timeout=15000)

        if final_submit.is_disabled():
            raise Exception("Final submit button is disabled. Step 3 requirements not met.")

        page.wait_for_timeout(1000)
        final_submit.click()
        _log("Step 3 completed — final submission...")

        page.wait_for_timeout(5000)

    banner = page.query_selector('.Banner-message .Banner-title')
    if banner and "Your application has been submitted" in banner.inner_text().strip():
        _log("Application submitted successfully!")
    else:
        _log(f"Application status unclear — check: {page.url}")

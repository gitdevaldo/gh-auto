import base64
import json
import re
from urllib.parse import parse_qs, urlencode

from lib.browser import open_browser

PROFILE_URL = "https://github.com/settings/profile"
BILLING_URL = "https://github.com/settings/billing/payment_information"
EDUCATION_URL = "https://github.com/settings/education/benefits"


def update_profile_name(page, name):
    page.goto(PROFILE_URL)
    page.wait_for_load_state("domcontentloaded")

    name_input = page.query_selector('input[name="user[profile_name]"]')
    if not name_input:
        raise Exception("Could not find name input on the page")

    name_input.fill("")
    name_input.type(name)
    print(f"Filled name field with: {name}")

    submit_btn = page.query_selector('button[type="submit"] .Button-label')
    if not submit_btn:
        submit_btn = page.query_selector('button[type="submit"]')
    if not submit_btn:
        raise Exception("Could not find submit button on the page")

    page.wait_for_timeout(500)

    with page.expect_navigation(wait_until="domcontentloaded", timeout=15000):
        submit_btn.click()

    final_url = page.url
    print(f"After submit, landed on: {final_url}")

    if "settings/profile" in final_url:
        flash = page.query_selector('.flash-success, .flash-notice')
        if flash:
            print(f"Profile updated successfully! Message: {flash.inner_text().strip()}")
        else:
            print("Profile updated successfully!")
    else:
        print(f"Unexpected result. Current URL: {final_url}")


def update_billing_address(page, first_name, last_name, address):
    page.goto(BILLING_URL)
    page.wait_for_load_state("domcontentloaded")

    edit_btn = page.query_selector('button.js-edit-user-personal-profile')
    if not edit_btn:
        edit_btn = page.query_selector('button.js-add-billing-information-btn')
    if not edit_btn:
        raise Exception("Could not find Edit billing button on the page")

    edit_btn.click()
    print("Clicked Edit billing button, waiting for form...")

    page.wait_for_selector('#billing_contact_first_name', state="visible", timeout=10000)
    print("Billing form appeared")

    def fill_input(selector, value):
        el = page.query_selector(selector)
        if el:
            el.fill("")
            el.type(value)
            print(f"  Filled {selector} with: {value}")
        else:
            print(f"  WARNING: Could not find {selector}")

    fill_input('#billing_contact_first_name', first_name)
    fill_input('#billing_contact_last_name', last_name)
    fill_input('#billing_contact_address1', address['address_line'])
    fill_input('#billing_contact_city', address['city'])

    country_select = page.query_selector('#billing_contact_country_code')
    if country_select:
        page.select_option('#billing_contact_country_code', 'ID')
        print("  Selected country: Indonesia (ID)")
        page.wait_for_timeout(500)
    else:
        print("  WARNING: Could not find country select")

    fill_input('#region_region', address['state_province'])
    fill_input('#billing_contact_postal_code', address['postal_code'])

    page.wait_for_timeout(500)

    save_btn = page.query_selector('button[value="Save billing information"]')
    if not save_btn:
        save_btn = page.query_selector('button[type="submit"].Button--primary')
    if not save_btn:
        raise Exception("Could not find Save billing button")

    save_btn.click()
    print("Clicked Save billing information")

    page.wait_for_timeout(2000)

    flash = page.query_selector('.flash-success, .flash-notice')
    if flash:
        print(f"Billing updated successfully! Message: {flash.inner_text().strip()}")
    else:
        print("Billing information saved.")


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
            print("Intercepted POST: replaced photo_proof with camera-faked blob")

        new_body = urlencode(params, doseq=True)
        route.continue_(post_data=new_body)

    return handle


def apply_education(page, card_data, app_type="faculty"):
    school_name = card_data.get("school_name", "")
    image_b64 = card_data.get("image", "")

    if not school_name:
        raise Exception("Card API did not return school_name")
    if not image_b64:
        raise Exception("Card API did not return image")

    photo_proof_json = _build_photo_proof(image_b64)

    page.route("**/settings/education/developer_pack_applications", _make_intercept_handler(photo_proof_json))
    print("Route interceptor installed for developer_pack_applications")

    page.goto(EDUCATION_URL)
    page.wait_for_load_state("domcontentloaded")
    print("Navigated to education benefits page")

    start_btn = page.wait_for_selector('#dialog-show-education-benefits-dialog', state="visible", timeout=10000)
    start_btn.click()
    print("Clicked 'Start an application'")

    if app_type == "faculty":
        radio_id = "#dev_pack_form_application_type_faculty"
    else:
        radio_id = "#dev_pack_form_application_type_student"

    radio = page.wait_for_selector(radio_id, state="visible", timeout=10000)
    radio.click()
    print(f"Selected application type: {app_type}")

    school_input = page.wait_for_selector('#js-school-name-search', state="visible", timeout=10000)
    school_input.fill("")
    school_input.type(school_name, delay=80)
    print(f"Typed school name: {school_name}")

    school_list = page.wait_for_selector('#js-school-name-list [role="option"]', state="visible", timeout=10000)
    school_list.click()
    print("Selected school from dropdown")

    page.wait_for_timeout(500)

    share_btn = page.wait_for_selector('button:has-text("Share Location")', state="visible", timeout=10000)
    share_btn.click()
    print("Clicked 'Share Location' — geolocation already granted via context")

    page.wait_for_timeout(2000)

    continue_btn = page.wait_for_selector('#js-developer-pack-application-submit-button', state="visible", timeout=10000)
    continue_btn.click()
    print("Clicked 'Continue'")

    page.wait_for_timeout(2000)

    if app_type == "student":
        proof_btn = page.wait_for_selector('button:has-text("Select...")', state="visible", timeout=10000)
        proof_btn.click()
        print("Opened proof type selector")

        id_card_option = page.wait_for_selector('[role="option"]:has-text("ID")', state="visible", timeout=10000)
        id_card_option.click()
        print("Selected proof type: ID Card")

        page.wait_for_timeout(500)

    submit_btn = page.wait_for_selector('#js-developer-pack-application-submit-button', state="visible", timeout=15000)
    submit_btn.click()
    print("Clicked 'Submit Application'")

    page.wait_for_timeout(3000)

    banner = page.query_selector('.Banner-message')
    if banner:
        msg = banner.inner_text().strip()
        print(f"Education application result: {msg}")
    else:
        print("Submit completed — checking page state...")
        print(f"Current URL: {page.url}")

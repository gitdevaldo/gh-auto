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
    school_name = card_data.get("schoolName", "")
    image_b64 = card_data.get("imageBase64", "")

    if not school_name:
        raise Exception("Card API did not return school_name")
    if not image_b64:
        raise Exception("Card API did not return image")

    photo_proof_json = _build_photo_proof(image_b64)

    page.route("**/settings/education/developer_pack_applications", _make_intercept_handler(photo_proof_json))
    print("Route interceptor installed for developer_pack_applications")

    page.goto(EDUCATION_URL)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(2000)
    print("Navigated to education benefits page")

    start_btn = page.wait_for_selector('#dialog-show-education-benefits-dialog', state="visible", timeout=15000)
    page.wait_for_timeout(1000)
    start_btn.click()
    print("Clicked 'Start an application'")

    page.wait_for_timeout(2000)

    if app_type == "faculty":
        radio_id = "#dev_pack_form_application_type_faculty"
    else:
        radio_id = "#dev_pack_form_application_type_student"

    radio = page.wait_for_selector(radio_id, state="visible", timeout=10000)
    page.wait_for_timeout(1000)
    radio.click()
    print(f"Selected application type: {app_type}")

    page.wait_for_timeout(1500)

    school_input = page.wait_for_selector('#js-school-name-search', state="visible", timeout=10000)
    page.wait_for_timeout(500)
    school_input.fill("")
    school_input.type(school_name, delay=100)
    print(f"Typed school name: {school_name}")

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
    print(f"  Found {len(all_options)} school option(s) in dropdown")

    best_match = None
    school_name_lower = school_name.strip().lower()
    for opt in all_options:
        opt_name = opt.get_attribute('data-school-name') or opt.inner_text().strip()
        print(f"    Option: '{opt_name}'")
        if opt_name.strip().lower() == school_name_lower:
            best_match = opt
            break

    if not best_match:
        best_match = all_options[0]
        fallback_name = best_match.get_attribute('data-school-name') or best_match.inner_text().strip()
        print(f"  No exact match found, using first option: '{fallback_name}'")

    selected_name = best_match.get_attribute('data-school-name') or best_match.inner_text().strip()
    best_match.click()
    print(f"Selected school from dropdown: '{selected_name}'")

    page.wait_for_timeout(2000)

    input_val = school_input.input_value()
    print(f"  School input value after selection: '{input_val}'")
    if not input_val.strip():
        raise Exception("School selection failed — input is empty after clicking option")

    share_btn = page.query_selector('button:has-text("Share Location")')
    if share_btn and share_btn.is_visible():
        page.wait_for_timeout(1000)
        share_btn.click()
        print("Clicked 'Share Location' — geolocation already granted via context")
        page.wait_for_timeout(3000)
    else:
        print("  'Share Location' button not found or not visible, skipping")

    page.wait_for_timeout(1000)

    continue_btn = page.wait_for_selector('#js-developer-pack-application-submit-button', state="visible", timeout=10000)
    btn_text = continue_btn.inner_text().strip()
    print(f"  Continue button text: '{btn_text}'")

    if continue_btn.is_disabled():
        raise Exception("Continue button is disabled. Step 1 requirements not met.")

    page.wait_for_timeout(1000)
    continue_btn.click()
    print("Clicked 'Continue'")

    page.wait_for_timeout(5000)

    if app_type == "student":
        proof_btn = page.wait_for_selector('button:has-text("Select...")', state="visible", timeout=10000)
        page.wait_for_timeout(1000)
        proof_btn.click()
        print("Opened proof type selector")

        page.wait_for_timeout(1000)
        id_card_option = page.wait_for_selector('[role="option"]:has-text("ID")', state="visible", timeout=10000)
        id_card_option.click()
        print("Selected proof type: ID Card")

        page.wait_for_timeout(1500)

    submit_btn = page.wait_for_selector('#js-developer-pack-application-submit-button', state="visible", timeout=15000)
    submit_text = submit_btn.inner_text().strip()
    print(f"  Submit button text: '{submit_text}'")

    if submit_btn.is_disabled():
        raise Exception("Submit button is disabled. Step 2 requirements not met.")

    page.wait_for_timeout(1000)
    submit_btn.click()
    print("Clicked 'Submit Application'")

    page.wait_for_timeout(5000)

    location_mismatch = page.query_selector('#dev_pack_form_far_from_campus_reason_distant_course_work')
    if location_mismatch and location_mismatch.is_visible():
        print("Step 3 detected: location mismatch — need to provide reason")

        page.wait_for_timeout(1000)
        distance_radio = page.query_selector('#dev_pack_form_far_from_campus_reason_distant_course_work')
        distance_radio.click()
        print("  Selected: 'All coursework is via distance learning'")

        page.wait_for_timeout(1000)

        reason_input = page.query_selector('#dev_pack_form_other_reason_text')
        if reason_input and reason_input.is_visible():
            reason_input.fill("")
            reason_input.type("My education program uses a distance learning method", delay=50)
            print("  Filled reason text")
            page.wait_for_timeout(1000)

        final_submit = page.wait_for_selector('#js-developer-pack-application-submit-button', state="visible", timeout=15000)
        final_text = final_submit.inner_text().strip()
        print(f"  Final submit button text: '{final_text}'")

        if final_submit.is_disabled():
            raise Exception("Final submit button is disabled. Step 3 requirements not met.")

        page.wait_for_timeout(1000)
        final_submit.click()
        print("Clicked 'Submit Application' (step 3)")

        page.wait_for_timeout(5000)

    print(f"Current URL after submit: {page.url}")

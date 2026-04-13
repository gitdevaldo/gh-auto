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


def _get_step_indicator(page):
    step_el = page.query_selector('[data-current-step]')
    if step_el:
        return step_el.get_attribute('data-current-step')
    active_step = page.query_selector('.education-step.active, .education-step--current')
    if active_step:
        return active_step.get_attribute('data-step') or active_step.inner_text().strip()
    submit_btn = page.query_selector('#js-developer-pack-application-submit-button')
    if submit_btn:
        btn_text = submit_btn.inner_text().strip().lower()
        if "continue" in btn_text:
            return "step1"
        elif "submit" in btn_text:
            return "step2"
    return None


def _wait_for_step_change(page, previous_step, description, timeout=15000):
    import time
    deadline = time.time() + timeout / 1000
    while time.time() < deadline:
        error_el = page.query_selector('.flash-error, .flash-warn, .Banner--error')
        if error_el:
            page.screenshot(path="debug_step_error.png")
            raise Exception(f"Step transition failed ({description}): {error_el.inner_text().strip()}")

        current = _get_step_indicator(page)
        if current and current != previous_step:
            print(f"  Step advanced: '{previous_step}' -> '{current}' ({description})")
            return current
        page.wait_for_timeout(300)

    page.screenshot(path="debug_step_timeout.png")
    raise Exception(f"Step did not advance after '{description}' (timed out). Still on '{previous_step}'.")


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
    page.wait_for_load_state("domcontentloaded")
    print("Navigated to education benefits page")

    start_btn = page.wait_for_selector('#dialog-show-education-benefits-dialog', state="visible", timeout=10000)
    start_btn.click()
    print("Clicked 'Start an application'")

    page.wait_for_timeout(1000)

    if app_type == "faculty":
        radio_id = "#dev_pack_form_application_type_faculty"
    else:
        radio_id = "#dev_pack_form_application_type_student"

    radio = page.wait_for_selector(radio_id, state="visible", timeout=10000)
    radio.click()
    print(f"Selected application type: {app_type}")

    page.wait_for_timeout(500)

    school_input = page.wait_for_selector('#js-school-name-search', state="visible", timeout=10000)
    school_input.fill("")
    school_input.type(school_name, delay=100)
    print(f"Typed school name: {school_name}")

    page.wait_for_timeout(1500)

    page.wait_for_selector(
        '#js-school-name-list .ActionListItem.js-school-autocomplete-result-selection',
        state="visible",
        timeout=15000,
    )

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

    page.wait_for_timeout(1000)

    input_val = school_input.input_value()
    print(f"  School input value after selection: '{input_val}'")
    if not input_val.strip():
        page.screenshot(path="debug_school_not_selected.png")
        raise Exception("School selection failed — input is empty after clicking option")

    share_btn = page.query_selector('button:has-text("Share Location")')
    if share_btn and share_btn.is_visible():
        share_btn.click()
        print("Clicked 'Share Location' — geolocation already granted via context")
        page.wait_for_timeout(2000)
    else:
        print("  'Share Location' button not found or not visible, skipping")

    step_before = _get_step_indicator(page)
    print(f"  Current step indicator before Continue: '{step_before}'")

    continue_btn = page.wait_for_selector('#js-developer-pack-application-submit-button', state="visible", timeout=10000)
    btn_text_before = continue_btn.inner_text().strip()
    print(f"  Button text: '{btn_text_before}'")

    if continue_btn.is_disabled():
        print("  WARNING: Continue button is disabled — something may be missing in step 1")
        page.screenshot(path="debug_step1_disabled.png")
        raise Exception("Continue button is disabled. Step 1 requirements not met.")

    continue_btn.click()
    print("Clicked 'Continue'")

    step_after = _wait_for_step_change(page, step_before, "Continue to step 2", timeout=15000)
    print(f"  Confirmed step transition: now on '{step_after}'")

    if app_type == "student":
        proof_btn = page.wait_for_selector('button:has-text("Select...")', state="visible", timeout=10000)
        proof_btn.click()
        print("Opened proof type selector")

        id_card_option = page.wait_for_selector('[role="option"]:has-text("ID")', state="visible", timeout=10000)
        id_card_option.click()
        print("Selected proof type: ID Card")

        page.wait_for_timeout(500)

    submit_btn = page.wait_for_selector('#js-developer-pack-application-submit-button', state="visible", timeout=15000)
    print(f"  Submit button text: '{submit_btn.inner_text().strip()}'")

    if submit_btn.is_disabled():
        print("  WARNING: Submit button is disabled — step 2 requirements not met")
        page.screenshot(path="debug_step2_disabled.png")
        raise Exception("Submit button is disabled. Step 2 requirements not met.")

    submit_btn.click()
    print("Clicked 'Submit Application'")

    page.wait_for_timeout(5000)

    banner = page.query_selector('.Banner-message')
    if banner:
        msg = banner.inner_text().strip()
        print(f"Education application result: {msg}")
    else:
        error_el = page.query_selector('.flash-error, .flash-warn, .Banner--error')
        if error_el:
            err_msg = error_el.inner_text().strip()
            print(f"ERROR after submit: {err_msg}")
            page.screenshot(path="debug_submit_error.png")
            raise Exception(f"Submit failed: {err_msg}")
        else:
            print("Submit completed — checking page state...")
            print(f"Current URL: {page.url}")
            page.screenshot(path="debug_final_state.png")
            print("Saved screenshot of final state to debug_final_state.png")

from lib.browser import open_browser

PROFILE_URL = "https://github.com/settings/profile"
BILLING_URL = "https://github.com/settings/billing/payment_information"


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

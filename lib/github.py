from lib.browser import open_browser

PROFILE_URL = "https://github.com/settings/profile"


def update_profile_name(name, cookies, username):
    context, ctx = open_browser(username, cookies)

    try:
        page = ctx.new_page()
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
    finally:
        context.__exit__(None, None, None)

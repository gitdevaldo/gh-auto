# GitHub Profile Automation

## Overview

A minimal Python automation script that:
1. Calls a card generation API to fetch a name
2. Uses camoufox headless browser to update the GitHub public profile name
3. Fetches a random Indonesian address and updates GitHub billing information

All actions run inside a single camoufox browser session with persistent profiles.

## Project Structure

```
main.py                → Entry point, orchestrates the full flow
lib/
  __init__.py
  card.py              → Card API integration (fetch generated name)
  cookies.py           → Cookie loading, username extraction, formatting
  browser.py           → Camoufox browser setup, persistent profiles
  github.py            → GitHub automation actions (profile name, billing address)
  address.py           → Random address generation (mocloc.com API), name splitting
source-code/
  gitstud/             → Reference Chrome extension (GitHub Education helper)
cookies.json           → GitHub session cookies (user-provided, not committed)
profiles/              → Persistent browser profiles per username (gitignored)
.env                   → Environment variables
.env.example           → Environment variable template
requirements.txt       → Python dependencies
replit.nix             → System-level dependencies for headless browser
```

## Stack

- **Python**: 3.12
- **Browser automation**: camoufox (headless Firefox via Playwright)
- **HTTP client**: requests
- **Config**: python-dotenv

## System Dependencies (replit.nix)

Camoufox runs a real Firefox binary headless. It requires these system libraries:

- `gtk3` — GTK3 (libgtk-3.so.0), required by Firefox/XPCOM
- `glib` — GLib low-level system library
- `dbus-glib` — D-Bus GLib bindings
- `alsa-lib` — ALSA audio library
- `xorg.libXrender` — X11 rendering extension
- `xorg.libXt` — X11 toolkit intrinsics

Without these, camoufox fails with: `libgtk-3.so.0: cannot open shared object file`

## Environment Variables

- `CARD_API_URL` — API endpoint to generate card data (returns JSON with `name` field)

## Automation Flow

1. Fetch a random name from card API
2. Open camoufox browser with persistent profile
3. Navigate to profile settings, fill name, submit form
4. Fetch random Indonesian address from mocloc.com API
5. Navigate to billing page, click Edit, fill address form, save

## Cookie Setup

`cookies.json` contains GitHub session cookies exported from a browser extension.
Format: array of cookie objects with `name`, `value`, `domain`, `path`, `secure`, `httpOnly`, `sameSite`, `expirationDate` fields.

The `dotcom_user` cookie is used to extract the GitHub username.

## Persistent Browser Profiles

Browser profiles are stored in `profiles/{username}/`. On first run for a username, a new profile directory is created. Subsequent runs reuse the profile, preserving browser state like cache and local storage.

## How to Run

```
python main.py
```

## Key Design Decisions

- Username is derived from `dotcom_user` cookie — no separate env var needed
- Single browser session handles all automation steps (profile + billing)
- Camoufox handles full form interactions (fill + click) inside the browser to avoid CSRF/session mismatch
- The `sameSite: "no_restriction"` cookie value is mapped to `"None"` for Playwright compatibility
- Stable selectors used: `input[name="..."]`, `#billing_contact_*`, `button.js-edit-user-personal-profile`
- Address API: `https://mocloc.com/api/v1/addresses/ID?count=1` (Indonesian addresses)

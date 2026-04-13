# GitHub Profile Automation

## Overview

A minimal Python automation script that:
1. Calls a card generation API to fetch a name
2. Uses camoufox headless browser to open GitHub profile settings
3. Fills the name field and submits the form to update the profile

Designed to run headless on a server without a display.

## Project Structure

```
main.py                → Entry point, orchestrates the flow
lib/
  __init__.py
  card.py              → Card API integration (fetch generated name)
  cookies.py           → Cookie loading, username extraction, formatting
  browser.py           → Camoufox browser setup, persistent profiles
  github.py            → GitHub automation actions
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
- Camoufox handles the full form submission (fill + click) inside the browser session to avoid CSRF/session mismatch issues
- The `sameSite: "no_restriction"` cookie value is mapped to `"None"` for Playwright compatibility
- Automation uses stable selectors: `input[name="user[profile_name]"]` and `button[type="submit"]`

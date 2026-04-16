# Copilot Instructions

## Build, test, and lint commands

This repository has two codebases:

| Scope | Command(s) | Notes |
| --- | --- | --- |
| Python automation (repo root) | `python -m pip install -r requirements.txt` | Install runtime dependencies. |
| Python automation (run flow) | `python main.py --type faculty` or `python main.py --type student` | Main entrypoint in this repo. |
| Chrome extension preview (`source-code/gitstud`) | `cd source-code/gitstud && node server.js` | Serves static files on port 5000. |

There is currently no configured automated test suite or linter command in this repository (no `pytest`/`unittest` tests, no lint config, no `package.json` scripts).  
Single-test command is therefore not available yet.

## High-level architecture

### 1. Root Python automation pipeline

- `main.py` orchestrates the full run:
  - Fetch card data (`lib/card.py`)
  - Fetch random Indonesian address (`lib/address.py`)
  - Open Camoufox persistent browser context (`lib/browser.py`)
  - Authenticate (cookie-based by default, or `--login` credentials)
  - Ensure 2FA + update profile + update billing + submit education application (`lib/github.py`)
  - Optionally send report email with OTP artifacts (`lib/mailer.py`)
- Cookie handling is centralized in `lib/cookies.py` (`dotcom_user` extraction + Playwright cookie normalization).
- Persistent state:
  - Browser profiles: `profiles/{username}/`
  - 2FA artifacts: `otp/{username}/secret.txt` and `otp/{username}/recovery_codes.txt`
- Education submission is finalized by intercepting the POST to `settings/education/developer_pack_applications` and replacing `dev_pack_form[photo_proof]` plus latitude/longitude in `lib/github.py`.

### 2. Reference Chrome extension (`source-code/gitstud`)

- Manifest V3 extension with:
  - `background.js` (proxy config, spoofing injection, message router)
  - `content.js` (DOM bypass + billing autofill + intercept data bridge)
  - `interceptor.js` (MAIN world fetch/XHR interception for `photo_proof`)
  - `popup.js` (UI actions; talks to background via `chrome.runtime.sendMessage`)
- No build step: static JS/HTML loaded unpacked in Chrome.
- This folder already contains its own `.github/copilot-instructions.md`; keep it aligned with root-level instructions when extension behavior changes.

## Key conventions for this repo

1. **Two application modes everywhere:** CLI accepts `faculty|student`; card API maps this to `teacher|student` (`lib/card.py`), and GitHub form radio IDs are selected accordingly (`lib/github.py`).
2. **Fail-fast automation style:** critical path helpers in `lib/github.py` call `_err(...)` and raise immediately when selectors, auth state, or form steps are invalid.
3. **Deliberate wait strategy:** interaction timing is based on `DELAY = 2000` plus `_goto()` (`domcontentloaded` + extra wait). Keep this pacing style when adding new browser steps.
4. **Cookie normalization rule:** incoming cookie `sameSite: "no_restriction"` must be converted to Playwright-compatible `"None"` in `format_cookies(...)`.
5. **Geolocation consistency:** card-derived latitude/longitude is reused across browser context geolocation and final education form submission interception.
6. **Extension message contract:** in `source-code/gitstud`, popup/content/background coordination uses explicit `message.action` strings (`enableProxy`, `generateAddress`, `injectInterceptor`, etc.) and shared `chrome.storage.local` keys; preserve existing action names unless all call sites are updated.

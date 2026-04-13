# GitHub Education Upload Enabler

## Project Overview

A Chrome extension (Manifest V3) that bypasses the "camera only" requirement on the GitHub Education benefits application page. It allows users to upload files (ID cards, proof of enrollment) instead of using a live webcam.

## Tech Stack

- **Type:** Chrome Extension (Manifest V3)
- **Languages:** Vanilla JavaScript, HTML, CSS
- **Build System:** None — static files loaded directly into Chrome as an unpacked extension
- **Package Manager:** None — no dependencies
- **Preview Server:** Node.js built-in `http` module (`server.js`)

## Project Structure

```
manifest.json      - Extension manifest (permissions, scripts, icons)
background.js      - Service worker: proxy management, auth, spoofing injection
content.js         - Injected into github.com: upload bypass, DOM manipulation
popup.html         - Extension popup UI
popup.js           - Popup logic (proxy toggle, spoofing toggle, address generator)
icon16/48/128.png  - Extension icons
server.js          - Simple static file server for Replit preview (port 5000)
index.html         - Project overview landing page for Replit preview
```

## Features

1. **File Upload Bypass** — Forces `dev_pack_form_camera_required` hidden input to `false`, injects custom file upload UI
2. **Proxy Support** — Configures PAC script to route GitHub traffic through proxy (eclipseproxy.com)
3. **Spoofing** — Overrides timezone, GPS, language (`Intl`, `navigator`, `RTCPeerConnection`)
4. **Address Generator** — Generates Indonesian addresses via mocloc.com API for billing form auto-fill

## Replit Setup

- **Workflow:** `Start application` runs `node server.js` on port 5000
- **Preview:** `index.html` serves as landing page; `popup.html` accessible at `/popup.html`
- **Deployment:** Autoscale, run `node server.js`

## Chrome Extension Installation

1. Open Chrome → `chrome://extensions`
2. Enable **Developer mode**
3. Click **Load unpacked** → select this project folder
4. Refresh a GitHub Education page

# Copilot Instructions

## Project Overview

This is a Chrome extension (Manifest V3) for GitHub Education that provides:
1. **Upload Bypass** - Enables file uploads on the benefits application page, bypassing camera-only requirement
2. **Proxy Support** - Residential proxy via Eclipse Proxy API
3. **Spoofing** - Timezone, GPS, and language spoofing (Indonesian location)
4. **Address Generator** - Auto-fills billing address using mocloc.com API

## Architecture

```
manifest.json     - Extension config, permissions, content script registration
background.js     - Service worker: proxy config, spoofing injection, API calls
popup.html/js     - Extension popup UI with toggle controls
content.js        - DOM manipulation for upload bypass and address filling
```

### Data Flow

- **Proxy**: popup.js → background.js (fetch API) → chrome.proxy API
- **Spoofing**: background.js injects script into page's MAIN world to override navigator/Intl
- **Address**: popup.js → background.js (fetch API) → content.js (fills form fields)

### External APIs

- Proxy: `http://eclipseproxy.com/api/genProxy?...` → returns `host:port:user:pass`
- Address: `https://mocloc.com/api/v1/addresses/ID?count=1` → returns JSON array

## Key Conventions

- UI elements injected by extension use `bypass-` prefix for IDs
- GitHub's green color (`#2ea44f`) used throughout for visual consistency
- All DOM queries handle elements not existing yet (SPA routing)
- Spoofing uses `window.__spoofingInjected` flag to prevent double-injection
- Form filling dispatches both `input` and `change` events for React compatibility

## Testing

1. Load unpacked in Chrome (`chrome://extensions` → Developer mode → Load unpacked)
2. Add icon files if missing: `icon16.png`, `icon48.png`, `icon128.png`
3. Click extension icon to access proxy/spoofing toggles and address generator
4. Test on `https://github.com/settings/education/*` and `https://github.com/settings/billing/*`

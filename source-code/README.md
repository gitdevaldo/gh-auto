# GitHub Education Upload Bypass Extension

This Chrome extension enables the file upload option on the GitHub Education benefits application page, bypassing the "camera only" requirement.

## How It Works (The Logic)

GitHub's application page uses a "camera first" approach for proof submission, often hiding the file upload option entirely based on server-side flags ("camera required"). This extension reverses that logic using a content script.

### Flow of Execution:

1.  **Injection**: The extension is configured (`manifest.json`) to run `content.js` automatically whenever you visit `https://github.com/settings/education/*`.
2.  **Detection**: The script constantly monitors the page (every 1 second) to detect when the **Proof Submission** section is loaded. Using a polling interval is necessary because the page is a single-page app (SPA) that changes content dynamically without full reloads.
3.  **Disabling Restrictions**:
    *   It searches for the hidden input field `dev_pack_form_camera_required` (which is typically set to `true`).
    *   It forces this value to `false`, effectively telling the form submission logic that a camera is *not* mandatory.
4.  **UI Injection**:
    *   It checks if the standard upload container (`.js-upload-proof-container` or `.Overlay-body`) is present.
    *   It injects a custom, green-bordered **"Upload Image Bypass"** box directly into the page.
5.  **File Processing**:
    *   When you select a file in the injected box, the script reads it locally as a Base64 string (using `FileReader`).
    *   It finds (or creates) the hidden `photo_proof` input field that GitHub's server expects.
    *   It populates this hidden field with your file data.
6.  **Enabling Submission**:
    *   Finally, it finds the "Submit" or "Continue" buttons (often disabled until a camera photo is taken).
    *   It deliberately removes the `disabled` attribute, allowing you to click them and send the form with your uploaded file.

## Installation

1.  Open Chrome and browse to `chrome://extensions`.
2.  Toggle **Developer mode** in the top right corner.
3.  Click **Load unpacked**.
4.  Select this `gitstud` folder.
5.  Refresh the GitHub Education page.

(function() {
    if (window.__fetchIntercepted) return;
    window.__fetchIntercepted = true;

    const PHOTO_KEY = 'dev_pack_form[photo_proof]';

    function getInterceptData() {
        document.dispatchEvent(new CustomEvent('__intercept_request_data'));

        const el = document.getElementById('__intercept_data');
        if (!el || !el.textContent) return null;

        try {
            const stored = JSON.parse(el.textContent);
            const imageDataUrl = stored.image;
            if (!imageDataUrl) return null;

            const mimeMatch = imageDataUrl.match(/^data:(image\/\w+);/);
            const mimeType = mimeMatch ? mimeMatch[1] : 'image/jpeg';
            const ext = mimeType.split('/')[1] || 'jpg';

            return JSON.stringify({
                image: imageDataUrl,
                metadata: {
                    filename: "camera." + ext,
                    type: "camera",
                    mimeType: mimeType,
                    deviceLabel: "USB2.0 HD UVC WebCam (322e:2103)"
                }
            });
        } catch(e) {
            return null;
        }
    }

    function tryReplace(body, replacementJson) {
        if (body && typeof body.has === 'function' && typeof body.set === 'function') {
            if (body.has(PHOTO_KEY)) {
                body.set(PHOTO_KEY, replacementJson);
                console.log("✅ photo_proof replaced (" + body.constructor?.name + ")");
                return true;
            }
            console.log("⚠️ No " + PHOTO_KEY + " in body. Keys:");
            if (typeof body.entries === 'function') {
                for (const [key] of body.entries()) {
                    console.log("  - " + key);
                }
            }
        }
        return false;
    }

    const originalFetch = window.fetch;
    window.fetch = async function(...args) {
        let [resource, options] = args;

        let url = '';
        if (typeof resource === 'string') {
            url = resource;
        } else if (resource instanceof Request) {
            url = resource.url;
        }

        const isTarget = url.includes('developer_pack_applications');
        const isPost = options && options.method && options.method.toUpperCase() === 'POST';

        if (isTarget && isPost && options.body) {
            console.log("📷 Detected POST to developer_pack_applications");

            const rawData = getInterceptData();
            if (rawData) {
                console.log("📷 Intercept data found, replacing photo_proof...");
                tryReplace(options.body, rawData);
            } else {
                console.log("ℹ️ No intercept image loaded — passing through normally");
            }
        }

        return originalFetch.apply(this, args);
    };

    const originalXHROpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url, ...rest) {
        this.__interceptMethod = method;
        this.__interceptUrl = url;
        return originalXHROpen.call(this, method, url, ...rest);
    };

    const originalXHRSend = XMLHttpRequest.prototype.send;
    XMLHttpRequest.prototype.send = function(body) {
        const isTarget = this.__interceptUrl && this.__interceptUrl.includes('developer_pack_applications');
        const isPost = this.__interceptMethod && this.__interceptMethod.toUpperCase() === 'POST';

        if (isTarget && isPost && body) {
            console.log("📷 Detected XHR POST to developer_pack_applications");
            const rawData = getInterceptData();
            if (rawData) {
                tryReplace(body, rawData);
            }
        }

        return originalXHRSend.call(this, body);
    };

    console.log("🔗 Fetch/XHR interceptor installed (MAIN world, CSP bypass)");
})();

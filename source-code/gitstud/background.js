// Background Service Worker for GitHub Education Helper

const ADDRESS_API = "https://mocloc.com/api/v1/addresses/ID?count=1";
const IP_CHECK_APIS = [
    {
        url: "http://ip-api.com/json/?fields=query,country,countryCode,city,regionName,timezone,isp",
        parse: (data) => ({
            ip: data.query,
            country: data.country,
            countryCode: data.countryCode,
            city: data.city,
            region: data.regionName,
            timezone: data.timezone,
            org: data.isp
        })
    },
    {
        url: "https://ipapi.co/json/",
        parse: (data) => ({
            ip: data.ip,
            country: data.country_name,
            countryCode: data.country_code,
            city: data.city,
            region: data.region,
            timezone: data.timezone,
            org: data.org
        })
    },
    {
        url: "https://api.ipify.org?format=json",
        parse: (data) => ({
            ip: data.ip,
            country: null,
            countryCode: null,
            city: null,
            region: null,
            timezone: null,
            org: null
        })
    }
];
const PROXY_PASSWORD = "11c11bdc-ef9e-4b82-b61c-df20cce291ac";

const CITY_CONFIG = {
    random: {
        label: "Random (Indonesia)",
        latitude: -7.6039,
        longitude: 111.9030,
        spoofCity: "Nganjuk",
        noCity: true
    },
    jakarta: {
        label: "Jakarta",
        latitude: -6.2088,
        longitude: 106.8456
    },
    kediri: {
        label: "Kediri",
        latitude: -7.8177,
        longitude: 112.0174
    },
    nganjuk: {
        label: "Nganjuk",
        latitude: -7.6039,
        longitude: 111.9030
    },
    ponorogo: {
        label: "Ponorogo",
        latitude: -7.8653,
        longitude: 111.4600
    },
    probolinggo: {
        label: "Probolinggo",
        latitude: -7.7543,
        longitude: 113.2159
    },
    madiun: {
        label: "Madiun",
        latitude: -7.6298,
        longitude: 111.5239
    }
};

function buildProxyApiUrl(city) {
    const config = CITY_CONFIG[city] || CITY_CONFIG.kediri;
    if (config.noCity) {
        return `http://eclipseproxy.com/api/genProxy?proxy=eclipse_gitdevaldo-country-id-session-wiSE63Mj-lifetime-30%3A${PROXY_PASSWORD}%3Acore.eclipseproxy.com%3A10000&format=h:pt:u:ps&amount=1`;
    }
    return `http://eclipseproxy.com/api/genProxy?proxy=eclipse_gitdevaldo-country-id-city-${city}-session-wiSE63Mj-lifetime-30%3A${PROXY_PASSWORD}%3Acore.eclipseproxy.com%3A10000&format=h:pt:u:ps&amount=1`;
}

function buildSpoofData(city) {
    const config = CITY_CONFIG[city] || CITY_CONFIG.kediri;
    return {
        timezone: "Asia/Jakarta",
        language: "id-ID",
        languages: ["id-ID", "id", "en-US", "en"],
        latitude: config.latitude,
        longitude: config.longitude,
        city: config.spoofCity || config.label,
        country: "Indonesia"
    };
}

let currentCity = "kediri";
let currentProxyData = null;

// Parse proxy response: "host:port:username:password"
function parseProxyResponse(response) {
    const parts = response.trim().split(':');
    if (parts.length >= 4) {
        return {
            host: parts[0],
            port: parseInt(parts[1]),
            username: parts[2],
            password: parts[3]
        };
    }
    throw new Error('Invalid proxy response format');
}

// Fetch new proxy from API
async function fetchProxy(city) {
    city = city || currentCity;
    try {
        let response;
        try {
            response = await fetch(buildProxyApiUrl(city));
        } catch (e) {
            response = await fetch(buildProxyApiUrl(city));
        }
        
        if (!response.ok) {
            throw new Error(`API returned status ${response.status}`);
        }
        const text = await response.text();
        console.log("📡 Proxy API response:", text);
        return parseProxyResponse(text);
    } catch (error) {
        console.error('Failed to fetch proxy:', error);
        throw error;
    }
}

// Configure Chrome proxy settings with PAC script for domain-specific routing
async function setProxy(proxyData) {
    const pacScript = `
        function FindProxyForURL(url, host) {
            if (shExpMatch(host, "*.github.com") || shExpMatch(host, "github.com")) {
                return "PROXY ${proxyData.host}:${proxyData.port}";
            }
            if (shExpMatch(host, "ipapi.co") || shExpMatch(host, "ip-api.com") || shExpMatch(host, "api.ipify.org")) {
                return "PROXY ${proxyData.host}:${proxyData.port}";
            }
            return "DIRECT";
        }
    `;

    const config = {
        mode: "pac_script",
        pacScript: {
            data: pacScript
        }
    };

    return new Promise((resolve, reject) => {
        chrome.proxy.settings.set({ value: config, scope: 'regular' }, () => {
            if (chrome.runtime.lastError) {
                reject(chrome.runtime.lastError);
            } else {
                console.log("🌐 Proxy configured for *.github.com only");
                resolve();
            }
        });
    });
}

// Clear proxy settings
async function clearProxy() {
    return new Promise((resolve, reject) => {
        chrome.proxy.settings.clear({ scope: 'regular' }, () => {
            if (chrome.runtime.lastError) {
                reject(chrome.runtime.lastError);
            } else {
                resolve();
            }
        });
    });
}

// Handle proxy authentication (MV3 compatible)
chrome.webRequest.onAuthRequired.addListener(
    (details) => {
        if (currentProxyData && details.isProxy) {
            console.log("🔐 Providing proxy credentials for:", details.challenger?.host);
            return {
                authCredentials: {
                    username: currentProxyData.username,
                    password: currentProxyData.password
                }
            };
        }
        return {};
    },
    { urls: ["<all_urls>"] },
    ["blocking"]
);

// Also restore proxy credentials from storage on startup
chrome.storage.local.get(['proxyEnabled', 'proxyData', 'spoofEnabled', 'selectedCity']).then(async (settings) => {
    currentCity = settings.selectedCity || "kediri";
    const spoofData = buildSpoofData(currentCity);

    if (settings.proxyEnabled !== false) {
        if (settings.proxyData) {
            currentProxyData = settings.proxyData;
            try {
                await setProxy(settings.proxyData);
                console.log("🌐 Proxy restored from storage (" + currentCity + ")");
            } catch (error) {
                console.error("Failed to restore proxy on startup:", error);
            }
        } else {
            try {
                const proxyData = await fetchProxy(currentCity);
                await setProxy(proxyData);
                currentProxyData = proxyData;
                await chrome.storage.local.set({ proxyEnabled: true, proxyData: proxyData });
                console.log("🌐 Proxy fetched and enabled on startup (" + currentCity + ")");
            } catch (error) {
                console.error("Failed to fetch proxy on startup:", error);
                await chrome.storage.local.set({ proxyEnabled: false });
            }
        }
    }

    if (settings.spoofEnabled !== false) {
        await chrome.storage.local.set({ spoofEnabled: true, spoofData: spoofData });
        console.log("🕵️ Spoofing enabled on startup (" + currentCity + ")");
    }
});

// Inject spoofing script into tabs
async function injectSpoofingScript(tabId) {
    const spoofData = buildSpoofData(currentCity);
    const spoofScript = `
        (function() {
            const spoofKey = '${spoofData.city}_${spoofData.latitude}_${spoofData.longitude}';
            if (window.__spoofingKey === spoofKey) return;
            window.__spoofingKey = spoofKey;

            const spoofData = ${JSON.stringify(spoofData)};
            const targetOffset = -420; // UTC+7 in minutes

            // ==================== NATIVE FUNCTION MASKING ====================
            // Store original toString to restore native-looking signatures
            const nativeToString = Function.prototype.toString;
            const spoofedFunctions = new Map();

            function maskAsNative(fn, nativeName) {
                spoofedFunctions.set(fn, \`function \${nativeName}() { [native code] }\`);
            }

            // Override Function.prototype.toString to hide our modifications
            Object.defineProperty(Function.prototype, 'toString', {
                value: function() {
                    if (spoofedFunctions.has(this)) {
                        return spoofedFunctions.get(this);
                    }
                    return nativeToString.call(this);
                },
                writable: true,
                configurable: true
            });
            maskAsNative(Function.prototype.toString, 'toString');

            // ==================== TIMEZONE SPOOFING ====================
            const originalDateTimeFormat = Intl.DateTimeFormat;
            const newDateTimeFormat = function(locales, options) {
                options = Object.assign({}, options, { timeZone: spoofData.timezone });
                return new originalDateTimeFormat(locales, options);
            };
            newDateTimeFormat.prototype = originalDateTimeFormat.prototype;
            newDateTimeFormat.supportedLocalesOf = originalDateTimeFormat.supportedLocalesOf;
            Intl.DateTimeFormat = newDateTimeFormat;
            maskAsNative(Intl.DateTimeFormat, 'DateTimeFormat');

            const originalResolvedOptions = Intl.DateTimeFormat.prototype.resolvedOptions;
            Intl.DateTimeFormat.prototype.resolvedOptions = function() {
                const result = originalResolvedOptions.call(this);
                result.timeZone = spoofData.timezone;
                return result;
            };
            maskAsNative(Intl.DateTimeFormat.prototype.resolvedOptions, 'resolvedOptions');

            // Spoof Date.prototype.getTimezoneOffset
            const originalGetTimezoneOffset = Date.prototype.getTimezoneOffset;
            Date.prototype.getTimezoneOffset = function() {
                return targetOffset;
            };
            maskAsNative(Date.prototype.getTimezoneOffset, 'getTimezoneOffset');

            // Spoof Date.prototype.toString and toTimeString to show correct timezone
            const originalDateToString = Date.prototype.toString;
            Date.prototype.toString = function() {
                const str = originalDateToString.call(this);
                // Replace timezone info with WIB (Western Indonesian Time)
                return str.replace(/GMT[+-]\\d{4}.*$/, 'GMT+0700 (Western Indonesia Time)');
            };
            maskAsNative(Date.prototype.toString, 'toString');

            const originalToTimeString = Date.prototype.toTimeString;
            Date.prototype.toTimeString = function() {
                const str = originalToTimeString.call(this);
                return str.replace(/GMT[+-]\\d{4}.*$/, 'GMT+0700 (Western Indonesia Time)');
            };
            maskAsNative(Date.prototype.toTimeString, 'toTimeString');

            // ==================== NAVIGATOR SPOOFING ====================
            // Use more robust property definition that survives inspection
            const navigatorProto = Object.getPrototypeOf(navigator);

            Object.defineProperty(navigatorProto, 'language', {
                get: function() { return spoofData.language; },
                configurable: true,
                enumerable: true
            });

            Object.defineProperty(navigatorProto, 'languages', {
                get: function() { return Object.freeze([...spoofData.languages]); },
                configurable: true,
                enumerable: true
            });

            // ==================== GEOLOCATION SPOOFING ====================
            const createFakePosition = () => ({
                coords: {
                    latitude: spoofData.latitude,
                    longitude: spoofData.longitude,
                    accuracy: 50 + Math.random() * 50, // Slight randomization
                    altitude: null,
                    altitudeAccuracy: null,
                    heading: null,
                    speed: null
                },
                timestamp: Date.now()
            });

            const originalGetCurrentPosition = navigator.geolocation.getCurrentPosition;
            navigator.geolocation.getCurrentPosition = function(success, error, options) {
                setTimeout(() => success(createFakePosition()), 50 + Math.random() * 100);
            };
            maskAsNative(navigator.geolocation.getCurrentPosition, 'getCurrentPosition');

            const originalWatchPosition = navigator.geolocation.watchPosition;
            navigator.geolocation.watchPosition = function(success, error, options) {
                const watchId = Math.floor(Math.random() * 100000);
                setTimeout(() => success(createFakePosition()), 50 + Math.random() * 100);
                return watchId;
            };
            maskAsNative(navigator.geolocation.watchPosition, 'watchPosition');

            // ==================== WEBRTC LEAK PREVENTION ====================
            // Block WebRTC from leaking real IP
            const rtcPeerConnection = window.RTCPeerConnection || window.webkitRTCPeerConnection || window.mozRTCPeerConnection;
            
            if (rtcPeerConnection) {
                const originalRTC = rtcPeerConnection;
                const newRTC = function(config, constraints) {
                    // Force use of TURN only to prevent IP leak, or block if no TURN
                    if (config && config.iceServers) {
                        config.iceServers = config.iceServers.map(server => {
                            if (server.urls) {
                                const urls = Array.isArray(server.urls) ? server.urls : [server.urls];
                                server.urls = urls.filter(url => url.startsWith('turn:'));
                            }
                            return server;
                        }).filter(server => server.urls && server.urls.length > 0);
                    }
                    return new originalRTC(config, constraints);
                };
                newRTC.prototype = originalRTC.prototype;
                window.RTCPeerConnection = newRTC;
                if (window.webkitRTCPeerConnection) window.webkitRTCPeerConnection = newRTC;
                maskAsNative(window.RTCPeerConnection, 'RTCPeerConnection');
            }

            // ==================== ADDITIONAL HARDENING ====================
            // Spoof Intl.NumberFormat locale detection
            const originalNumberFormat = Intl.NumberFormat;
            Intl.NumberFormat = function(locales, options) {
                if (!locales) locales = spoofData.language;
                return new originalNumberFormat(locales, options);
            };
            Intl.NumberFormat.prototype = originalNumberFormat.prototype;
            Intl.NumberFormat.supportedLocalesOf = originalNumberFormat.supportedLocalesOf;
            maskAsNative(Intl.NumberFormat, 'NumberFormat');

            // Prevent detection via prototype chain inspection
            const spoofedObjects = [
                Date.prototype.getTimezoneOffset,
                Date.prototype.toString,
                Date.prototype.toTimeString,
                Intl.DateTimeFormat,
                Intl.DateTimeFormat.prototype.resolvedOptions,
                navigator.geolocation.getCurrentPosition,
                navigator.geolocation.watchPosition
            ];

            // Make Object.getOwnPropertyDescriptor return expected results
            const originalGetOwnPropertyDescriptor = Object.getOwnPropertyDescriptor;
            Object.getOwnPropertyDescriptor = function(obj, prop) {
                const result = originalGetOwnPropertyDescriptor.call(this, obj, prop);
                // Hide that we modified these
                if (result && typeof result.value === 'function' && spoofedFunctions.has(result.value)) {
                    result.value = result.value; // Keep as is but appears normal
                }
                return result;
            };

            console.log('🕵️ Stealth spoofing active: ' + spoofData.city + ', ' + spoofData.country);
        })();
    `;

    try {
        const tab = await chrome.tabs.get(tabId).catch(() => null);
        if (!tab || !tab.url || tab.url.startsWith('chrome://') || tab.url.startsWith('chrome-extension://') || tab.url.startsWith('about:')) {
            return;
        }
        await chrome.scripting.executeScript({
            target: { tabId: tabId, allFrames: false },
            func: (script) => {
                const scriptEl = document.createElement('script');
                scriptEl.textContent = script;
                (document.head || document.documentElement).appendChild(scriptEl);
                scriptEl.remove();
            },
            args: [spoofScript],
            world: 'MAIN',
            injectImmediately: true
        });
    } catch (error) {
        if (!error.message?.includes('error page') && !error.message?.includes('Cannot access')) {
            console.warn('Spoofing injection skipped for tab ' + tabId + ':', error.message);
        }
    }
}

// Fetch address from API
async function fetchAddress() {
    try {
        const response = await fetch(ADDRESS_API);
        if (!response.ok) throw new Error('Address API request failed');
        const data = await response.json();
        if (Array.isArray(data) && data.length > 0) {
            return data[0];
        }
        throw new Error('No address data returned');
    } catch (error) {
        console.error('Failed to fetch address:', error);
        throw error;
    }
}

// Message handler
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    (async () => {
        try {
            switch (message.action) {
                case 'injectInterceptor': {
                    const tabId = sender.tab?.id;
                    if (tabId) {
                        try {
                            await chrome.scripting.executeScript({
                                target: { tabId },
                                files: ['interceptor.js'],
                                world: 'MAIN'
                            });
                            console.log('✅ Interceptor injected into MAIN world for tab', tabId);
                        } catch (e) {
                            console.error('Failed to inject interceptor:', e);
                        }
                    }
                    sendResponse({ success: true });
                    break;
                }

                case 'enableProxy': {
                    const proxyData = await fetchProxy(currentCity);
                    await setProxy(proxyData);
                    currentProxyData = proxyData;
                    await chrome.storage.local.set({ proxyData: proxyData });
                    sendResponse({ success: true, proxyData });
                    break;
                }

                case 'disableProxy': {
                    await clearProxy();
                    currentProxyData = null;
                    sendResponse({ success: true });
                    break;
                }

                case 'refreshProxy': {
                    const proxyData = await fetchProxy();
                    if (currentProxyData) {
                        await setProxy(proxyData);
                    }
                    currentProxyData = proxyData;
                    sendResponse({ success: true, proxyData });
                    break;
                }

                case 'enableSpoofing': {
                    const spoofData = buildSpoofData(currentCity);
                    await chrome.storage.local.set({ spoofEnabled: true, spoofData: spoofData });

                    const tabs = await chrome.tabs.query({});
                    for (const tab of tabs) {
                        if (tab.url && !tab.url.startsWith('chrome://') && !tab.url.startsWith('chrome-extension://')) {
                            await injectSpoofingScript(tab.id);
                        }
                    }

                    sendResponse({ success: true, spoofData: spoofData });
                    break;
                }

                case 'disableSpoofing': {
                    await chrome.storage.local.set({ spoofEnabled: false });
                    sendResponse({ success: true });
                    break;
                }

                case 'changeCity': {
                    const newCity = message.city;
                    if (!CITY_CONFIG[newCity]) {
                        sendResponse({ success: false, error: 'Unknown city: ' + newCity });
                        break;
                    }
                    currentCity = newCity;
                    const spoofData = buildSpoofData(newCity);
                    await chrome.storage.local.set({ selectedCity: newCity, spoofData: spoofData });

                    const settings = await chrome.storage.local.get(['proxyEnabled', 'spoofEnabled']);

                    if (settings.proxyEnabled) {
                        const proxyData = await fetchProxy(newCity);
                        await setProxy(proxyData);
                        currentProxyData = proxyData;
                        await chrome.storage.local.set({ proxyData: proxyData });
                    }

                    if (settings.spoofEnabled) {
                        const allTabs = await chrome.tabs.query({});
                        for (const tab of allTabs) {
                            if (tab.url && !tab.url.startsWith('chrome://') && !tab.url.startsWith('chrome-extension://')) {
                                await injectSpoofingScript(tab.id);
                            }
                        }
                    }

                    sendResponse({
                        success: true,
                        city: newCity,
                        cityLabel: CITY_CONFIG[newCity].label,
                        spoofData: spoofData,
                        proxyData: currentProxyData
                    });
                    break;
                }

                case 'getCities': {
                    const cities = Object.entries(CITY_CONFIG).map(([key, val]) => ({
                        value: key,
                        label: val.label
                    }));
                    sendResponse({ success: true, cities: cities, currentCity: currentCity });
                    break;
                }

                case 'generateAddress': {
                    const address = await fetchAddress();
                    sendResponse({ success: true, address });
                    break;
                }

                case 'checkIP': {
                    let lastError = null;
                    for (const api of IP_CHECK_APIS) {
                        try {
                            const controller = new AbortController();
                            const timeout = setTimeout(() => controller.abort(), 8000);
                            const response = await fetch(api.url, { signal: controller.signal });
                            clearTimeout(timeout);
                            if (!response.ok) continue;
                            const data = await response.json();
                            const parsed = api.parse(data);
                            sendResponse({ success: true, ...parsed });
                            lastError = null;
                            break;
                        } catch (error) {
                            lastError = error;
                            continue;
                        }
                    }
                    if (lastError) {
                        sendResponse({ success: false, error: 'All IP check services failed. Proxy may be blocking requests or offline.' });
                    }
                    break;
                }

                default:
                    sendResponse({ success: false, error: 'Unknown action' });
            }
        } catch (error) {
            sendResponse({ success: false, error: error.message });
        }
    })();

    return true; // Keep message channel open for async response
});

// Inject spoofing on tab navigation if enabled
chrome.tabs.onUpdated.addListener(async (tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url && !tab.url.startsWith('chrome://') && !tab.url.startsWith('chrome-extension://')) {
        const settings = await chrome.storage.local.get(['spoofEnabled']);
        if (settings.spoofEnabled) {
            await injectSpoofingScript(tabId);
        }
    }
});

// Initialize on install - enable proxy and spoofing by default
chrome.runtime.onInstalled.addListener(async (details) => {
    console.log('GitHub Education Helper installed');
    
    if (details.reason === 'install') {
        currentCity = "kediri";
        const spoofData = buildSpoofData(currentCity);
        try {
            const proxyData = await fetchProxy(currentCity);
            await setProxy(proxyData);
            currentProxyData = proxyData;
            await chrome.storage.local.set({ 
                proxyEnabled: true, 
                proxyData: proxyData,
                spoofEnabled: true,
                spoofData: spoofData,
                selectedCity: currentCity
            });
            console.log('✅ Proxy fetched and enabled (Kediri)');
            console.log('✅ Spoofing enabled by default');
        } catch (error) {
            console.error('Failed to fetch proxy on install:', error);
            await chrome.storage.local.set({ 
                proxyEnabled: false,
                spoofEnabled: true,
                spoofData: spoofData,
                selectedCity: currentCity
            });
        }
    }
});

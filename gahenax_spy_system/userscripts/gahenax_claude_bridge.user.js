// ==UserScript==
// @name         Gahenax Claude Bridge v1.2
// @namespace    http://gahenax.ai/
// @version      1.2
// @description  Bidirectional bridge — Claude.ai <-> local Gahenax environment
// @author       Antigravity AI
// @match        https://claude.ai/chat/*
// @grant        GM_xmlhttpRequest
// @connect      localhost
// ==/UserScript==

(function() {
    'use strict';

    const BRIDGE    = "http://localhost:8080";
    const SYNC_MS   = 3000;   // push chat to bridge
    const POLL_MS   = 4000;   // poll for Antigravity replies
    const SESSION   = () => window.location.pathname.split('/').pop();

    //  Widget 
    const widget = document.createElement('div');
    widget.innerHTML = `
        <div id="ghx-widget" style="position:fixed;bottom:80px;right:20px;z-index:9999;
             background:#111;border:1px solid #4CAF50;border-radius:8px;
             padding:10px;color:#4CAF50;font-family:monospace;font-size:12px;min-width:160px;">
            <div style="font-weight:bold;border-bottom:1px solid #4CAF50;margin-bottom:6px;padding-bottom:4px;">
                GAHENAX BRIDGE v1.2
            </div>
            <div id="ghx-status">Initializing...</div>
            <div id="ghx-count" style="color:#888;font-size:10px;margin-top:2px;"></div>
            <button id="ghx-sync" style="margin-top:6px;width:100%;background:#2E7D32;
                    color:#fff;border:none;cursor:pointer;border-radius:4px;padding:4px;">
                SYNC NOW
            </button>
        </div>`;
    document.body.appendChild(widget);

    const setStatus = (msg, color = '#4CAF50') => {
        const el = document.getElementById('ghx-status');
        if (el) { el.innerText = msg; el.style.color = color; }
    };
    const setCount = (txt) => {
        const el = document.getElementById('ghx-count');
        if (el) el.innerText = txt;
    };

    //  Capture chat messages 
    const getMessages = () => {
        const msgs = [];
        document.querySelectorAll('[data-testid="user-message"], [data-testid="assistant-message"]')
            .forEach(el => {
                const isUser = !!el.closest('[data-testid="user-message"]');
                msgs.push({ role: isUser ? "user" : "assistant", text: el.innerText.trim(), ts: Date.now() });
            });
        if (!msgs.length) {
            document.querySelectorAll('.prose').forEach(el =>
                msgs.push({ role: "unknown", text: el.innerText.trim(), ts: Date.now() })
            );
        }
        return msgs;
    };

    //  Push telemetry to bridge 
    const syncToBridge = () => {
        const messages = getMessages();
        if (!messages.length) { setStatus("No messages yet", "#888"); return; }
        GM_xmlhttpRequest({
            method: "POST", url: `${BRIDGE}/telemetry`,
            data: JSON.stringify({ session_id: SESSION(), url: location.href, messages }),
            headers: { "Content-Type": "application/json" },
            onload: r => {
                if (r.status === 200) {
                    setStatus("Synced", "#4CAF50");
                    setCount(`${messages.length} msgs | ${new Date().toLocaleTimeString()}`);
                } else {
                    setStatus("Sync error", "#f44");
                }
            },
            onerror: () => setStatus("Bridge offline", "#f44")
        });
    };

    //  Poll for Antigravity replies 
    const pollOutbox = () => {
        GM_xmlhttpRequest({
            method: "GET",
            url: `${BRIDGE}/messages/claude/pending?session_id=${SESSION()}`,
            onload: r => {
                if (r.status !== 200) return;
                let data;
                try { data = JSON.parse(r.responseText); } catch { return; }
                if (!data.messages || data.messages.length === 0) return;

                data.messages.forEach(msg => {
                    injectMessage(`[Antigravity] ${msg.content}`);
                });
                setStatus(`Reply received`, "#00bcd4");
            }
        });
    };

    //  Inject Antigravity reply as a banner in the chat 
    const injectMessage = (text) => {
        const banner = document.createElement('div');
        banner.style.cssText = `
            position:fixed;top:20px;left:50%;transform:translateX(-50%);
            background:#0d1117;border:1px solid #4CAF50;border-radius:8px;
            padding:12px 20px;color:#4CAF50;font-family:monospace;font-size:13px;
            z-index:99999;max-width:600px;word-break:break-word;
            box-shadow:0 4px 20px rgba(0,0,0,0.6);`;
        banner.innerText = text;
        document.body.appendChild(banner);
        setTimeout(() => banner.remove(), 8000);
    };

    //  Event handlers 
    document.getElementById('ghx-sync').addEventListener('click', syncToBridge);

    let syncTimer;
    new MutationObserver(() => {
        clearTimeout(syncTimer);
        syncTimer = setTimeout(syncToBridge, SYNC_MS);
    }).observe(document.querySelector('div.flex-1.overflow-y-auto') || document.body, { childList: true, subtree: true });

    //  Polling loops 
    setInterval(syncToBridge, SYNC_MS + 1000);  // periodic full sync
    setInterval(pollOutbox, POLL_MS);            // poll for Antigravity replies

    // Initial sync
    setTimeout(syncToBridge, 1500);
    setStatus("Bridge active");
})();

// ==UserScript==
// @name         Gahenax Claude Bridge v1.1
// @namespace    http://gahenax.ai/
// @version      1.1
// @description  Secure bridge between Claude.ai and local Gahenax environment
// @author       Antigravity AI
// @match        https://claude.ai/chat/*
// @grant        GM_xmlhttpRequest
// @connect      localhost
// ==/UserScript==
(function() {
    'use strict';
    const BRIDGE_URL = "http://localhost:8080/telemetry";
    const widget = document.createElement('div');
    widget.innerHTML = `
        <div id="ghx-widget" style="position:fixed;bottom:80px;right:20px;z-index:9999;
             background:#111;border:1px solid #4CAF50;border-radius:8px;
             padding:10px;color:#4CAF50;font-family:monospace;font-size:12px;">
            <div style="font-weight:bold;border-bottom:1px solid #4CAF50;margin-bottom:6px;">GAHENAX BRIDGE</div>
            <div id="ghx-status">Ready</div>
            <button id="ghx-sync" style="margin-top:6px;width:100%;background:#2E7D32;
                    color:#fff;border:none;cursor:pointer;border-radius:4px;padding:4px;">SYNC</button>
        </div>`;
    document.body.appendChild(widget);
    const setStatus = (msg, color='#4CAF50') => {
        const el = document.getElementById('ghx-status');
        if (el) { el.innerText = msg; el.style.color = color; }
    };
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
    const sync = () => {
        const messages = getMessages();
        if (!messages.length) { setStatus("No messages", "#ffff00"); return; }
        const sessionId = window.location.pathname.split('/').pop();
        GM_xmlhttpRequest({
            method: "POST", url: BRIDGE_URL,
            data: JSON.stringify({ session_id: sessionId, url: location.href, messages }),
            headers: { "Content-Type": "application/json" },
            onload: r => setStatus(r.status === 200 ? `Synced ${messages.length}` : "Server error", r.status === 200 ? "#4CAF50" : "#f00"),
            onerror: () => setStatus("Bridge offline", "#f00")
        });
    };
    document.getElementById('ghx-sync').addEventListener('click', sync);
    let syncTimer;
    new MutationObserver(() => { clearTimeout(syncTimer); syncTimer = setTimeout(sync, 3000); })
        .observe(document.querySelector('div.flex-1.overflow-y-auto') || document.body, { childList: true, subtree: true });
})();

// ==UserScript==
// @name         Gahenax Claude Bridge v1.2
// @namespace    http://gahenax.ai/
// @version      1.2
// @description  Bidirectional bridge: Claude.ai ↔ Antigravity (Gemini CLI) via local hub
// @author       Antigravity AI
// @match        https://claude.ai/chat/*
// @grant        GM_xmlhttpRequest
// @connect      localhost
// ==/UserScript==
(function () {
    'use strict';

    const BRIDGE   = "http://localhost:8080";
    const POLL_MS  = 4000;   // poll Antigravity replies every 4s
    const SYNC_MS  = 3000;   // debounce for outbound sync

    // ── Widget ────────────────────────────────────────────────────────────
    const widget = document.createElement('div');
    widget.innerHTML = `
        <div id="ghx-widget" style="position:fixed;bottom:80px;right:20px;z-index:9999;
             background:#111;border:1px solid #4CAF50;border-radius:8px;
             padding:10px;color:#4CAF50;font-family:monospace;font-size:12px;min-width:180px;">
            <div style="font-weight:bold;border-bottom:1px solid #4CAF50;margin-bottom:6px;">
                GAHENAX BRIDGE v1.2
            </div>
            <div id="ghx-status">Iniciando...</div>
            <div id="ghx-inbox" style="margin-top:6px;max-height:80px;overflow-y:auto;
                 font-size:11px;color:#aaa;border-top:1px solid #333;padding-top:4px;display:none;">
            </div>
            <button id="ghx-sync" style="margin-top:6px;width:100%;background:#2E7D32;
                    color:#fff;border:none;cursor:pointer;border-radius:4px;padding:4px;">
                SYNC →
            </button>
        </div>`;
    document.body.appendChild(widget);

    const setStatus = (msg, color = '#4CAF50') => {
        const el = document.getElementById('ghx-status');
        if (el) { el.innerText = msg; el.style.color = color; }
    };

    const addInboxMsg = (text) => {
        const box = document.getElementById('ghx-inbox');
        if (!box) return;
        box.style.display = 'block';
        const line = document.createElement('div');
        line.style.cssText = 'border-bottom:1px solid #222;padding:2px 0;';
        line.innerText = `⟵ ${text.slice(0, 80)}${text.length > 80 ? '…' : ''}`;
        box.prepend(line);
        // keep last 5
        while (box.children.length > 5) box.removeChild(box.lastChild);
    };

    // ── Read Claude messages from DOM ─────────────────────────────────────
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

    const sessionId = () => window.location.pathname.split('/').pop();

    // ── Outbound: Claude → Bridge → Antigravity ───────────────────────────
    const syncOut = () => {
        const messages = getMessages();
        if (!messages.length) { setStatus("Sin mensajes", "#ffff00"); return; }
        GM_xmlhttpRequest({
            method: "POST",
            url: `${BRIDGE}/telemetry`,
            data: JSON.stringify({ session_id: sessionId(), url: location.href, messages }),
            headers: { "Content-Type": "application/json" },
            onload: r => {
                if (r.status === 200) {
                    setStatus(`↑ ${messages.length} msgs`, "#4CAF50");
                } else {
                    setStatus("Error servidor", "#f00");
                }
            },
            onerror: () => setStatus("Bridge offline", "#f00"),
        });
    };

    // ── Inbound: Bridge → Claude (Antigravity replies) ────────────────────
    const pollInbound = () => {
        GM_xmlhttpRequest({
            method: "GET",
            url: `${BRIDGE}/messages/claude/pending?session_id=${sessionId()}`,
            onload: r => {
                if (r.status !== 200) return;
                try {
                    const data = JSON.parse(r.responseText);
                    if (data.pending > 0) {
                        setStatus(`↓ ${data.pending} de Antigravity`, "#00bcd4");
                        data.messages.forEach(m => {
                            const text = m.content?.text || JSON.stringify(m.content);
                            addInboxMsg(text);
                        });
                    }
                } catch (_) {}
            },
            onerror: () => {},   // silencioso si el bridge está offline
        });
    };

    // ── Event wiring ──────────────────────────────────────────────────────
    document.getElementById('ghx-sync').addEventListener('click', syncOut);

    // Auto-sync outbound on DOM change
    let syncTimer;
    new MutationObserver(() => {
        clearTimeout(syncTimer);
        syncTimer = setTimeout(syncOut, SYNC_MS);
    }).observe(
        document.querySelector('div.flex-1.overflow-y-auto') || document.body,
        { childList: true, subtree: true }
    );

    // Poll inbound from Antigravity
    setInterval(pollInbound, POLL_MS);

    setStatus("Ready ✓");
})();

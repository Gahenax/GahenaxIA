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
    let lastSyncCount = 0;

    // --- UI Infrastructure ---
    const widget = document.createElement('div');
    widget.id = 'gahenax-hub';
    widget.innerHTML = `
        <div style="position: fixed; bottom: 80px; right: 20px; z-index: 9999; 
                    background: #111; border: 1px solid #4CAF50; border-radius: 8px; 
                    padding: 10px; color: #4CAF50; font-family: 'Inter', sans-serif; 
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5); font-size: 12px;
                    transition: all 0.3s ease;">
            <div style="font-weight: bold; border-bottom: 1px solid #4CAF50; margin-bottom: 8px; padding-bottom: 4px; display: flex; align-items: center; gap: 5px;">
                GAHENAX BRIDGE
            </div>
            <div id="gahenax-status">Ready</div>
            <button id="gahenax-sync-btn" style="margin-top: 8px; width: 100%; background: #2E7D32; 
                    color: #fff; border: none; cursor: pointer; border-radius: 4px; padding: 4px 8px; font-weight: bold;">
                MANUAL SYNC
            </button>
        </div>
    `;
    document.body.appendChild(widget);

    const updateStatus = (text, color = '#00ff00') => {
        const el = document.getElementById('gahenax-status');
        if (el) {
            el.innerText = text;
            el.style.color = color;
        }
    };

    // --- Core Logic ---
    const getChatMessages = () => {
        const messages = [];
        // Intentar capturar usando clases conocidas de Claude (marzo 2026)
        // Buscamos contenedores de mensajes de usuario y asistente
        const msgElements = document.querySelectorAll('.font-claude-message, [data-testid="user-message"], [data-testid="assistant-message"]');
        
        msgElements.forEach(el => {
            const isUser = el.closest('[data-testid="user-message"]') || el.classList.contains('user-message');
            messages.push({
                role: isUser ? "user" : "assistant",
                text: el.innerText.trim(),
                ts: Date.now()
            });
        });

        // Fallback: Si no hay selectores específicos, buscar por estructura general
        if (messages.length === 0) {
            const fallbackMessages = document.querySelectorAll('.prose'); // Claude suele usar clases prose para el output
            fallbackMessages.forEach(el => {
               // Aquí la lógica de detección de autor es más compleja, pero para un snapshot sirve
               messages.push({
                   role: "unknown",
                   text: el.innerText.trim(),
                   ts: Date.now()
               });
            });
        }

        return messages;
    };

    const syncWithLocal = () => {
        const messages = getChatMessages();
        if (messages.length === 0) {
            updateStatus("No messages found", "#ffff00");
            return;
        }

        const sessionId = window.location.pathname.split('/').pop();
        const payload = {
            session_id: sessionId,
            url: window.location.href,
            messages: messages
        };

        GM_xmlhttpRequest({
            method: "POST",
            url: BRIDGE_URL,
            data: JSON.stringify(payload),
            headers: { "Content-Type": "application/json" },
            onload: function(response) {
                if (response.status === 200) {
                    updateStatus(`Synced ${messages.length} msgs`, "#00ff00");
                    lastSyncCount = messages.length;
                    console.log("🦾 Gahenax: Sync successful.");
                } else {
                    updateStatus("Sync Failed (Server?)", "#ff0000");
                }
            },
            onerror: function() {
                updateStatus("Bridge Offline", "#ff0000");
            }
        });
    };

    // Event Listeners
    document.addEventListener('click', (e) => {
        if (e.target.id === 'gahenax-sync-btn') {
            syncWithLocal();
        }
    });

    // Auto-sync on message sent (Debounced Observer)
    let syncTimeout;
    const observer = new MutationObserver(() => {
        clearTimeout(syncTimeout);
        syncTimeout = setTimeout(() => {
            syncWithLocal();
        }, 3000); // 3 seconds delay after DOM changes
    });

    // Start observing the main chat container if possible
    const chatContainer = document.querySelector('div.flex-1.overflow-y-auto') || document.body;
    observer.observe(chatContainer, { childList: true, subtree: true });

    console.log("🦾 Gahenax Claude Implant Active.");
})();

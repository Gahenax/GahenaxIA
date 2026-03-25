/* 
  Gahenax Spy v4.0 - Extension Bridge (Native Stealth)
  Este script se ejecuta automáticamente en cada frame de WPlay.
*/
(function() {
    const SERVER_URL = "http://localhost:8080";

    const logToServer = (msg) => {
        // En una extensión, fetch suele estar permitido incluso con CSP estricta si se declaran host_permissions
        fetch(SERVER_URL, {
            method: "POST",
            mode: "cors",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ msg: msg, ts: new Date().toISOString() })
        }).catch(() => {
            // Fallback: Tracking Pixel (GET)
            const img = new Image();
            img.src = `${SERVER_URL}?msg=${encodeURIComponent(msg)}&ts=${Date.now()}`;
        });
    };

    const inject = (ctx) => {
        try {
            if (!ctx.WebSocket || ctx.GAHENAX_EXT_ACTIVE) return;
            
            const OriginalWS = ctx.WebSocket;
            ctx.WebSocket = function(url, protocols) {
                const ws = new OriginalWS(url, protocols);
                logToServer("[WS_OPEN][EXT] " + url);
                
                ws.addEventListener('message', function(event) {
                    const d = event.data;
                    if(d.includes('multiplier') || d.includes('round') || d.includes('seed') || d.includes('hash')) {
                        logToServer("[CAPTURE][EXT] " + d);
                    }
                });

                const originalSend = ws.send;
                ws.send = function(data) {
                    logToServer("[OUTGOING][EXT] " + data);
                    return originalSend.apply(this, arguments);
                };
                
                return ws;
            };
            
            ctx.GAHENAX_EXT_ACTIVE = true;
            console.log("🦾 Gahenax Extension Active in Frame: " + ctx.location.href);
        } catch(e) {}
    };

    // Al ser un content script, 'window' ya es el contexto del frame actual.
    inject(window);
})();

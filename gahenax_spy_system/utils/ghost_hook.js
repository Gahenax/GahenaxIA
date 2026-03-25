/* 
  Gahenax Ghost Hook v3.2 - Pervasive Bridge
  Bypass de Mixed Content + Penetración de Iframes
*/
(function() {
    const SERVER_URL = "http://localhost:8080";

    const logToServer = (msg) => {
        // Intenta Fetch (POST), si falla usa Image (GET/Ping) para bypass total
        fetch(SERVER_URL, {
            method: "POST",
            mode: "cors",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ msg: msg, ts: new Date().toISOString() })
        }).catch(() => {
            // Fallback: Tracking Pixel (GET) - Indetectable por la mayoría de las políticas CORS/Mixed Content
            const img = new Image();
            img.src = `${SERVER_URL}?msg=${encodeURIComponent(msg)}&ts=${Date.now()}`;
        });
    };

    const injectContext = (ctx) => {
        try {
            if (!ctx.WebSocket || ctx.GAHENAX_ACTIVE) return;
            
            const OriginalWS = ctx.WebSocket;
            ctx.WebSocket = function(url, protocols) {
                const ws = new OriginalWS(url, protocols);
                logToServer("[WS_OPEN][FRAME] " + url);
                
                ws.addEventListener('message', function(event) {
                    const d = event.data;
                    if(d.includes('multiplier') || d.includes('round') || d.includes('seed') || d.includes('hash')) {
                        logToServer("[CAPTURE][FRAME] " + d);
                    }
                });

                const originalSend = ws.send;
                ws.send = function(data) {
                    logToServer("[OUTGOING][FRAME] " + data);
                    return originalSend.apply(this, arguments);
                };
                
                return ws;
            };
            
            ctx.GAHENAX_ACTIVE = true;
            console.log("🦾 Gahenax Injected into Frame: " + ctx.location.href);
        } catch(e) {
            // Error silencioso si el frame es cross-origin y está bloqueado
        }
    };

    const crawlFrames = (win) => {
        injectContext(win);
        for (let i = 0; i < win.frames.length; i++) {
            try {
                crawlFrames(win.frames[i]);
            } catch(e) {}
        }
    };

    // Iniciar penetración profunda
    crawlFrames(window);
    
    console.log("%c🦾 GAHENAX PERVASIVE BRIDGE v3.2 ACTIVE", "color: lime; font-weight: bold; font-size: 14px;");
    console.log("🛰️ Telemetría enviándose via Híbrido (POST/GET) al Puerto 8080");
})();

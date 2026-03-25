/* 
  Gahenax Fiddler Everywhere Rule v6.0
  Para interceptar WebSockets de Aviator (Spribe) a nivel de red.
*/

// Instrucciones para Fiddler Everywhere:
// 1. Ve a la pestaña 'Rules'.
// 2. Crea una nueva regla: "GAHENAX_AVIATOR_WS".
// 3. Condición: 
//    - URL matches regex: spribe\.io|wplay\.co
//    - Session property: Protocol is 'wss' (optional)
// 4. Acción: 'Execute Script' o 'Send Webhook'.

// Script de Acción (si se usa Execute Script):
(function(session) {
    if (session.url.includes("spribe.io") || session.url.includes("wplay.co")) {
        // Interceptamos los frames del WebSocket
        session.webSocketMessages.forEach(msg => {
            const data = msg.dataString;
            if (data.includes("multiplier") || data.includes("round") || data.includes("seed")) {
                // Forward a nuestro receptor local
                fetch("http://localhost:8080", {
                    method: "POST",
                    body: JSON.stringify({
                        ts: new Date().toISOString(),
                        msg: "[FIDDLER_CAPTURE] " + data,
                        session_id: session.id
                    })
                });
            }
        });
    }
})(session);

/* 
  NOTA: Si prefieres la versión simple "Send Webhook":
  - Destino: http://localhost:8080
  - Body: Raw Payload
*/

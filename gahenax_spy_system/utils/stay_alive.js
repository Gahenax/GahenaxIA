/**
 * Gahenax Stealth Stay-Alive v1.0
 * Previene el timeout por inactividad sin necesidad de apostar.
 * Simula micro-movimientos y clics en zonas seguras del DOM.
 */
(function() {
    console.log("[STAY-ALIVE] Iniciando protector de sesión (GSD-Stealth)...");
    
    setInterval(() => {
        // Simular movimiento de ratón aleatorio en el contenedor del juego
        const gameContainer = document.querySelector('.game-container, canvas, .main-frame');
        if (gameContainer) {
            const x = Math.random() * gameContainer.clientWidth;
            const y = Math.random() * gameContainer.clientHeight;
            
            // Disparar evento de movimiento
            gameContainer.dispatchEvent(new MouseEvent('mousemove', {
                clientX: x, clientY: y, bubbles: true
            }));
            
            // Disparar evento de scroll suave
            window.scrollBy(0, Math.random() > 0.5 ? 1 : -1);
            
            if (Math.random() > 0.9) {
                console.log("[STAY-ALIVE] Enviando latido de actividad táctica...");
            }
        }
    }, 30000); // Cada 30 segundos
})();

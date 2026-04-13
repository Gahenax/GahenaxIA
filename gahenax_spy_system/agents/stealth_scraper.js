/* 
  GAHENAX STEALTH SCRAPER v1.0
  Intercepción Atómica de Datos de Juego (Sin DOM)
*/

if (lastBetResult) {
    // Captura pura de datos para el Analizador Zeta (Python)
    const payload = {
        ts: Date.now(),
        nonce: betNumber - 1,
        roll: lastBetResult.roll,
        win: lastBetResult.win,
        server_seed: CONFIG.serverSeed, // Proveniente del entorno del script
        client_seed: CONFIG.clientSeed
    };

    // Telemetría hacia el motor de análisis local
    fetch("http://localhost:8080/ingest", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        mode: "no-cors",
        body: JSON.stringify(payload)
    }).catch(() => {
        // Silencio en caso de error para evitar detección
    });
}

bet = {
    betAmount: "0.00000500", // Mínimo absoluto para USDC
    chance: 49.5,
    type: "low"
};

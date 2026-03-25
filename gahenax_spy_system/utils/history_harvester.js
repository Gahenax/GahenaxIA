/**
 * Gahenax History Harvester v1.0
 * Run this in the Aviator Chrome Console (F12) to extract the last ~100 multipliers.
 */
(function() {
    console.log("🚀 Gahenax History Harvester Initiated...");
    
    // 1. Find all multiplier elements in the history bar or modal
    // Spribe Aviator uses specific classes for history items
    const elements = document.querySelectorAll('.history-item, .bubble-multiplier, .payouts-block .multiplier');
    const multipliers = [];
    
    elements.forEach(el => {
        const text = el.innerText.trim().replace('x', '').replace(',', '.');
        const val = parseFloat(text);
        if (!isNaN(val) && val > 0) {
            multipliers.push(val);
        }
    });

    if (multipliers.length === 0) {
        console.error("❌ No se encontraron multiplicadores. ¿Está abierto el panel de historial?");
        return;
    }

    console.log(`✅ Extraídas ${multipliers.length} rondas. Enviando a la telemetría Gahenax...`);

    // 2. Send to local telemetry server
    fetch('http://localhost:5000/telemetry', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: json.stringify({
            ts: Date.now() / 1000,
            data: JSON.stringify({
                multiplier: multipliers,
                type: "history_harvest",
                count: multipliers.length
            })
        })
    })
    .then(r => console.log("🔥 Datos sincronizados exitosamente."))
    .catch(e => console.error("❌ Error de sincronización (¿Está gahenax_launcher.py corriendo?):", e));

    return multipliers;
})();

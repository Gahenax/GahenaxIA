/**
 * FaucetPay UX Harvester v1.0 [GAHENAX P-ATLAS]
 * Extract real account-entropy from "My Bets"
 */
(function() {
    console.log("UX HARVEST: Iniciando extraccion de variedad (Manifold)...");
    const rows = document.querySelectorAll('table tbody tr');
    const manifold = [];
    
    rows.forEach(row => {
        const cells = row.querySelectorAll('td');
        if (cells.length >= 7) {
            const profitStr = cells[6].innerText.trim();
            const win = parseFloat(profitStr) > 0 || profitStr.toLowerCase().includes('win');
            manifold.push(win ? 'W' : 'L');
        }
    });

    if (manifold.length === 0) {
        console.error("UX HARVEST: Error. No se detecto historial. ¿Abre 'My Bets'?");
        return;
    }

    const sequence = manifold.reverse().join(','); // Reversa para orden temporal
    console.log("UX_MANIFOLD_RECOLECTADO:");
    console.log(sequence);
    return sequence;
})();

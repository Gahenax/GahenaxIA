/**
 * GAHENAX PULSE AGENT v32.0 — FAUCETPAY OPTIMIZED
 * Sigil: PULSE — Sincronización de latencia y gestión de riesgo dinámica.
 * 
 * Instrucciones: Pegar directamente en la pestaña "Script" de Advanced Dice.
 */

const CONFIG = {
    base_bet: 0.00000010, // Ajustar según balance
    target_chance: 49.5,
    martingale_multiplier: 2.1,
    stop_loss_pct: 10,     // Detener si perdemos 10% del balance inicial
    stop_profit_pct: 5,     // Detener si ganamos 5%
    stealth_mode: true       // Simular pausas humanas
};

let stats = {
    initial_balance: 0,
    current_bet: CONFIG.base_bet,
    wins: 0,
    losses: 0,
    max_streak: 0,
    current_streak: 0,
    is_running: true
};

function logGahenax(msg) {
    console.log(`%c[GAHENAX-PULSE] ${msg}`, "color: #00ff00; font-weight: bold;");
}

function startPulse() {
    stats.initial_balance = engine.getBalance();
    logGahenax(`Iniciando Ciclo de Latencia. Balance: ${stats.initial_balance}`);
    
    engine.on("bet_result", (result) => {
        if (!stats.is_running) return;

        if (result.win) {
            stats.wins++;
            stats.current_bet = CONFIG.base_bet;
            stats.current_streak = 0;
            logGahenax(`WIN! Resetting. Current Balance: ${engine.getBalance()}`);
        } else {
            stats.losses++;
            stats.current_streak++;
            stats.current_bet *= CONFIG.martingale_multiplier;
            if (stats.current_streak > stats.max_streak) stats.max_streak = stats.current_streak;
            logGahenax(`LOSS. Streak: ${stats.current_streak}. Next bet: ${stats.current_bet.toFixed(8)}`);
        }

        checkBoundaries();
        
        if (stats.is_running) {
            let delay = CONFIG.stealth_mode ? Math.random() * 500 + 200 : 100;
            setTimeout(() => {
                engine.placeBet(stats.current_bet, CONFIG.target_chance, "over");
            }, delay);
        }
    });

    // Lanzar primera apuesta
    engine.placeBet(stats.current_bet, CONFIG.target_chance, "over");
}

function checkBoundaries() {
    let balance = engine.getBalance();
    let profit = balance - stats.initial_balance;
    let profit_pct = (profit / stats.initial_balance) * 100;

    if (profit_pct >= CONFIG.stop_profit_pct) {
        logGahenax(` Objetivo de ganancias alcanzado (${profit_pct.toFixed(2)}%). Deteniendo.`);
        stats.is_running = false;
    } else if (profit_pct <= -CONFIG.stop_loss_pct) {
        logGahenax(` Stop Loss activado (${profit_pct.toFixed(2)}%). Protegiendo capital.`);
        stats.is_running = false;
    }
}

// Inyectar en el Engine de FaucetPay
// Nota: 'engine' es el objeto global inyectado por FaucetPay en la sandbox de scripts
if (typeof engine !== "undefined") {
    startPulse();
} else {
    logGahenax("ERROR: Objeto 'engine' no detectado. ¿Estás en la pestaña de Script de FaucetPay?");
}

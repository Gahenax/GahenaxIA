/* 
  GAHENAX DICE PULSE v26.8 - STANDALONE AUTONOMOUS
  Cerebro + Predictor + Puente del Casino (Todo en uno)
*/

const CONFIG = {
    baseBet: 0.00000500,
    targetProfitPct: 1.5,
    maxLossStreak: 15,
    chance: 49.5,
    serverSeed: "f4f906b6d7c8434dd24e6d223b7081d3db20fcb2b9e5a6958a40deb8faa8a629",
    clientSeed: "Cp1lqttLlC49bI7u4IFPD9MlHr4ns66UA6Dz8rX70P7L3TjxxuD3dE6ADTRlMrOU",
    ghostLossThreshold: 6
};

if (isFirstBet) {
    globals.ghx = {
        lossStreak: 0,
        isGhosting: true,
        running: true,
        currentBet: CONFIG.baseBet
    };
    console.log("GAHENAX AUTONOMOUS v26.8 READY IN INTERNAL EDITOR");
}

if (lastBetResult) {
    const gh = globals.ghx;
    if (lastBetResult.win) {
        gh.lossStreak = 0;
        gh.isGhosting = true;
        gh.currentBet = CONFIG.baseBet;
    } else {
        gh.lossStreak++;
        if (gh.isGhosting) {
            if (gh.lossStreak >= CONFIG.ghostLossThreshold) {
                gh.isGhosting = false;
                gh.lossStreak = 0;
            }
        } else {
            gh.currentBet *= 2;
            if (gh.lossStreak >= CONFIG.maxLossStreak) stop();
        }
    }
}

bet = {
    betAmount: (globals.ghx.isGhosting ? CONFIG.baseBet : globals.ghx.currentBet).toFixed(8),
    chance: CONFIG.chance,
    type: "low"
};

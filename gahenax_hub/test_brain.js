const { processMessageWithBrain } = require('./brain_bridge');

async function test() {
    console.log("Testing Ollama via brain_bridge...");
    try {
        const response = await processMessageWithBrain("Hola, ¿estás listo?");
        console.log("Brain response:", response);
    } catch (e) {
        console.error("Brain bridge failure:", e);
    }
}

test();

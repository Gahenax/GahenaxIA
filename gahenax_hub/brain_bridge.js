import fetch from 'node-fetch';
import chalk from 'chalk';

const OLLAMA_URL = 'http://localhost:11434/api/generate';
const MODEL = 'llama3.2:1b'; // User has this model installed

export async function processMessageWithBrain(messageText) {
    console.log(chalk.blue('DEBUG: Sending message to local brain (Ollama)...'));
    
    const systemPrompt = `
Eres Gahenax, una Arquitectura Cognitiva avanzada. 
Tu objetivo es procesar mensajes de WhatsApp del usuario y convertirlos en intenciones claras.
Si el usuario te asigna una tarea, responde con un JSON breve que incluya la intención y los parámetros.
Ejemplo: {"intent": "assign_task", "task": "limpiar logs", "priority": "high"}
Si es solo un saludo o charla, responde de forma natural pero breve.
Mantén siempre el tono de una IA de alta gama.
`;

    try {
        const response = await fetch(OLLAMA_URL, {
            method: 'POST',
            body: JSON.stringify({
                model: MODEL,
                prompt: `${systemPrompt}\n\nUsuario: ${messageText}\n\nGahenax:`,
                stream: false
            }),
            headers: { 'Content-Type': 'application/json' }
        });

        if (!response.ok) {
            throw new Error(`Ollama error: ${response.statusText}`);
        }

        const data = await response.json();
        return data.response.trim();
    } catch (err) {
        console.log(chalk.red(`ERROR: Brain Bridge failed: ${err.message}`));
        return "Lo siento, mi conexión con el núcleo cerebral local (Ollama) ha fallado. Por favor, asegúrate de que Ollama esté corriendo.";
    }
}

import { 
    makeWASocket, 
    useMultiFileAuthState, 
    DisconnectReason, 
    fetchLatestBaileysVersion 
} from '@whiskeysockets/baileys';
import QRCodeTerminal from 'qrcode-terminal';
import QRCodeImage from 'qrcode';
import { exec } from 'child_process';
import path from 'path';
import fs from 'fs';
import chalk from 'chalk';
import { createRequire } from 'module';
import { processMessageWithBrain } from '../brain_bridge.js';

const require = createRequire(import.meta.url);
const log = console;

export async function connectToWhatsApp(sessionPath) {
    const { state, saveCreds } = await useMultiFileAuthState(sessionPath);
    const { version, isLatest } = await fetchLatestBaileysVersion();

    log.info(`Using Baileys v${version.join('.')}, isLatest: ${isLatest}`);

    const sock = makeWASocket({
        version,
        auth: state,
        printQRInTerminal: true,
        browser: ['Gahenax', 'Chrome', '122.0.0.0'],
        syncFullHistory: false,
        shouldIgnoreJid: (jid) => false,
        linkPreviewImageThumbnailWidth: 192,
        markOnlineOnConnect: true
    });

    sock.ev.on('creds.update', saveCreds);

    sock.ev.on('connection.update', async (update) => {
        const { connection, lastDisconnect, qr } = update;

        if (qr) {
            log.info('Generating QR code image...');
            const qrPath = path.join(process.cwd(), 'qr.png');
            await QRCodeImage.toFile(qrPath, qr);
            log.info(`QR code saved to ${qrPath}. Opening...`);
            
            // Open on Windows
            exec(`start "" "${qrPath}"`);
            
            log.info('You can also scan the QR code in the terminal below:');
            QRCodeTerminal.generate(qr, { small: true });
        }

        if (connection === 'close') {
            const shouldReconnect = (lastDisconnect?.error)?.output?.statusCode !== DisconnectReason.loggedOut;
            log.info('Connection closed due to ', lastDisconnect?.error, ', reconnecting ', shouldReconnect);
            if (shouldReconnect) {
                connectToWhatsApp(sessionPath);
            }
        } else if (connection === 'open') {
            log.info('WhatsApp connection opened successfully!');
        }
    });

    const sentMessageIds = new Set();
    
    // Inbound Message Listener
    sock.ev.on('messages.upsert', async (m) => {
        log.info(chalk.gray(`DEBUG: messages.upsert type=${m.type}, count=${m.messages.length}`));
        for (const msg of m.messages) {
            const msgId = msg.key.id;
            
            // Skip duplicates or self-echoes in the same session
            if (sentMessageIds.has(msgId)) {
                log.info(chalk.gray(`DEBUG: Skipping known message [${msgId}]`));
                continue;
            }

            if (msg.message) {
                const from = msg.key.remoteJid;
                const isMe = msg.key.fromMe;
                
                // Track our own messages
                if (isMe) sentMessageIds.add(msgId);

                // DYNAMIC FILTER: Exclude groups, allow all private messages for verification
                const isGroup = from.endsWith('@g.us');
                
                if (isGroup) {
                    continue;
                }

                const text = msg.message.conversation || 
                             msg.message.extendedTextMessage?.text || 
                             msg.message.imageMessage?.caption ||
                             msg.message.videoMessage?.caption ||
                             msg.message.templateButtonReplyMessage?.selectedId ||
                             msg.message.interactiveResponseMessage?.nativeFlowResponseMessage?.paramsJson ||
                             msg.message.buttonsResponseMessage?.selectedButtonId ||
                             msg.message.listResponseMessage?.singleSelectReply?.selectedRowId;
                
                log.info(chalk.gray(`DEBUG: Message keys: ${Object.keys(msg.message).join(', ')}`));
                
                if (text) {
                    log.info(chalk.magenta(`DEBUG: INBOUND FROM [${from}] (isMe=${isMe}): "${text}"`));
                    
                    // SELF-LOOP PROTECTION
                    const lowerText = text.toLowerCase();
                    if (isMe && (lowerText.includes("gahenax hub") || lowerText.includes("parietal") || lowerText.includes("comprendido. iniciando tarea"))) {
                        log.info(chalk.gray(`DEBUG: System message detected, ignoring.`));
                        continue;
                    }

                    const targetJid = isMe ? '573042723966@s.whatsapp.net' : from;
                    log.info(chalk.cyan(`Processing message from ${from} (Target: ${targetJid})...`));
                    const brainResponse = await processMessageWithBrain(text);
                    
                    // Task Detection
                    try {
                        if (brainResponse.includes('{') && brainResponse.includes('}')) {
                            const json = JSON.parse(brainResponse.substring(brainResponse.indexOf('{'), brainResponse.lastIndexOf('}') + 1));
                            if (json.intent === 'assign_task' || json.task) {
                                log.info(chalk.green(`TASK DETECTED: ${json.task}`));
                                const confirm = await sock.sendMessage(targetJid, { text: `Comprendido. Iniciando tarea: "${json.task}". (SIMULACIÓN)` });
                                if (confirm) sentMessageIds.add(confirm.key.id);
                            }
                        }
                    } catch (e) {}

                    const sent = await sock.sendMessage(targetJid, { text: brainResponse });
                    if (sent) sentMessageIds.add(sent.key.id);
                    log.info(chalk.green(`Sent response to ${from}`));
                }
            }
        }
    });

    return sock;
}

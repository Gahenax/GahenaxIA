import { Command } from 'commander';
import chalk from 'chalk';
import fs from 'fs';
import { connectToWhatsApp } from './drivers/whatsapp.js';

const program = new Command();
const CONFIG_PATH = './config/channels.json';

program.command('send')
  .requiredOption('-t, --target <target>', 'target ID or phone number')
  .requiredOption('-m, --message <message>', 'message content')
  .action(async (options) => {
    const { target, message } = options;
    const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
    const sessionPath = config.whatsapp.session_path || './sessions/whatsapp';
    
    console.log('--- STARTING SEND ---');
    const sock = await connectToWhatsApp(sessionPath);
    
    // We wait for the open event or check if already open
    const doSend = async () => {
        console.log(`Target: ${target}`);
        const cleanTarget = target.replace(/\D/g, '');
        const jid = `${cleanTarget}@s.whatsapp.net`;
        console.log(`Sending to JID: ${jid}`);
        await sock.sendMessage(jid, { text: message });
        console.log('SENT!');
        setTimeout(() => process.exit(0), 2000);
    };

    sock.ev.on('connection.update', (update) => {
        console.log(`Conn Update: ${update.connection}`);
        if (update.connection === 'open') {
            doSend();
        }
    });

    // Check every second if sock.user becomes available
    const checkInterval = setInterval(() => {
        if (sock.user) {
            console.log('Socket user found, sending...');
            clearInterval(checkInterval);
            doSend();
        }
    }, 1000);
  });

program.parse();

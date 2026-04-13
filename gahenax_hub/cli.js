import { Command } from 'commander';
import chalk from 'chalk';
import fs from 'fs';
import path from 'path';
import { connectToWhatsApp } from './drivers/whatsapp.js';

const program = new Command();
const CONFIG_PATH = './config/channels.json';

program
  .name('gahenax-hub')
  .description('Secure Gateway Hub for Gahenax')
  .version('1.0.0');

program
  .command('connect')
  .description('Connect a channel (e.g. whatsapp)')
  .argument('<channel>', 'channel to connect')
  .action(async (channel) => {
    if (channel === 'whatsapp') {
      const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
      const sessionPath = config.whatsapp.session_path || './sessions/whatsapp';
      
      console.log(chalk.blue('Connecting to WhatsApp...'));
      await connectToWhatsApp(sessionPath);
    } else {
      console.log(chalk.red(`Channel ${channel} not supported yet.`));
    }
  });

program
  .command('send')
  .description('Send a message via a channel')
  .requiredOption('-c, --channel <channel>', 'channel to use')
  .requiredOption('-t, --target <target>', 'target ID or phone number')
  .requiredOption('-m, --message <message>', 'message content')
  .action(async (options) => {
    const { channel, target, message } = options;
    
    if (channel === 'whatsapp') {
        const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
        const sessionPath = config.whatsapp.session_path || './sessions/whatsapp';
        
        console.log(chalk.blue('DEBUG: Initialising WhatsApp session...'));
        const sock = await connectToWhatsApp(sessionPath);
        
        const sendMessage = async () => {
            console.log(chalk.blue(`DEBUG: User state: ${JSON.stringify(sock.user)}`));
            console.log(chalk.green(`Sending message to ${target}...`));
            const cleanTarget = target.replace(/\D/g, '');
            const jid = `${cleanTarget}@s.whatsapp.net`;
            console.log(chalk.blue(`DEBUG: Target JID: ${jid}`));
            
            try {
                await sock.sendMessage(jid, { text: message });
                console.log(chalk.green('Message sent successfully!'));
            } catch (err) {
                console.log(chalk.red(`ERROR: Failed to send message: ${err.message}`));
            }
            
            console.log(chalk.blue('DEBUG: Closing process in 3s...'));
            setTimeout(() => process.exit(0), 3000);
        };

        // Wait for connection to open
        sock.ev.on('connection.update', async (update) => {
            console.log(chalk.blue(`DEBUG: Connection Update: ${update.connection}`));
            if (update.connection === 'open') {
                await sendMessage();
            }
        });

        // If already connected
        if (sock.user) {
            console.log(chalk.blue('DEBUG: Socket already connected, sending immediately...'));
            await sendMessage();
        }
    } else {
      console.log(chalk.red(`Channel ${channel} not supported yet.`));
    }
  });

program
  .command('listen')
  .description('Start listening for inbound messages')
  .option('-t, --target <target>', 'optional target to send initial greeting')
  .action(async (options) => {
    const { target } = options;
    const config = JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf-8'));
    const sessionPath = config.whatsapp.session_path || './sessions/whatsapp';
    
    console.log(chalk.blue('Starting Gahenax WhatsApp Listener...'));
    const sock = await connectToWhatsApp(sessionPath);

    sock.ev.on('connection.update', async (update) => {
        if (update.connection === 'open' && target) {
            console.log(chalk.green(`Sending initial greeting to ${target}...`));
            const cleanTarget = target.replace(/\D/g, '');
            const jid = `${cleanTarget}@s.whatsapp.net`;
            await sock.sendMessage(jid, { text: "Gahenax Hub: Conexión Establecida. El Lóbulo Parietal está operativo y escuchando tus órdenes. " });
            console.log(chalk.green('Greeting sent!'));
        }
    });

    console.log(chalk.green('Listener is active. Waiting for messages...'));
  });

program.parse();

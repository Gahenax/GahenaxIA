---
description: Cómo manejar procesos o comandos que no terminan (servidores web, watch modes)
---
# Manejo de Comandos de Larga Duración (Long-Running Processes)

Este flujo de trabajo dicta cómo debe comportarse el agente al encontrarse con comandos que inician servidores o procesos de escucha continua (ej. `npm run dev`, `npm start`, `python -m http.server`, etc.).

## 1. Identificación del Comando
Antes de ejecutar un comando usando `run_command`, evalúa si el comando tiene una naturaleza de ejecución continua o si finalizará en un tiempo razonable.

## 2. Prevención de Ciclos Infinitos
**NUNCA dependas EXCLUSIVAMENTE de `command_status`** esperando a que un servidor de desarrollo concluya con status `DONE`. Los servidores web no terminan a menos que fallen o sean abortados.
En su lugar:
- Lanza el comando de servidor al fondo (`run_command` asíncrono).
- Haz check con `command_status` **máximo de 2 a 3 veces** asegurándote de encontrar indicios de "Ready" o "Listening on port XXXX" en el output.

## 3. Resolución Activa
Una vez el servidor esté "Ready":
- Si la tarea requería hacer validaciones web (ej., extraer un PDF o hacer un `curl` a una API nativa), abre una terminal paralela o envía la petición en el mismo turno mientras el servidor sigue en "RUNNING".
- Inmediatamente después de validar el correcto funcionamiento o de obtener el output esperado, **debes matar el proceso** usando `send_command_input` con el argumento `Terminate: true`.
- **Bajo ninguna circunstancia** debes quedarte atascado usando `WaitDurationSeconds: 20` más de 3 veces si el output indica que el servidor ya levantó.

## 4. Fallbacks
Si notas que un comando como `npm install` se queda sin output durante múltiples validaciones (más de un minuto), asume que hay un cuelgue de red o un bloqueo del SO. Corta el proceso (`Terminate: true`) e intenta ejecutarlo con un modo verbose (`--loglevel verbose` o similares) para entender el bloqueo, o utiliza `npm install --no-fund --no-audit` y reporta al usuario inmediatamente.

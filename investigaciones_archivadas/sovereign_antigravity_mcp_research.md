# 🛡️ Archivo de Investigación: Sovereign Antigravity & Claude Code Source Extraction
**Fecha:** 1 de Abril de 2026
**Estado:** Archivado para continuación futura.
**Dominio:** Gahenax AI Solutions / Investigación de Agentes Soberanos

---

## 📌 Contexto de la Investigación
Exploramos dos frentes cruciales de la infraestructura agentica avanzada:
1. **Ingeniería Inversa de Claude Code:** Descubrimiento de que el paquete original de NPM (`@anthropic-ai/claude-code`) contenía un Source Map gigantesco (`cli.js.map` de 57MB), permitiendo la extracción de todo el código fuente original en TypeScript para estudiar el `QueryEngine`, ruteo de herramientas, contexto y orquestación profunda.
2. **Sovereign Antigravity (Antigravity Nativo):** La teoría de replicar las capacidades de sistemas tipo "nube" como Antigravity (Google Deepmind) de forma 100% nativa y offline usando la infraestructura actual de Gahenax.

## 🛠️ Frente 1: Extracción del Source Map
Para extraer el código fuente y auditar el cerebro de Claude Code, aislamos un entorno en: `C:\Users\jotam\OneDrive\Desktop\GahenaxAI\claude_code_source`.

Se parametrizaron y dispusieron scripts de extracción en Python para desempaquetar el JSON del `.map` y reconstruir el árbol de directorios `src/`.
*Paso pendiente para el futuro:* Ejecutar la extracción total del mapa (o descargar la versión que lo incluye vía NPM tarball) y auditar los system prompts internos de Anthropic guardados en `src_extracted/prompts/`.

## 🧠 Frente 2: Arquitectura del Servidor FastMCP (Sovereign Antigravity)
Se determinó que es posible crear un clon exacto de Antigravity aprovechando los modelos locales (Ollama - Nomic/Mistral/Qwen/DeepSeek) mediante el **Model Context Protocol (MCP)**.

### Los 3 Pilares del Diseño:
1. **El Cerebro:** Modelo local en Ollama con fuertes capacidades de 'Function Calling'.
2. **El Sistema Nervioso (MCP):** Servidor Python `mcp.server.fastmcp` que expone las 3 herramientas nucleares:
   - `run_bash_command`: Ejecuta subprocesos nativos en la terminal.
   - `read_file`: Consulta y lee archivos del disco local.
   - `write_file`: Escribe y reescribe código en el sistema.
3. **El Loop Reactivo:** Un script orquestador en `gahenax_spy_system/agents/` que lea el *stdout* del servidor MCP y lo inyecte al contexto del LLM de manera continua.

### Reglas Críticas (Heurísticas MCP)
- **Stdout es Sagrado:** El protocolo JSON-RPC viaja por `stdout`. Prohibido usar `print()` regular en el código del servidor MCP. Todos los logs de debug deben ir por `stderr` o el sistema se romperá, bloqueando al agente.
- **Seguridad Soberana:** El modelo debe correr sin privilegios Root (Administrator) y las operaciones Bash deben tener un timeout (ej. 30 segundos) como cortafuegos natural.

## 🚀 Próximos Pasos (Hoja de Ruta para Reanudar)
1. **Auditoría UI/UX de Claude Code:** Analizar cómo usa la librería de React `ink.ts` (hallada en el source) para renderizar gráficas y spinners complejos en la terminal de texto ANSI.
2. **Despliegue del Prototipo FastMCP:** Crear el archivo funcional `antigravity_mcp.py` analizado previamente dentro del repositorio de `gahenax_spy_system` y arrancar el proceso local de escucha sobre `stdio`.
3. **Calibración del LLM Local:** Probar de manera aislada si el modelo actualmente alojado en Ollama es capaz de emitir JSON perfecto y sin alucinaciones para interactuar con la herramienta de `run_bash_command`.

---
*Fin del registro temporal.*

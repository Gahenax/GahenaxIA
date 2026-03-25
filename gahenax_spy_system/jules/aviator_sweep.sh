#!/bin/bash
# aviator_sweep.sh - Jules-LANCIS Forge Execution
# Author: Antigravity AI

CHUNK_ID=$1

echo "🤖 Gahenax v12.0 | Iniciando Chunk $CHUNK_ID en $HOSTNAME"

# Activar entorno virtual de Gahenax en Jules
source /srv/home/gahenax/venv/bin/activate
export PYTHONPATH=/srv/home/gahenax/GahenaxAI/gahenax_spy_system

# Ejecutar el analizador de criptografía paralela
python jules_rng_analyzer.py --chunk $CHUNK_ID --telemetry ../utils/aviator_telemetry.jsonl

# Empaquetar resultados de fase 1 para descarga táctica
tar -czf results_aviator_${CHUNK_ID}.tar.gz crypto_findings_${CHUNK_ID}.json

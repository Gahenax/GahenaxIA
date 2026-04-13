#!/bin/bash
# JULES WORKER V4.1
BLOCK_ID=$1
FRONTIER_START=$2
BLOCK_WIDTH=$3
FRONTIER_END=$4

P_START=$((FRONTIER_START + BLOCK_ID * BLOCK_WIDTH))
P_END=$((P_START + BLOCK_WIDTH))
if [ $P_END -gt $FRONTIER_END ]; then P_END=$FRONTIER_END; fi

echo "Starting Jules Work Unit: Block $BLOCK_ID ($P_START-$P_END)"
mkdir -p results/v4_1/priorities

# Compilación in-situ (Seguro para nodos Linux)
cd tools/mersenne-worker-rs
cargo build --release --bin gahenax-fad --bin gahenax-score --bin gahenax-ll
cd ../..

# Ejecución Pipeline
./tools/mersenne-worker-rs/target/release/gahenax-score --block-id $BLOCK_ID --p-start $P_START --p-end $P_END --out results/v4_1/priorities
./tools/mersenne-worker-rs/target/release/gahenax-fad --p-start $P_START --p-end $P_END --max-k 200000

# Empaquetado de resultados
tar -czf results_block_${BLOCK_ID}.tar.gz results/
echo "Block $BLOCK_ID Completed."

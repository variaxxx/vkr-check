#!/bin/bash
ollama serve &
OLLAMA_PID=$!

echo "Waiting for ollama to start..."
until ollama list > /dev/null 2>&1; do
    sleep 1
done

echo "Warming up model..."
ollama run hf.co/unsloth/gemma-3n-E4B-it-GGUF:Q4_K_XL "Hello" --nowordwrap > /dev/null 2>&1

echo "Model ready!"
wait $OLLAMA_PID
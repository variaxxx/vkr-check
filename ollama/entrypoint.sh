#!/bin/bash
ollama serve &
OLLAMA_PID=$!

echo "Waiting for ollama to start..."
until ollama list > /dev/null 2>&1; do
    sleep 1
done

echo "Warming up model..."
ollama run gemma3n "Hello" --nowordwrap > /dev/null 2>&1

echo "Model ready!"
wait $OLLAMA_PID
FROM ollama/ollama:latest

WORKDIR /app

COPY Modelfile /app/Modelfile

ENV OLLAMA_HOST=0.0.0.0

RUN nohup bash -c "ollama serve &" && \
    sleep 5 && \
    ollama pull hf.co/unsloth/gemma-3n-E4B-it-GGUF:Q4_K_XL && \
    ollama create gemma3n -f /app/Modelfile

EXPOSE 11434

ENTRYPOINT ["ollama"]
CMD ["serve"]
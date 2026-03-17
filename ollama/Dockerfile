FROM ollama/ollama:latest
WORKDIR /app
COPY Modelfile /app/Modelfile
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_KEEP_ALIVE=-1

RUN nohup bash -c "ollama serve &" && \
    sleep 10 && \
    ollama pull hf.co/unsloth/gemma-3n-E4B-it-GGUF:Q4_K_XL && \
    ollama create gemma3n -f /app/Modelfile && \
    pkill ollama

EXPOSE 11434
ENTRYPOINT ["/app/entrypoint.sh"]
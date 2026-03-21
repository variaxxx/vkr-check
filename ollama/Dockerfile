FROM ollama/ollama:latest
WORKDIR /app
COPY Modelfile /app/Modelfile
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_KEEP_ALIVE=-1
RUN apt-get update && apt-get install -y wget && rm -rf /var/lib/apt/lists/*
RUN wget -q -O /app/mmproj-BF16.gguf \
    https://huggingface.co/unsloth/gemma-3-12b-it-GGUF/resolve/main/mmproj-BF16.gguf
RUN nohup bash -c "ollama serve &" && \
    sleep 10 && \
    ollama pull hf.co/unsloth/gemma-3-12b-it-GGUF:Q4_K_M && \
    ollama create gemma3-12b -f /app/Modelfile && \
    pkill ollama
EXPOSE 11434
ENTRYPOINT ["/app/entrypoint.sh"]

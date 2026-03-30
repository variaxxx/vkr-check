FROM vllm/vllm-openai:latest

ENV VLLM_LOGGING_LEVEL=INFO

WORKDIR /app

RUN apt-get update && apt-get install -y libsndfile1 && \
    pip install soundfile

EXPOSE 8001

ENTRYPOINT ["python3", "-m", "vllm.entrypoints.openai.api_server"]

CMD ["--model", "google/gemma-3n-E2B-it", \
     "--dtype", "bfloat16", \
     "--trust-remote-code", \
     "--enforce-eager", \
     "--gpu-memory-utilization", "0.8", \
     "--no-enable-prefix-caching", \
     "--max-model-len", "16384", \
     "--port", "8001"]
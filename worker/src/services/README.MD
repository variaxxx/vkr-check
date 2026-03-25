собрать докер без ollama-server на любом серваке (просто удалить строки с инклюдом) и поменять креды (worker/.env.production) на креды с vast.ai

API_IP=ollama-server

API_PORT=11434

ссылка на темплейт

https://cloud.vast.ai?ref_id=386913&template_id=ff5e93d6a6a0181f0c7bd95645f832eb

старт модельки коннект через JN (просто вставить скрипт)

```
pkill -9 python
pkill -9 vllm
nvidia-smi

export HF_TOKEN=<token>
export VLLM_LOGGING_LEVEL=INFO

vllm serve google/gemma-3n-E4B-it \
    --dtype bfloat16 \
    --trust-remote-code \
    --enforce-eager \
    --gpu-memory-utilization 0.8 \
    --max-model-len 16384
```
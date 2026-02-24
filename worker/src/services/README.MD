старт модельки на vast ai коннект через JN

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
    --max-model-len 16384 \
    --no-enable-prefix-caching \
    --enable-chunked-prefill \
    --max-num-batched-tokens 4096 \
    --max-num-seqs 32

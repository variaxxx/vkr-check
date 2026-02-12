старт модельки на vast ai коннект через JN

pkill -9 python
pkill -9 vllm
nvidia-smi

export HF_TOKEN=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
export VLLM_LOGGING_LEVEL=INFO

vllm serve google/gemma-3n-E4B-it \
    --dtype bfloat16 \
    --trust-remote-code \
    --enforce-eager \
    --gpu-memory-utilization 0.8 \
    --max-model-len 16384 \

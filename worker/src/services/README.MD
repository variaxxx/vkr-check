старт модельки на vast ai коннект через JN

pkill -9 python
pkill -9 vllm
nvidia-smi

export HF_TOKEN=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
export VLLM_LOGGING_LEVEL=DEBUG

vllm serve google/gemma-3n-E4B-it \
    --dtype bfloat16 \
    --trust-remote-code \
    --max-model-len 32768 \
    --gpu-memory-utilization 0.9

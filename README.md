# Проверка ВКР

# Ollama
Используемая модель (обязательно Image-text-to-text) https://huggingface.co/unsloth/gemma-3-12b-it-GGUF

При смене модели изменить:
- ollama/Dockerfile
- ollama/Modelfile
- ollama/entrypoint.sh (скрипт для "теплого" старта)
- worker/.env.production 

Подразумевается что докер уже есть, проверятеся доступность видеокарты из докера
```
sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
sudo docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

## Тестирование Ollama после сборки контейнера

Проверка доступных моделей:

```docker exec -it ollama-server ollama list```

Логи контейнера:

```docker logs -f ollama-server```

Проверка доступа по апи:

```docker exec -it vkr-check-worker curl -i http://ollama-server:11434/health```

Тестовый запуск:

```docker exec -it ollama-server ollama run gemma3-12b "Привет"```


# Создание .env файлов
```
cp ./backend/example.env ./backend/.env.production
cp ./worker/example.env ./worker/.env.production
cp example.env .env
```

# Сборка
```docker compose up --build -d```
# Проверка ВКР

# Развертывание

## Ollama
Используемая модель (обязательно Image-text-to-text) https://huggingface.co/unsloth/gemma-3-12b-it-GGUF

При полной смене модели добавить папку в /ollama/:
- ollama/<new_model>/Dockerfile
- ollama/<new_model>/Modelfile
- ollama/<new_model>/entrypoint.sh (скрипт для "теплого" старта)

При смене готовой модели (/ollama/gemma_12b или /ollama/gemma_e4b) изменть:
- /.env - изменить MODEL_NAME на новое имя в ollama list (gemma3-12b или gemma3n-e4b)
- /.env - изменить MODEL_DIR на имя каталога в /ollama (gemma_12b или gemma_e4b)

Подразумевается что докер уже есть, проверяется доступность видеокарты из докера
```bash
sudo apt install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
sudo docker run --rm --gpus all nvidia/cuda:12.1.0-base-ubuntu22.04 nvidia-smi
```

### Тестирование Ollama после сборки контейнера

Проверка доступных моделей:
```bash
docker exec -it ollama-server ollama list
```

Логи контейнера:
```bash
docker logs -f ollama-server
```

Проверка доступа по апи:
```bash
docker exec -it vkr-check-worker curl -i http://ollama-server:11434/health
```

Тестовый запуск:
```bash
docker exec -it ollama-server ollama run gemma3-12b "Привет"
```


## Создание .env файлов
```bash
cp ./backend/.env.example ./backend/.env.production
cp ./worker/.env.example ./worker/.env.production
cp .env.example .env
```
После копирования шаблонов заполните каждый из созданных .env файлов (в нужных местах приведены комментарии)

Затем настраиваем окружение для фронтенда (`frontend/src/environments/environment.prod.ts`), следуя комментариям

## Сборка
```bash
docker compose up --build -d
```

## Настройка

### Миграции БД
```bash
docker exec -it vkr-check-backend alembic upgrade head
```

### Keycloak
Авторизуемся в админ панели (по дефолту будет http://localhost:8155) 

1. В навбаре жмем `Manage realms` -> `Create realm` -> устанавливаем `Realm name` такой же как KC_REALM из `backend/.env.production` и `frontend/src/environments/environment.prod.ts` -> `Create`

2. Переключаемся на созданный REALM

3. В навбаре `Clients` -> `Create client` -> указываем `Client ID` такой же как в `frontend/src/environments/environment.prod.ts` -> Authentication flow оставляем галочку только у `Implicit flow` -> PKCE method ставим `S256` -> Valid redirect URIs ставим RegExp на адрес фронтенда (например: http://123.123.123.123:4200*) -> `Save`

4. В навбаре `Realm roles` -> `Create role` -> указываем `Role name` такой же как в массиве KC_ALLOWED_ROLES из `backend/.env.production` -> `Save`

5. В навбаре `Users` -> `Add user` -> Заполняем нужные поля -> `Create`

6. На странице созданного пользователя заходим в `Role mapping` -> `Assign role` -> `Realm roles` -> Выдаем роль созданную в пункте 4

7. На странице пользователя заходим в `Credentials` -> `Set password` -> Указываем пароль и выключаем пункт Temporary

Далее авторизация в сервисе будет по Username и паролю созданного пользователя.

### Установка credentials для QR

Для загрузки PDF в Google Drive воркер использует OAuth-клиент из файла `oauth_client.json`.

1. Создайте или выберите проект в [Google Cloud Console](https://console.cloud.google.com/).

2. В этом проекте включите `Google Drive API`: `Google Cloud Console -> APIs & Services -> Enabled APIs & services -> Enable APIs and Services -> Google Drive API`.

3. Настройте OAuth consent screen:
   `Google Cloud Console -> Google Auth platform -> Branding`.
   Укажите название приложения, `User support email` и контактный email(который мы создали на имя МИЭМ).

4. Выберите аудиторию в `Google Auth platform -> Audience`:
    выберите `External`, а в режиме тестирования добавьте нужный аккаунт(почту) в `Test users`.

5. Создайте OAuth client:
   `Google Cloud Console -> Google Auth platform -> Clients -> Create Client -> Desktop app`
   Важно: нужен именно тип `Desktop app`, потому что код авторизуется через локальный браузер (`InstalledAppFlow`).

6. Скачайте созданный JSON-файл и сохраните его в директории `worker/` под именем `oauth_client.json`.
   Если файл лежит в другом месте или называется иначе, обновите переменную `OAUTH_CLIENT_FILE` в `.env`.

7. Убедитесь, что в `.env` корректно заполнены:
   `SCOPES=https://www.googleapis.com/auth/drive`
   `OAUTH_CLIENT_FILE=oauth_client.json`
   `PARENT_FOLDER_ID=<id папки на Google Drive>`

8. Перейдите в папку `worker/` и запустите скрипт `token_generate.sh`:
   ```
   cd worker
   ./token_generate.sh
   ```
   Потребует ввести пароль от ВМ
   Скрипт выполнит авторизацию через `oauth_client.json`, создаст файл `token.json` в директории `worker/` и отправит на ВМ.

Примечания:

- Аккаунт, под которым вы проходите OAuth-авторизацию, должен иметь доступ к папке, указанной в `PARENT_FOLDER_ID`.(эта папка уже создана)

**Конец.**

> Инструкция разработчика лежит в `DEVDOCS.md`

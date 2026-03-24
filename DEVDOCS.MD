# Документация для разработчика
## backend

### Стек: 
- `FastAPI` + `dishka` (DI)
- `SQLAlchemy Async` + `Alembic`
- `PostgreSQL`
-  `MinIO`
-  `Celery/RabbitMQ`

### Формат ответов API:
```json
{
  "status": 200, // http статус код
  "message": "string",
  "data": [] // любой вид (объект, массив, null)
}
``` 

### HTTP API

Swagger документация будет доступна по пути `/docs`

**Авторизация**
- `POST /auth/kc` - принимает токен Keycloak и выдает локальный `access_token` + ставит `refresh_token` в httpOnly cookie
- `POST /auth/refresh` - обновляет `access_token` по cookie
- `POST /auth/logout` - удаляет refresh cookie
- `GET /user/me` - профиль текущего пользователя

**Документы**
- `POST /documents/upload` - принимает PDF/DOCX (DOCX конвертируется в PDF через LibreOffice). После загрузки файл сохраняется в MinIO bucket `documents`, запись создается в БД, затем отправляется Celery задача `ml.process_document`
- `GET /documents`, `GET /documents/search`, `GET /documents/{id}` - список/поиск/карточка документа
- `GET /documents/{id}/download` - скачать исходный файл (с QR-кодом на отчет, если обработан)
- `GET /documents/{id}/report` - скачать PDF-отчет по документу

**Отчеты**
- `GET /report?start=...&end=...` - выгрузка XLSX по обработанным документам пользователя

Поиск по авторам реализован в PostgreSQL через `tsvector + pg_trgm` (миграция `backend/alembic/versions/0002_authors_search_index.py`).

Локальный запуск backend:
```bash
cd backend
poetry install
poetry run alembic upgrade head
poetry run uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

## frontend

### Стек:
- `Angular 21` (standalone components, `OnPush`, `RxJS`)
- `TailwindCSS 4` + `SCSS`.

**Маршрутизация**
- `/auth` - вход через Keycloak
- `/auth/callback` - обработка токена из URL fragment и завершение логина
- `/` - главная (загрузка файлов)
- `/documents` - история документов
- `/documents/:docId` - карточка документа
- `/reports` - выгрузка сводного отчета

**Клиентский API-слой**
- `auth.interceptor` - добавляет `Bearer` токен, при `401` запускает refresh и повтор запроса
- `response-data.interceptor` - разворачивает backend-обертку и отдает фронту `data`
- Сервисы:
  - `AuthService` - логин/логаут/refresh и генерация ссылки авторизации Keycloak
  - `DocumentService` - загрузка файлов, поиск, пагинация, скачивание документа
  - `ReportsService` - скачивание отчета по документу и XLSX-отчета по периоду

Основные feature-модули:

- `home` - загрузка документов и отображение последних работ
- `documents/history` - фильтрация по статусу + поиск + пагинация
- `documents/document` - деталка, метрики, скачивание документа/отчета
- `reports` - выбор периода и выгрузка `report.xlsx`

Ключевые env-настройки в `frontend/src/environments/environment*.ts`: 
- `HOST` - адрес фронтенда (для редиректов с KC)
- `API_BASE_URL` - адрес API
- `KEYCLOAK_BASE_URL` - адрес KC
- `KEYCLOAK_REALM` - название Realm в KC
- `KEYCLOAK_CLIENT_ID` - Client ID из KC
- `KEYCLOAK_USES_AUTH_ENDPOINT` - используется ли /auth/ в эндпоинте для авторизации KC (в старых версиях)  

Локальный запуск frontend:
```bash
cd frontend
npm ci
npm start
```

## ollama

Инструкции по развертыванию и тестированию находятся в файле `ollama/README.MD`

Основные требования к модели: мультимодальность, >=4b

Протестированные варианты моделей:

- `google/gemma-3n-E4B-it` (в квантованной версии нет мультимодальности) - 8b модель, 24Гб vRAM, неплохие результаты

- `google/gemma-3n-E2B-it` - 4b модель, 16Гб vRAM, но слабовата

- `google/gemma-3-12b-it` (hf.co/unsloth/gemma-3-12b-it-GGUF:UD-Q4_K_XL) - 12b модель, в скобках максимальное квантование для 16Гб vRAM, но слабовата

## worker

### Алгоритм

(`worker/tasks/process_document.py`):

1. Загружается файл из Minio и через Dependency Injection (di) подгружаются модули

2. Файл загружается в doc_processor, конвертится в MD и первично разбивается по заголовкам регулярками 
DocumentProcessorService.get_structured_text(file_buffer)

3. Асинхронно запускаются запросы к модели:

    - Извлечение метаданных (ФИО, группа, тема) - мультимодальный запрос (task_parser.py)

    - Извлечение задания - мультимодальный запрос (task_parser.py)

    - Проверка подписей - поиск подписей с YOLO + мультимодальный запрос (pages_markup.py)

    - Классификация заголовков по фиксированной структуре разделов (headers_classifier.py)

4. Создается векторное хранилище (rag.py), классифицированные заголовки отдаются как метаданные. Потом проходит проверка структуры (check_structure) - если раздел не найден, он не проверяется.

5. Асинхронно запускаются запросы к модели:

    - Проверка приложения (vkr_application_check.py)

    - Проверка списка литературы (vkr_literature_check.py)

    - Проверка введения (vkr_intro_checker.py)

    - Проверка заключения (vkr_conclusion_checker.py)

    - Проверка аннотаций на русском и английском (vkr_annotation_checker.py)

    - Оценка соответствия работы пунктам задания, каждый пункт - отдельный запрос (vkr_analyzer.py)

6. Формируется итоговый отчет в формате json (vkr_report.py), в нем же рассчитывается оценка и статус (зачет/незачет). Потом по json формируется html страница, конвертится в pdf и грузится в Minio и на гугл диск (google_store.py). Ссылка на гугл диск конвертится в qr код и крепится на 1 страницу исходного документа (самой работы) в Minio.

7. Необходимые данные отправляются в БД

### Оценка

Оценка формируется следующим образом:

Независимо ставится оценка (0-10) по следующим пунктам:
- аннотация
- введение
- заключение
- список литературы
- приложение
- среднее по пунктам из задания

Итоговая оценка - среднее арифметическое

Если приложение не найдено, в оценке оно не учитывается. 

Если какой то раздел не найден, за него в любом случае ставится 0. Даже если он на самом деле есть в дипломе, но модель не смогла найти пункт, это значит, что оформление неправильное.

### Зачет

По каждому разделу ставится зачет/незачет (от 4 баллов). Если завалено больше 2 разделов - незачет, если 2 и меньше - зачет. 

### Изменение метрики

Логика расчета метрик находится в файле vkr_report.py функция VKRReport._calculate_summary(). 

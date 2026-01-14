dependencies installation:
```
poetry install
```

run in dev mode:
```
poetry run uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
```

run linting:
```
poetry run ruff check --fix
```
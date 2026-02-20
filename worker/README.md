```
poetry install
celery -A src.main worker --loglevel=info
```
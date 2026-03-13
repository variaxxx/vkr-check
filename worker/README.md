```
poetry install
celery -A src.main worker --loglevel=info
```

 Для проверки работы с qr-code нужно написать саньку чтобы он скинул креды
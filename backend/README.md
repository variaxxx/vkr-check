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

db upgrade:
```
poetry run alembic upgrade head
```

http://localhost:8155/realms/LOCAL/protocol/openid-connect/auth?response_type=id_token+token&client_id=spa-client&redirect_uri=http%3A%2F%2Flocalhost%3A4200%2Fauth%2Fcallback&scope=openid+profile&state=local&nonce=nonce123&code_challenge=9DNJSIcSs4mR1cyzPuZslCWRNq5y2rA_wPejSEIqV0c&code_challenge_method=S256

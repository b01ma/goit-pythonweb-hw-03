# goit-pythonweb-hw-03

Веб-додаток на `http.server` з маршрутизацією, обробкою форми та Jinja2-сторінкою для читання повідомлень.

## Функціональність

- `GET /` або `GET /index.html` — сторінка `index.html`
- `GET /message` або `GET /message.html` — сторінка `message.html`
- `POST /message` — прийом форми (`username`, `message`) і запис у `storage/data.json`
- `GET /read` — Jinja2-шаблон з усіма повідомленнями
- `GET /style.css`, `GET /logo.png` — статичні ресурси
- Невідомий маршрут — `error.html` з кодом `404`

## Локальний запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Після запуску: `http://localhost:3000`

## Docker (опціонально)

Збірка:

```bash
docker build -t goit-pythonweb-hw-03 .
```

Запуск з volume для збереження `data.json` поза контейнером:

```bash
mkdir -p storage
test -f storage/data.json || echo '{}' > storage/data.json
docker run --rm -p 3000:3000 -v "$(pwd)/storage:/app/storage" goit-pythonweb-hw-03
```

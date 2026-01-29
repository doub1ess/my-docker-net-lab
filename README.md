# Docker Network Lab: Nginx → 2 Flask apps → 2 Redis

Проект Docker Compose: поднимаются два одинаковых Flask‑приложения (`app_a` и `app_b`), у каждого свой Redis (`redis_a`, `redis_b`). Снаружи доступна только точка входа `reverse_proxy` (Nginx), который роутит запросы по путям `/a/*` и `/b/*`.

## Что внутри

Сервисы:

- `app_a` — Flask API (порт 8080 внутри контейнера), подключён к `redis_a`.
- `app_b` — Flask API (порт 8080 внутри контейнера), подключён к `redis_b`.
- `redis_a` — Redis для `app_a` (+ volume `redis_a_data`).
- `redis_b` — Redis для `app_b` (+ volume `redis_b_data`).
- `reverse_proxy` — Nginx, публикует наружу `localhost:8080` и проксирует:
  - `/a/…` → `app_a:8080`
  - `/b/…` → `app_b:8080`

Сети:

- `localnet_1`: `app_a` + `redis_a` + `reverse_proxy`
- `localnet_2`: `app_b` + `redis_b` + `reverse_proxy`


## Быстрый старт

Из корня проекта 
`docker compose up -d --build`
`docker compose ps`


## Как обращаться к сервисам

Весь внешний доступ идёт через Nginx:

- `http://localhost:8080/a/...` → приложение A
- `http://localhost:8080/b/...` → приложение B

прямой `http://localhost:8080/health` не предусмотрен (у Nginx настроены только `/a/` и `/b/`).

## API приложения

### 1) Проверка “жив ли сервис”

- A:
`curl -i http://localhost:8080/a/`

- B:
`curl -i http://localhost:8080/b/`

Ожидается ответ:
OK

### 2) Healthcheck

- A:
`curl -i http://localhost:8080/a/health`

- B:
`curl -i http://localhost:8080/b/health`


Ожидается JSON вида:
{
  "status": "ok",
  "details": {
    "redis": "ok"
  }
}

### 3) Кэш в Redis (POST/GET)

Записать значение (ключ = `test`, значение = тело запроса):

- В A:
`curl -i -X POST http://localhost:8080/a/cache/test -d "helloA"`


- В B:
`curl -i -X POST http://localhost:8080/b/cache/test -d "helloB"`


Прочитать значение:

- Из A:
`curl -i http://localhost:8080/a/cache/test`

- Из B:
`curl -i http://localhost:8080/b/cache/test`


## Как проверить изоляцию (идея двух сетей)

`app_a` и `app_b` находятся в разных Docker‑сетях и не обязаны видеть друг друга напрямую. Роль “моста” выполняет `reverse_proxy`, подключённый к обеим сетям.


## Полезные команды

Логи:
`docker compose logs -f app_a`
`docker compose logs -f app_b`
`docker compose logs -f reverse_proxy`

Зайти в контейнер:
`docker compose exec app_a sh`
`docker compose exec reverse_proxy sh`

Проверить, что Redis жив внутри контейнера:
`docker compose exec redis_a redis-cli ping`
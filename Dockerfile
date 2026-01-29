FROM python:3.12-alpine

LABEL maintainers="Stepan Shiian"

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN addgroup -S app && adduser -S doubless -G app && apk add --no-cache wget

ENV APP_TMP_DATA=/tmp
ENV REDIS_HOST=redis
ENV REDIS_PORT=6379

EXPOSE 8080

USER doubless:app

ENTRYPOINT ["python", "app/app.py"]
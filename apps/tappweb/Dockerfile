FROM python:3.11-alpine as builder

RUN --mount=type=cache,target=/var/cache/apk,sharing=shared \
    apk add build-base libffi-dev

COPY ./alembic.ini ./poetry.lock ./pyproject.toml /code/
COPY ./.env /code/.env
COPY ./src /code

WORKDIR /code
RUN --mount=type=cache,target=/root/.cache,sharing=shared \
    pip install --upgrade pip &&\
    pip install poetry &&\
    poetry export -f requirements.txt --output requirements.txt --without-hashes &&\
    pip install -r requirements.txt &&\
    pip uninstall -y poetry &&\
    rm -rf requirements.txt

FROM python:3.11-alpine as runner

ENV PYTHONUNBUFFERED 1
ENV PYTHONPATH "/code/src:${PYTHONPATH}"

COPY --from=builder /code /code
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages

RUN apk add --no-cache curl

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 CMD curl -f http://localhost:80/healthcheck || exit 1

RUN addgroup -S app && adduser -S app -G app
USER app

WORKDIR /code
ENTRYPOINT python main.py migrate && python main.py run 0.0.0.0 80

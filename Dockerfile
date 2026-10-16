FROM node:22-bookworm-slim AS web
WORKDIR /build/frontend
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim-bookworm AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY backend/requirements.lock.txt /app/backend/requirements.lock.txt
RUN pip install --no-cache-dir -r /app/backend/requirements.lock.txt \
    && useradd --create-home --uid 10001 tarka
COPY --chown=tarka:tarka backend/ /app/backend/
COPY --from=web --chown=tarka:tarka /build/frontend/dist/ /app/frontend/dist/
USER tarka
WORKDIR /app/backend
EXPOSE 8003
CMD ["sh", "-c", "python -m app.manage upgrade && python -m app.manage seed && exec uvicorn app.main:app --host 0.0.0.0 --port 8003"]

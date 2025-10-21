# Dockerfile multi-stage pour Recipe Recommender avec Poetry
FROM python:3.12-slim as builder

# Variables d'environnement pour Poetry
ENV POETRY_VERSION=1.7.1 \
    POETRY_HOME=/opt/poetry \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VIRTUALENVS_CREATE=true \
    POETRY_CACHE_DIR=/tmp/poetry_cache

# Installation des dépendances système
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Installation de Poetry
RUN curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /opt/poetry/bin/poetry /usr/local/bin/poetry

WORKDIR /app

# Copier UNIQUEMENT les fichiers de dépendances
COPY pyproject.toml poetry.lock ./

# IMPORTANT: Copier le code source AVANT l'installation
COPY src/ ./src/

# Installer les dépendances ET le package
RUN poetry install --no-dev && rm -rf $POETRY_CACHE_DIR

# ============================================
# STAGE 2: Runtime
# ============================================
FROM python:3.12-slim as runtime

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src:$PYTHONPATH" \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Installer curl pour healthcheck
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Créer utilisateur
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app /data && \
    chown -R appuser:appuser /app /data

WORKDIR /app

# Copier l'environnement virtuel
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copier TOUT le code source
COPY --chown=appuser:appuser src/ ./src/
COPY --chown=appuser:appuser data/ ./data/
COPY --chown=appuser:appuser pyproject.toml poetry.lock ./

USER appuser

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

EXPOSE 8501

ENTRYPOINT ["streamlit", "run"]
CMD ["src/recipe_recommender/app.py", "--server.port=8501", "--server.address=0.0.0.0"]

FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instala dependências de sistema necessárias para compilação e operações
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	gcc \
	libpq-dev \
	curl \
	&& rm -rf /var/lib/apt/lists/*

# Copia requirements e instala dependências Python
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia todo o projeto
COPY . .

# Criar usuário não-root por segurança
RUN useradd -m appuser && chown -R appuser /app
USER appuser

EXPOSE 8000

# Usa variável PORT fornecida pelo provedor (ex: Render). Fallback para 8000.
CMD ["sh", "-c", "uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --workers 2"]

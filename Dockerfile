# Imagem base oficial do Python slim
FROM python:3.12-slim

# Evitar criação de arquivos .pyc e garantir logs em tempo real
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar o restante da aplicação
COPY backend/ ./backend/
COPY data/ ./data/
COPY frontend/ ./frontend/
COPY run.py .

# Porta padrão de execução
EXPOSE 8000

# Comando de inicialização ouvindo em todas as interfaces de rede
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

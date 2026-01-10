# Dockerfile
FROM python:3.14-slim

# Establecer directorio de trabajo
WORKDIR /app

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código
COPY . .

# Comando por defecto
CMD ["python", "src/etl_job.py", "2025-08-20"]
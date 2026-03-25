# Imagen base
FROM python:3.12-slim

# Establecer directorio de trabajo 
WORKDIR /app

# Copiar los archivos principales del miner
COPY main_miner.py .
COPY requirements.txt .

# Instalar dependencias necesarias
RUN pip install --no-cache-dir -r requirements.txt

# Indicar que el contenedor necesita la variable de entorno que corresponde al token de GitHub
# para acceder a la API
ENV GITHUB_TOKEN=""

# Comando por defecto al ejecutar el contenedor (el token debe pasarse al ejecutar esto
# docker run -e GITHUB_TOKEN=<token_para_la_api> miner
CMD ["python", "main_miner.py"]
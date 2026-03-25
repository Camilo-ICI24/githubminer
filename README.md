# GitHubMiner


## Descripción

Este proyecto extrae información de repositorios populares en GitHub (Python y Java), generando un ranking de las palabras más utilizadas en la definición de funciones y métodos. Los resultados se visualizan mediante una interfaz web con gráficos interactivos.

Se compone de dos partes fundamentales:

1. **Miner (`main_miner.py`)**: Accede a la API de GitHub utilizando el token personal del usuario, descargando repositorios, analizando los archivos `.py` y `.java` relacionados y registrando los resultados en archivos JSON con los rankings.
2. **Visualizador (`visualizador/`)**: Interfaz web que muestra gráficos de barras de las palabras más populares en Python y Java usando Chart.js y Nginx.

---

## Requisitos

- Python >= 3.8  
- Librerías: `requests`, `zipfile`, `io`, `collections`, `os`, `json`, `re`, `time`  
- Docker y Docker Compose para ejecución en contenedores
- Token personal de GitHub (`GITHUB_TOKEN`)

---

## Instalación y Uso

### 1. Configuración del Token

Crea un archivo `.env` en la raíz del proyecto con tu token de GitHub:

```env
GITHUB_TOKEN=token_personal
```

Es importante que no expongas el token personal de manera pública.

### 2. Ejecución sin Docker

Instala las dependencias necesarias para la ejecución del miner.

```bash
pip install -r miner/requirements.txt
```

Ejecuta el archivo principal del miner.

```bash
python miner/main_miner.py
```

### 3. Ejecución con Docker

#### Dockerfile Miner
Se ubica en la ruta `miner/Dockerfile`. Con este archivo, se crea la imagen del miner, mediante el comando

```bash
docker build -t cybersec-miner ./miner
```

#### Dockerfile Visualizer
Se ubica en la ruta `visualizador/Dockerfile`. Con este archivo, se sirve la interfaz gráfica del ranking mediante Nginx, utilizando

```bash
docker build -t cybersec-ui ./visualizador
```

#### Docker Compose
Es posible construir ambas imágenes, tanto del miner como de la interfaz gráfica, a la vez, con el uso del archivo `docker-compose.yml`. Se levanta con el comando

```bash
docker-compose up --build
```

Al ejecutarse este comando, el visualizador quedará disponible en `http://localhost:8080/`

## Documentación del Código
- `main_miner.py`: Comentarios detallados sobre funcionamiento, parámetros y retornos de cada método desarrollado.
- `script.js`: Documentación acerca del funcionamiento de la lógica de creación y actualización de los gráficos.
- `index.html`: Interfaz sencilla con dos gráficos y control de cantidad de palabras más utilizadas.
"""
main_miner.py

Este código se encarga de realizar el proceso de minería de datos, accediendo a diferentes repositorios
almacenados en GitHub mediante llamadas a la API para rescatar aquellos que posean mayor valoración, 
cuyo lenguaje de programación sea Python y Java, generando un ranking de las palabras más utilizadas
para definir funciones o métodos en estos lenguajes. La información fundamental de cada repositorio es
almacenada en un archivo JSON que es accedido más tarde por el visualizador gráfico, siendo desplegado
por una interfaz web.

Requisitos:
-Python >= 3.8
-Librerías: io, collections, requests, os, json, re, zipfile, time.

Uso:
-Establecer una variable de entorno GITHUB_TOKEN con el token personal de GitHub
-Ejecutar el comando python main_miner.py
"""

from io import BytesIO
from collections import Counter

import requests
import os
import json
import re
import zipfile
import time

# Token de acceso para realizar las llamadas a la API de GitHub
token_acceso = os.getenv("GITHUB_TOKEN")

def descargar_info_repo(dueño, repo, headers):
    """
    Obtiene la información necesaria de cada repositorio.

    Parámetros:
    -dueño: usuario de GitHub dueño del repositorio
    -repo: nombre del repositorio
    -headers: cabeceras HTTP para autenticación y acceso a la API

    Retorna:
    -Diccionario con la información extraída del repositorio, como nombre, valoración con estrellas, 
    enlace HTML, lenguaje de programación y nombre del usuario dueño.
    """
    url_desc = f"https://api.github.com/repos/{dueño}/{repo}"
    response = requests.get(url_desc, headers)

    if response.status_code != 200:
        print(f'Se ha producido un error al descargar la información: {response.status_code, response.text}')
        return None

    repo_guardar = response.json()

    if 'name' not in repo_guardar:
        print(f"Se ha producido un error al obtener la información de este repositorio: {repo_guardar.get('message')}")
        return None

    html_url = repo_guardar.get('html_url')
    name = repo_guardar.get('name')
    stars = repo_guardar.get('stargazers_count')
    language = repo_guardar.get('language')

    if not all([html_url, name]):
        print(f'El repositorio {repo} no tiene datos suficientes. Omitiendo...')
        return None

    save = {
        "name": repo_guardar['name'],
        "stars": repo_guardar['stargazers_count'],
        "html_url": repo_guardar.get('html_url', None),
        "language": repo_guardar['language'],
        "owner": repo_guardar['owner']['login']
    }

    print(f"Repositorio {repo} almacenado con éxito")
    return save

def analizar_zip_repo(dueño, repo, headers):
    """
    Descarga el repositorio en formato ZIP, analiza los archivos Python y Java y extrae sus funciones
    y métodos.

    Parámetros:
    -dueño: usuario de GitHub dueño del repositorio
    -repo: nombre del repositorio
    -headers: cabeceras HTTP para autenticación y acceso a la API

    Retorna:
    -resultado_py: Lista que contiene todas las palabras de las funciones en Python
    -resultado_java: Lista que contiene todas las palabras de las funciones en Java
    """
    url_zip = f"https://api.github.com/repos/{dueño}/{repo}/zipball"

    resp = requests.get(url_zip, headers)

    if resp.status_code == 403:
        print(f'Se ha alcanzado el límite de consultas al intentar descargar {repo}')
        return None, None

    if resp.status_code != 200:
        print(f'Se ha producido un error al descargar el ZIP del repo {repo}: {resp.text}')
        return [], []
    
    try:
        archivo_zip = zipfile.ZipFile(BytesIO(resp.content))
    except zipfile.BadZipFile as corrupto:
        print(f'El ZIP que se intenta acceder presenta problemas: {corrupto}')
        return [], []

    resultado_py = []
    resultado_java = []

    for archivo in archivo_zip.namelist():
        try:
            if archivo.endswith(".py"):
                arch = archivo_zip.open(archivo).read().decode(errors='ignore').splitlines()
                resultado_py += extraer_palabras_python(arch)
            

            elif archivo.endswith(".java"):
                arch = archivo_zip.open(archivo).read().decode(errors='ignore').splitlines()
                resultado_java += extraer_palabras_java(arch)
        except UnicodeDecodeError as decodif:
            print(f'No fue posible leer este archivo: {decodif}')
            continue

    return resultado_py, resultado_java

def extraer_palabras_python(texto):
    """
    Analiza y extrae las palabras de las funciones de un archivo Python.

    Parámetros:
    -texto: Archivo Python incluído en el repositorio.

    Retorna:
    -palabras: Lista de palabras extraídas de todas las funciones.
    """
    palabras = []

    for linea in texto:
        linea_iterada = linea.lstrip()
        if linea_iterada.startswith("def "):
            palabras_funcion = linea_iterada.split("(")[0][4:]
            palabras.extend([pal for pal in palabras_funcion.split("_") if pal])

    return palabras

def extraer_palabras_java(texto):
    """
    Analiza y extrae las palabras de las funciones de un archivo Java.

    Parámetros:
    -texto: Archivo Java incluído en el repositorio.

    Retorna:
    -palabras: Lista de palabras extraídas de todas las funciones.
    """
    palabras = []

    for linea in texto:
        linea_iterada = linea.lstrip()

        if "(" in linea_iterada and ")" in linea_iterada and "{" in linea_iterada:
            parentesis = linea_iterada.find('(')
            espacio = linea_iterada.rfind(" ", 0, parentesis)
            if espacio == -1:
                continue

            metodo = linea_iterada[espacio+1 : parentesis]

            pal_metodo = re.findall(r'[A-Z][^A-Z]*', metodo)
            pal_metodo = [p.lower() for p in pal_metodo]

            palabras.extend(pal_metodo)

    return palabras

def cooldown_check(headers, recurso='core'):
    """
    Verifica si se han consumido todas las llamadas a la API de GitHub.

    Parámetros:
    -headers: cabecera HTTP para autenticación y acceso a la API.
    -recurso: tipo de consultas que pueden realizarse desde la API.

    Retorna:
    -false: Booleano que indica que existen consultas posibles, permitiendo que el análisis de archivos
    continúe.
    """
    url_consultas = "https://api.github.com/rate_limit"
    resp = requests.get(url_consultas, headers=headers)
    if resp.status_code != 200:
        return False
    
    datos_consultas = resp.json()
    consultas_restantes = datos_consultas['resources'].get(recurso, {}).get('remaining', 0)

    if consultas_restantes == 0:
        print(f'Se han acabado las queries para el recurso {recurso}')
        return True
    
    return False

def miner(leng, estrellas_minimas=90000, max_pages=1):
    """
    Busca repositorios en GitHub desde la API según su valoración mínima y lenguaje de programación, 
    recuperando su información básica.

    Parámetros:
    -leng: lenguaje de programación de interés.
    -estrellas_minimas: valoración mínima que deben tener los repositorios a analizar.
    -max_pages: cantidad de páginas que se accederán para obtener los datos.

    Retorna:
    -repos_totales: Lista que contiene toda la información de cada repositorio extraído.
    """
    headers = {
    "Authorization": f"Bearer {token_acceso}",
    "Accept": "application/vnd.github.v3+json"
    }

    query = f"language:{leng} stars:>{estrellas_minimas}"

    repos_totales = []
    page = 1

    while page <= max_pages:
        api_url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&page={page}"

        respuesta = requests.get(api_url, headers=headers)

        if respuesta.status_code == 403:
            print('Se ha alcanzado el límite de consultas a la API')
            break

        if respuesta.status_code != 200:
            print(f"Se ha producido un error al obtener los repositorios: {respuesta.status_code}")
            break

        datos = respuesta.json()
        if not datos.get('items'):
            break

        for repo in datos['items']:
            info_repo = descargar_info_repo(dueño=repo['owner']['login'], repo=repo['name'], headers=headers)
            if info_repo:
                repos_totales.append(info_repo)
            time.sleep(1)

        page += 1

    return repos_totales

def ranking(elemento):
    """
    Genera un top ordenado con las 10 palabras más frecuentes en cada lenguaje.

    Parámetros:
    -elemento: lista de palabras que se ordenarán según frecuencia.

    Retorna:
    -lista ordenada de menor a mayor frecuencia de cada palabra.
    """
    if not elemento:
        return []
    
    rank = Counter(elemento)
    return sorted(rank.items(), key=lambda x: x[1], reverse=True)[:10]

def main():

    headers = {
        "Authorization": f"Bearer {token_acceso}",
        "Accept": "application/vnd.github.v3+json"
        }
    
    lenguajes = ["Python", "Java"]
    info = []

    for l in lenguajes:
        info.extend(miner(l))

    print(f'Se han almacenado {len(info)} repositorios exitosamente')

    palabras_py, palabras_java = [], []

    for repository in info:
        if cooldown_check(headers, 'core'):
            print('Queries terminadas. Deteniendo análisis....')
            break

        print(f"Analizando repositorio {repository['name']}.....")
        resultado_py, resultado_java = analizar_zip_repo(repository['owner'], repository['name'], headers=headers)

        if resultado_py is None or resultado_java is None:
            print('Deteniendo análisis: Límite alcanzado.....')
            break

        palabras_py += resultado_py
        palabras_java += resultado_java
        print(f"Repositorio {repository['name']} analizado con éxito")

    ranking_py = ranking(palabras_py)
    ranking_java = ranking(palabras_java)

    os.makedirs("visualizador", exist_ok=True)

    with open("info_repos.json", 'w') as inf:
        print("Creando archivo 'info_repos.json'. Almacenando datos....")
        json.dump(info, inf, indent=4)

    with open("visualizador/mas_usados_py.json", 'w') as result_py:
        print("Creando archivo 'mas_usados_py.json'. Almacenando datos....")
        json.dump(ranking_py, result_py, indent=4)

    with open('visualizador/mas_usados_java.json', 'w') as result_java:
        print("Creando archivo 'mas_usados_java.json'. Almacenando datos....")
        json.dump(ranking_java, result_java, indent=4)

    print('Archivos JSON y rankings realizados con éxito')

    return {
        "info_repos": info,
        "ranking_py": ranking_py,
        "ranking_java": ranking_java
    }

if __name__ == "__main__":
    main()
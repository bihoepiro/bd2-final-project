
## Introducción

### Objetivo del proyecto
Este proyecto está enfocado en entender y aplicar los algoritmos de búsqueda y recuperación de información basada en el contenido.

### Descripción del dataset
Se trabajó con una base de datos obtenida de Kaggle que contiene información sobre más de 18,000 canciones de Spotify, incluyendo artista, álbum, funciones de audio (por ejemplo, el volumen), letra, idioma de la letra, géneros y subgéneros.
### Importancia de aplicar indexación

## Backend

### Índice Invertido

#### Construcción del índice en memoria secundaria
Para el procesamiento de bloques, creamos la clase `Bloque`, que posee como atributos `limite` (máximo de objetos), `entradas` (elementos) y `next_block` (encargado del encadenamiento de bloques).

```cpp
class Bloque:
    def __init__(self, limite):
        self.limite = limite
        self.entradas = {}
        self.next_block = None

```
- Además la clase posee funciones de agregar_entrada, la cual calcula si la cantidad de entradas del bloque es menor que el límite, en ese caso se agrega al bloque.
```cpp
    def agregar_entrada(self, palabra, docs):
        if len(self.entradas) < self.limite:
            self.entradas[palabra] = docs
            return True
        else:
            return False

    def guardar(self, filename):
        data = {
            'entradas': self.entradas,
            'next_block': self.next_block
        }
        with open(filename, 'w') as file:
            json.dump(data, file)
```          
### Ejecución óptima de consultas aplicando similitud de coseno: 
En esta parte del código decidimos utilizar una búsqueda binaria para poder buscar de manera efectiva los términos en los bloques de memoria. Dado a que estan ordenados, accedemos a los bloques de memoria a buscar los términos y retornamos en qué bloque se encuentra. A partir de este, extraemos sus documento y su frecuencia del término
    
```cpp
    def binary_search(bloque, term):
    words = sorted(bloque.keys())
    low = 0
    high = len(words) - 1

    while low <= high:
        mid = (low + high) // 2
        mid_word = words[mid]

        if mid_word == term:
            return bloque[mid_word]

        elif mid_word < term:
            low = mid + 1

        else:
            high = mid - 1
    return None
  ```

 ### Procesamiento de la consulta :
 Para procesar la consulta con similitud de coseno seguimos los siguientes pasos:
 1. Obtenemos los términos de cada query
 2. Buscamos los términos en cada bloque por medio de binary search
 3. Computamos el peso (tfidf) del término en el documento
 4. Añadimos el documento dentro de los scores 
```cpp
def procesar_consulta(query, k):
    query_terms = recibir_query(query)
    doc_scores = {}

    for term in query_terms:
        for bloque in bloques_cargados:
            result = binary_search(bloque.entradas, term)
            
            if result:
                for doc_id, tf_value in result.items():
                    if doc_id == "df":
                        continue
                    df = result.get("df", 1)
                    tfidf = compute_tfidf(tf_value, df, cant_docs)
                    if doc_id in doc_scores:
                        doc_scores[doc_id] += tfidf
                    else:
                        doc_scores[doc_id] = tfidf

    top_k_documentos = sorted(doc_scores.items(), key=lambda item: item[1], reverse=True)[:k]
    return top_k_documentos
```
### Conexión mediante API:

La API está construida usando Flask, un micro-framework de Python, y se beneficia de Flask-CORS para manejar peticiones de diferentes dominios. Los datos de las canciones están almacenados en un archivo CSV y en una base de datos PostgreSQL.

#### Endpoints

##### `/search`

Este es el único endpoint de la API y permite realizar búsquedas de canciones. Las peticiones deben ser de tipo POST y el cuerpo de la petición debe ser un JSON con los siguientes campos:

- `query`: La consulta de búsqueda.
- `topK`: (Opcional) El número de resultados a devolver. Por defecto es 10.
- `indexingMethod`: El método de indexación a utilizar, puede ser `PostgreSQL` o `Índice local`.

##### Ejemplo de petición

```json
{
  "query": "amor",
  "topK": 5,
  "indexingMethod": "PostgreSQL"
}
```

#### Estructura del Código

El código se divide en varias partes:

##### Inicialización de Flask

Se inicializa la aplicación Flask y se configura CORS para permitir peticiones desde diferentes dominios.

```python
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
```

##### Carga y Preprocesamiento de Datos

Se lee el archivo CSV que contiene las letras de las canciones y se eliminan las columnas innecesarias. Luego, se preprocesan las canciones y se crean bloques de datos para el índice local.

```python
import pandas as pd
from indexing import prepro_cancion, crear_bloques, guardar_bloques, cargar_bloques

Dataf = pd.read_csv("only_letras.csv")
Dataf = Dataf.drop(columns=['Unnamed: 10', 'Unnamed: 11', 'Unnamed: 12', 'Unnamed: 13',
                            'Unnamed: 14', 'Unnamed: 15', 'Unnamed: 16', 'Unnamed: 17',
                            'Unnamed: 18', 'Unnamed: 19'])

fuerte_dic = prepro_cancion(Dataf)
diccionario_ordenado = dict(sorted(fuerte_dic.items()))
limite_bloque = 50
bloques = crear_bloques(diccionario_ordenado, limite_bloque)
guardar_bloques(bloques)

bloques_cargados = cargar_bloques(len(bloques))
cant_docs = Dataf.shape[0]
```

##### Conexión a PostgreSQL

Se define una función para conectarse a la base de datos PostgreSQL utilizando las variables de entorno para los parámetros de conexión.

```python
import psycopg2
from os import environ

def connect_to_postgres():
    return psycopg2.connect(
        host=environ.get('DB_HOST', 'localhost'),
        database=environ.get('DB_NAME', 'proyecto'),
        port=environ.get('DB_PORT', '5432'),
        user=environ.get('DB_USER', 'postgres'),
        password=environ.get('DB_PASSWORD', '210904')
    )
```

##### Endpoint de Búsqueda

El endpoint `/search` maneja las peticiones POST y ejecuta la búsqueda según el método de indexación especificado.

```python
@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('query')
    top_k = int(data.get('topK', 10))
    indexing_method = data.get('indexingMethod')

    if not query or not indexing_method:
        return jsonify(error="Invalid input"), 400

    if indexing_method == 'PostgreSQL':
        try:
            conn = connect_to_postgres()
            cursor = conn.cursor()

            postgreSQL_select = """
                SELECT track_name, lyrics, duration_ms, ts_rank(indexed, query) AS rank
                FROM spotify_songs, plainto_tsquery('multilingual', %s) query
                ORDER BY rank DESC
                LIMIT %s;
            """

            cursor.execute(postgreSQL_select, (query, top_k))
            results = [{'track_name': row[0], 'lyrics': row[1], 'duration_ms': row[2], 'rank': row[3]} for row in cursor.fetchall()]

            cursor.close()
            conn.close()

            return jsonify(results=results)
        except Exception as e:
            return jsonify(error=str(e)), 500
    elif indexing_method == 'Índice local':
        try:
            results = procesar_consulta(query, top_k, bloques_cargados, cant_docs)
            result_list = []
            for score, doc_id in results:
                result_data = Dataf.loc[doc_id, ['track_name', 'lyrics', 'duration_ms']].to_dict()
                result_data['score'] = score
                result_list.append(result_data)
            return jsonify(results=result_list)
        except Exception as e:
            return jsonify(error=str(e)), 500
    else:
        return jsonify(error="Invalid indexing method"), 400
```

##### Ejecución de la Aplicación

Finalmente, se ejecuta la aplicación en modo de depuración.

```python
if __name__ == '__main__':
    app.run(debug=True)
```

Esta API proporciona una funcionalidad robusta para buscar canciones a partir de sus letras, utilizando tanto una base de datos PostgreSQL con índices GIN como un índice local basado en bloques. La estructura modular y el uso de variables de entorno permiten una configuración flexible y segura.

### Frontend:
Para realizar el diseño del frontend se utilizó **React** como framework.
### Diseño de la GUI
Esta aplicación permite buscar canciones rápidamente utilizando diferentes métodos de indexación. Los usuarios pueden ingresar una consulta,
especificar cuántos resultados quieren ver y elegir el método de indexación para optimizar la búsqueda.
1. **Campo de Búsqueda ("Enter your query")**:
   - Aquí puedes escribir la palabra o frase que deseas buscar.

2. **Número de Resultados ("Top K")**:
   - Especifica cuántos resultados quieres que se muestren. Por defecto está en 10.

3. **Método de Indexación ("Indexing Method")**:
   - Un menú desplegable que te permite elegir el método de indexación para la búsqueda. Las opciones pueden incluir PostgreSQL, MongoDB, etc.

4. **Botón de Búsqueda ("Search")**:
   - Haz clic aquí para iniciar la búsqueda con los parámetros especificados.

5. **Tiempo de Consulta ("Query Time")**:
   - Muestra el tiempo que tomó realizar la búsqueda en milisegundos.
6. **Resultados de la Búsqueda**:
   - La lista de resultados que coinciden con la consulta. Cada resultado muestra:
     - El título de la canción.
     - La duración de la canción.
     - Un puntaje de relevancia (si aplica).
#### Instrucciones de Uso

1. **Realizar una Búsqueda**:
   - Escribe tu consulta en el campo de búsqueda. Por ejemplo, "hhshshshshs".
   - Especifica el número de resultados que deseas ver en el campo "Top K". Por ejemplo, 10.
   - Selecciona el método de indexación desde el menú desplegable.
   - Haz clic en el botón "Search".

3. **Cambiar el Método de Indexación**:
   - Abre el menú desplegable junto a "Indexing Method".
   - Selecciona el método que deseas utilizar.
   - Realiza la búsqueda nuevamente para ver cómo cambia el tiempo de consulta y los resultados.

- #### Screenshots de la GUI
  •⁠  ⁠Esta imagen es antes de escribir alguna consulta.
   <img src="WhatsApp Image 2024-06-18 at 21.06.09.jpeg" width="800px">
•  Ejecutando un consulta "boy" y usando el método de indexación de postgress. Al lado izquierdo nos retorna la posición 1 del top K.
   <img src="WhatsApp Image 2024-06-18 at 21.06.36.jpeg" width="800px">
• Si deslizamos hacia abajo podemos encontrar las letras de las canciones.
   <img src="WhatsApp Image 2024-06-18 at 21.06.51.jpeg" width="800px">
#### Instrucciones para utilizar el Frontend

##### Requisitos Previos

Asegúrate de tener Node.js y npm (Node Package Manager) instalados en tu sistema.

#### Pasos para Configurar y Ejecutar la Aplicación
 - Abre tu terminal y clona el repositorio de la aplicación.
 - Luego ejecute los siguentes comandos
   ```
   cd frontend
   npm install
   npm run dev
   ```
### Experimentación:
Se presenta una comparativa en tiempo de ejecución de cada implementación en función del número de registros. (Para todos los casos la cantidad de elementos recuperados en el top k se toma como 10)
|                | MyIndex        | PostgreSQL           |
|----------------|----------------|----------------------|
| N = 1000       |                |    0.129 ms          |
| N = 2000       |                |    0.440 ms          |
| N = 4000       |                |    0.623 ms          |
| N = 8000       |                |    1.502 ms          |
| N = 16000      |                |    2.228 ms          |
| N = 32000      |                |    3.865 ms          |
| N = 64000      |                |    4.125 ms          |
| N = 128000     |                |    4.842 ms          |











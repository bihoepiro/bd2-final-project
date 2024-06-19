## Introducción
-  Objetivo del proyecto:
   Este proyecto está enfocado a entender y aplicar los algoritmos de
  búsqueda y recuperación de la información basado en el contenido.
-  Descripción del dataset:
  Se trabajo con la base de datos obtenido por Kaggle. Lo cual contiene varios tipos de información sobre más de 18000 canciones de Spotify, incluido el artista, el álbum,
las funciones de audio (por ejemplo, el volumen), la letra, el idioma de la letra, los géneros y los subgéneros.
-  Importancia de aplicar indexación.
### Backend: 
1. Indice Invertido:
2. Indice Multidimensional:
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











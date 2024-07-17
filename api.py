from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
from os import environ
import FinalSpimi  # Importar el archivo de indexación
import requests

app = Flask(__name__)
CORS(app)

# Cargar los bloques y otras variables globales
bloques_cargados, cant_docs = FinalSpimi.cargar_bloques_y_docs()

# Función para conectar con PostgreSQL
def connect_to_postgres():
    return psycopg2.connect(
        host=environ.get('DB_HOST', 'localhost'),
        database=environ.get('DB_NAME', 'proyecto'),
        port=environ.get('DB_PORT', '5432'),
        user=environ.get('DB_USER', 'postgres'),
        password=environ.get('DB_PASSWORD', '210904')
    )

# Función para obtener la URL de la imagen del álbum desde iTunes
def get_itunes_album_cover_url(album_name):
    search_url = f"https://itunes.apple.com/search?term={album_name}&entity=album"
    response = requests.get(search_url)
    data = response.json()
    if data['resultCount'] > 0:
        return data['results'][0]['artworkUrl100']
    else:
        return None

# Endpoint para la búsqueda
@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data.get('query')
    top_k = int(data.get('topK', 10))  # Default de 10 si no se especifica
    indexing_method = data.get('indexingMethod')

    if not query or not indexing_method:
        return jsonify(error="Invalid input"), 400

    if indexing_method == 'PostgreSQL':
        try:
            # Conectar a PostgreSQL y realizar búsqueda con índice GIN
            conn = connect_to_postgres()
            cursor = conn.cursor()

            postgreSQL_select = """
                SELECT track_name, track_album_name, lyrics, duration_ms, ts_rank(indexed, query) AS rank
                FROM spotify_songs, plainto_tsquery('multilingual', %s) query
                ORDER BY rank DESC
                LIMIT %s;
            """

            cursor.execute(postgreSQL_select, (query, top_k))
            results = []
            for row in cursor.fetchall():
                image_url = get_itunes_album_cover_url(row[1])
                results.append({
                    'track_name': row[0],
                    'track_album_name': row[1],
                    'lyrics': row[2],
                    'duration_ms': row[3],
                    'rank': row[4],
                    'album_cover': image_url
                })

            cursor.close()
            conn.close()

            return jsonify(results=results)
        except Exception as e:
            return jsonify(error=str(e)), 500
    elif indexing_method == 'Custom Implementation':
        try:
            # Procesar la consulta utilizando el índice local
            top_k_documentos = FinalSpimi.procesar_consulta(query, top_k, bloques_cargados, cant_docs)
            for doc in top_k_documentos:
                album_name = doc['track_album_name']
                doc['album_cover'] = get_itunes_album_cover_url(album_name)
            return jsonify(results=top_k_documentos)
        except Exception as e:
            return jsonify(error=str(e)), 500
    else:
        return jsonify(error="Invalid indexing method"), 400

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Cambiar el puerto a 5001

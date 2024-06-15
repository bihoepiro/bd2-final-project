from flask import Flask, request, jsonify
import psycopg2
from os import environ, path
from dotenv import load_dotenv

app = Flask(__name__)

# Cargar variables de entorno desde .env
basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.env'))

# Función para conectar con PostgreSQL
def connect_to_postgres():
    return psycopg2.connect(
        host=environ.get('POSTGRES_HOST'),
        database=environ.get('POSTGRES_DATABASE_NAME'),
        port='5432',
        user='postgres',
        password=environ.get('POSTGRES_CONN_PASSWORD')
    )

# Endpoint para la búsqueda
@app.route('/search', methods=['POST'])
def search():
    data = request.get_json()
    query = data['query']
    top_k = int(data['topK'])
    indexing_method = data['indexingMethod']

    if indexing_method == 'PostgreSQL':
        # Conectar a PostgreSQL y realizar búsqueda con índice GIN
        conn = connect_to_postgres()
        cursor = conn.cursor()

        cursor.execute("SELECT title, lyrics, duration, image FROM songs WHERE to_tsvector('english', title || ' ' || lyrics) @@ plainto_tsquery(%s) LIMIT %s;", (query, top_k))
        results = [{'title': row[0], 'lyrics': row[1], 'duration': row[2], 'image': row[3]} for row in cursor.fetchall()]

        cursor.close()
        conn.close()

        return jsonify(results=results)

    else:
        # En caso de que el método de indexación no sea reconocido
        return jsonify(error="Unsupported indexing method"), 400


if __name__ == '__main__':
    app.run(debug=True)

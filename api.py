import psycopg2
from flask import Flask, request, jsonify
from flask_cors import CORS
from os import environ
import FinalSpimi

app = Flask(__name__)
CORS(app)

# Cargar el índice una vez al inicio
df, merged_index, idf = FinalSpimi.index_and_search('C://Users//bepiquien//utec//bd2//spotify_songs.csv')

# Función para conectar con PostgreSQL
def connect_to_postgres():
    return psycopg2.connect(
        host=environ.get('DB_HOST', 'localhost'),
        database=environ.get('DB_NAME', 'proyecto'),
        port=environ.get('DB_PORT', '5432'),
        user=environ.get('DB_USER', 'postgres'),
        password=environ.get('DB_PASSWORD', '210904')
    )

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
            results = FinalSpimi.query_processing(query, top_k)
            result_list = []
            for score, doc_id in results:
                result_data = df.loc[doc_id, ['track_name', 'lyrics', 'duration_ms']].to_dict()
                result_data['score'] = score
                result_list.append(result_data)
            return jsonify(results=result_list)
        except Exception as e:
            return jsonify(error=str(e)), 500
    else:
        return jsonify(error="Invalid indexing method"), 400

if __name__ == '__main__':
    app.run(debug=True)

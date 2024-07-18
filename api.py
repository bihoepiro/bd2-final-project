from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import psycopg2
from os import environ, path, makedirs
import os
import FinalSpimi  # Importar el archivo de indexación
import requests
import yt_dlp as youtube_dl
import librosa
import soundfile as sf
import ffmpeg
import pandas as pd

app = Flask(__name__)
CORS(app)

# Configurar rutas de salida para descargas
ruta_descarga_mp3 = 'canciones/mp3'
ruta_descarga_wav = 'canciones/wav'
makedirs(ruta_descarga_mp3, exist_ok=True)
makedirs(ruta_descarga_wav, exist_ok=True)
df_songs = pd.read_csv('spotify_songs.csv')
def descargar_y_convertir(track_name, track_artist, track_id):
    query = f"{track_name} {track_artist} lyrics"
    print(f"Buscando y descargando: {query}")

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'extractaudio': True,
        'outtmpl': os.path.join(ruta_descarga_mp3, f"{track_id}.webm"),
        'quiet': False,
        'no_warnings': True
    }

    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"ytsearch:{query}"])
            print(f"Descarga completa: {track_id}.webm")
    except Exception as e:
        print(f"Error al buscar o descargar el video en YouTube: {e}")
        raise

    webm_file = os.path.join(ruta_descarga_mp3, f"{track_id}.webm")
    mp3_file = os.path.join(ruta_descarga_mp3, f"{track_id}.mp3")

    if not path.exists(webm_file):
        print(f"Error: El archivo {webm_file} no existe después de la descarga.")
        raise FileNotFoundError(f"El archivo {webm_file} no se encontró después de la descarga.")

    # Convertir .webm a .mp3 usando ffmpeg-python
    try:
        ffmpeg.input(webm_file).output(mp3_file).run()
        print(f"Conversión completa: {track_id}.mp3")
    except Exception as e:
        print(f"Error al convertir el archivo {webm_file} a .mp3: {e}")
        raise

    return mp3_file

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
                SELECT track_id, track_name, track_album_name, lyrics, duration_ms, ts_rank(indexed, query) AS rank
                FROM spotify_songs, plainto_tsquery('multilingual', %s) query
                ORDER BY rank DESC
                LIMIT %s;
            """

            cursor.execute(postgreSQL_select, (query, top_k))
            results = []
            for row in cursor.fetchall():
                image_url = get_itunes_album_cover_url(row[2])
                results.append({
                    'track_id': row[0],
                    'track_name': row[1],
                    'track_album_name': row[2],
                    'lyrics': row[3],
                    'duration_ms': row[4],
                    'rank': row[5],
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

@app.route('/audio', methods=['GET'])
def obtener_audio():
    track_id = request.args.get('track_id')
    indexing_method = request.args.get('indexingMethod', 'PostgreSQL')

    if not track_id:
        return jsonify(error="track_id is required"), 400

    if indexing_method == 'PostgreSQL':
        conn = connect_to_postgres()
        cursor = conn.cursor()
        cursor.execute("SELECT track_name, track_artist FROM spotify_songs WHERE track_id = %s", (track_id,))
        row = cursor.fetchone()
        cursor.close()
        conn.close()
    elif indexing_method == 'Custom Implementation':
        row = None
        top_k_documentos = FinalSpimi.procesar_consulta(track_id, 1, bloques_cargados, cant_docs)
        if top_k_documentos:
            row = (top_k_documentos[0]['track_name'], top_k_documentos[0]['track_artist'])
    else:
        return jsonify(error="Invalid indexing method"), 400

    if not row:
        return jsonify(error="Track not found"), 404

    track_name, track_artist = row
    print(f"Obtenido track_name: {track_name}, track_artist: {track_artist}")
    mp3_file = path.join(ruta_descarga_mp3, f"{track_id}.mp3")

    if not path.exists(mp3_file):
        print(f"Archivo MP3 no encontrado. Descargando: {track_name} - {track_artist}")
        try:
            descargar_y_convertir(track_name, track_artist, track_id)
        except Exception as e:
            print(f"Error al descargar y convertir: {e}")
            return jsonify(error="Failed to download the track"), 500

    if not path.exists(mp3_file):
        return jsonify(error="Failed to download the track"), 500

    return send_file(mp3_file, mimetype='audio/mp3')
@app.route('/track_info', methods=['GET'])
def track_info():
    track_id = request.args.get('track_id')
    if not track_id:
        return jsonify(error="track_id is required"), 400

    try:
        track_info = df_songs[df_songs['track_id'] == track_id].iloc[0].to_dict()
        return jsonify(track_info)
    except IndexError:
        return jsonify(error="Track not found"), 404
    except Exception as e:
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True, port=5001)  # Cambiar el puerto a 5001

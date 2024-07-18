from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.neighbors import KDTree
import pandas as pd
import requests

# Inicializar la aplicación Flask
app = Flask(__name__)
CORS(app)  # Habilitar CORS en toda la aplicación

# Cargar las características desde el archivo CSV
df_caracteristicas = pd.read_csv('features_vectors.csv', header=None)
df_caracteristicas.rename(columns={0: 'track_id'}, inplace=True)

# Cargar el archivo de metadatos de canciones
df_songs = pd.read_csv('spotify_songs.csv')

# Crear la matriz de características y la lista de IDs
caracteristicas = df_caracteristicas.drop(columns=['track_id']).values
track_ids = df_caracteristicas['track_id'].values

# Construir el KDTree
tree = KDTree(caracteristicas)

def buscar_knn(consulta_id, k):
    consulta_vector = df_caracteristicas[df_caracteristicas['track_id'] == consulta_id].drop(columns=['track_id']).values
    if consulta_vector.shape[0] == 0:
        raise ValueError(f"Track ID {consulta_id} not found in features_vectors.csv")
    distancias, indices = tree.query(consulta_vector, k=k)
    resultados = [(track_ids[i], distancias[0][j]) for j, i in enumerate(indices[0])]
    return resultados

def get_itunes_album_cover_url(album_name):
    search_url = f"https://itunes.apple.com/search?term={album_name}&entity=album"
    response = requests.get(search_url)
    data = response.json()
    if data['resultCount'] > 0:
        return data['results'][0]['artworkUrl100']
    else:
        return None

@app.route('/recommend_knn', methods=['POST'])
def recommend_knn():
    data = request.get_json()
    consulta_id = data.get('track_id')
    k = int(data.get('top_k', 6))  # Número de vecinos más cercanos

    if not consulta_id:
        return jsonify(error="track_id is required"), 400

    try:
        recomendaciones = buscar_knn(consulta_id, k)
        response = []
        for rec_id, distancia in recomendaciones:
            track_info = df_songs[df_songs['track_id'] == rec_id].iloc[0].to_dict()
            lyrics = track_info.get('lyrics', 'Lyrics not available')
            truncated_lyrics = (lyrics[:200] + '...') if lyrics != 'Lyrics not available' and len(lyrics) > 200 else lyrics
            response.append({
                'track_id': rec_id,
                'track_name': track_info.get('track_name', 'Unknown'),
                'artist_name': track_info.get('track_artist', 'Unknown'),
                'album_name': track_info.get('track_album_name', 'Unknown'),
                'release_date': track_info.get('track_album_release_date', 'Unknown'),
                'lyrics': truncated_lyrics,
                'album_cover': get_itunes_album_cover_url(track_info.get('track_album_name', '')),
                'distance': distancia
            })
        print("Response: ", response)  # Registro de la respuesta
        return jsonify(recommendations=response)
    except ValueError as ve:
        print("ValueError: ", str(ve))  # Registro del error
        return jsonify(error=str(ve)), 400
    except Exception as e:
        print("Error: ", str(e))  # Registro del error
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)  # Cambiar el puerto si es necesario

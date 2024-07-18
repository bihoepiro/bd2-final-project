from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.neighbors import KDTree
import pandas as pd
import numpy as np
import requests
from SongRecognizer import SongRecognizer
from KNNHighD import KNNHighD
from KNNRTree import KNNRTree

app = Flask(__name__)
CORS(app)

df_caracteristicas = pd.read_csv('features_vectors.csv', header=None)
df_caracteristicas.rename(columns={0: 'track_id'}, inplace=True)
df_songs = pd.read_csv('spotify_songs.csv')

caracteristicas = df_caracteristicas.drop(columns=['track_id']).values
track_ids = df_caracteristicas['track_id'].values

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

knn_highd = KNNHighD(num_bits=32)
knn_highd.load_features_from_csv('features_vectors.csv')
knn_highd.build_index()

def buscar_knn_highD(consulta_id, k):
    consulta_vector = df_caracteristicas[df_caracteristicas['track_id'] == consulta_id].drop(columns=['track_id']).values
    if consulta_vector.shape[0] == 0:
        raise ValueError(f"Track ID {consulta_id} not found in features_vectors.csv")
    query_features = np.array(consulta_vector, dtype=np.float32)
    results = knn_highd.knn_query(query_features, k=k)
    return results

knn_rtree = KNNRTree()
knn_rtree.load_features_from_csv('features_vectors.csv')
knn_rtree.build_index()

def buscar_knn_RTree(consulta_id, k):
    consulta_vector = df_caracteristicas[df_caracteristicas['track_id'] == consulta_id].drop(columns=['track_id']).values
    if consulta_vector.shape[0] == 0:
        raise ValueError(f"Track ID {consulta_id} not found in features_vectors.csv")
    query_features = np.array(consulta_vector, dtype=np.float32)
    results = knn_rtree.knn_query(query_features, k=k)
    return results

#reconocedor de audio
def query_features_Recognizer(audiowav):
    reco = SongRecognizer(audiowav)
    r = reco.recognize_song()
    query_features = reco.extraer_fv(r, "features_vectors.csv", "spotify_songs.csv")
    return query_features

@app.route('/recommend_knn', methods=['POST'])
def recommend_knn():
    data = request.get_json()
    consulta_id = data.get('track_id')
    k = int(data.get('top_k', 6))
    method = data.get('method', 'KNN-Secuencial')

    if not consulta_id:
        return jsonify(error="track_id is required"), 400

    try:
        if method == 'KNN-Secuencial':
            recomendaciones = buscar_knn(consulta_id, k)
        elif method == 'KNN-HighD':
            recomendaciones = buscar_knn_highD(consulta_id, k)
        elif method == 'KNN-RTree':
            recomendaciones = buscar_knn_RTree(consulta_id, k)
        else:
            raise ValueError(f"Invalid method: {method}")

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
        print("Response: ", response)
        return jsonify(recommendations=response)
    except ValueError as ve:
        print("ValueError: ", str(ve))
        return jsonify(error=str(ve)), 400
    except Exception as e:
        print("Error: ", str(e))
        return jsonify(error=str(e)), 500

if __name__ == '__main__':
    app.run(debug=True, port=5002)

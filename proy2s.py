# -*- coding: utf-8 -*-
"""Proy2S.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1NgcYtKRYkJtanhqPH5xDkGuwfLTfBXPj
"""

class Doc:
    def __init__(self, track_id, track_name, track_artist, lyrics, track_popularity,
                 track_album_id, track_album_name, track_album_release_date, playlist_name,
                 playlist_id, playlist_genre, playlist_subgenre, danceability, energy, key,
                 loudness, mode, speechiness, acousticness, instrumentalness, liveness, valence,
                 tempo, duration_ms, language):
        self.track_id = track_id
        self.track_name = track_name
        self.track_artist = track_artist
        self.lyrics = lyrics
        self.track_popularity = track_popularity
        self.track_album_id = track_album_id
        self.track_album_name = track_album_name
        self.track_album_release_date = track_album_release_date
        self.playlist_name = playlist_name
        self.playlist_id = playlist_id
        self.playlist_genre = playlist_genre
        self.playlist_subgenre = playlist_subgenre
        self.danceability = danceability
        self.energy = energy
        self.key = key
        self.loudness = loudness
        self.mode = mode
        self.speechiness = speechiness
        self.acousticness = acousticness
        self.instrumentalness = instrumentalness
        self.liveness = liveness
        self.valence = valence
        self.tempo = tempo
        self.duration_ms = duration_ms
        self.language = language

import pandas as pd
import os
import nltk
import pickle
import glob
import numpy as np
from collections import defaultdict
from sklearn.metrics.pairwise import cosine_similarity

nltk.download('punkt')
from nltk.stem.snowball import SnowballStemmer

stemmer = SnowballStemmer('english')

class SPIMIBlock:
    def __init__(self, block_id, memory_limit):
        self.block_id = block_id
        self.memory_limit = memory_limit
        self.inverted_index = {}
        self.current_memory_usage = 0

    def add_to_index(self, term, doc_id, tf):
        if term not in self.inverted_index:
            self.inverted_index[term] = {}
        self.inverted_index[term][doc_id] = tf
        self.current_memory_usage += self._calculate_memory_usage(term, doc_id, tf)

        if self.current_memory_usage > self.memory_limit:
            self.write_to_disk()
            self.reset_block()

    def write_to_disk(self):
        with open(f'block_{self.block_id}.pkl', 'wb') as f:
            pickle.dump(self.inverted_index, f)

    def reset_block(self):
        self.inverted_index = {}
        self.current_memory_usage = 0

    def _calculate_memory_usage(self, term, doc_id, tf):
        return len(term) + 28  # Estimación simplificada

class Doc:
    def __init__(self, *args):
        self.track_id = args[0]
        self.track_name = args[1]
        self.track_artist = args[2]
        self.lyrics = args[3]

        self.language = args[-1]

def obtener_tf(words, word):
    return words.count(word)

def procesar_documento(text):
    stoplist = set(["a", "an", "and", "are", "as", "at", "be", "but", "by",
                    "for", "if", "in", "into", "is", "it", "no", "not", "of",
                    "on", "or", "such", "that", "the", "their", "then", "there",
                    "these", "they", "this", "to", "was", "will", "with", "...",
                    "/", "-", "&", ")", "(", ".", "..", "?", "'s"])
    words = nltk.word_tokenize(text.lower())
    return [stemmer.stem(word) for word in words if word not in stoplist]

# Lectura y procesamiento de los documentos
csv_file = 'data.csv'  # Ajustar la ruta del archivo
df = pd.read_csv(csv_file)

docs = []
memory_limit = 1e6  # Límite de memoria en bytes (ajustar según sea necesario)
current_block_id = 0
current_block = SPIMIBlock(current_block_id, memory_limit)

for index, row in df.iterrows():
    doc = Doc(*row)
    docs.append(doc)
    words = procesar_documento(doc.lyrics)

    for word in set(words):
        tf = obtener_tf(words, word)
        current_block.add_to_index(word, index + 1, tf)

if current_block.inverted_index:
    current_block.write_to_disk()

print("Indexación completada.")

def merge_blocks(block_filenames):
    merged_index = {}

    for block_filename in block_filenames:
        with open(block_filename, 'rb') as f:
            block = pickle.load(f)
            for term, postings in block.items():
                if term not in merged_index:
                    merged_index[term] = postings
                else:
                    merged_index[term].update(postings)

    return merged_index
import glob
block_files = glob.glob('block_*.pkl')
final_index = merge_blocks(block_files)

with open('final_index.pkl', 'wb') as f:
    pickle.dump(final_index, f)

print("Fusión de bloques completada.")

def vectorize_documents(index, num_docs):
    doc_vectors = defaultdict(lambda: np.zeros(len(index)))
    term_index = {term: i for i, term in enumerate(index.keys())}

    for term, postings in index.items():
        for doc_id, tf in postings.items():
            doc_vectors[doc_id][term_index[term]] = tf

    return doc_vectors, term_index

def vectorize_query(query, term_index):
    query_vector = np.zeros(len(term_index))
    for term in query:
        if term in term_index:
            query_vector[term_index[term]] = 1
    return query_vector.reshape(1, -1)

with open('final_index.pkl', 'rb') as f:
    final_index = pickle.load(f)

num_docs = len(df)
doc_vectors, term_index = vectorize_documents(final_index, num_docs)

query_text = "latina"
query_terms = procesar_documento(query_text)
query_vector = vectorize_query(query_terms, term_index)

similarities = []
for doc_id, doc_vector in doc_vectors.items():
    similarity = cosine_similarity(query_vector, doc_vector.reshape(1, -1))
    similarities.append((doc_id, similarity[0][0]))

top_k = 30
top_k_docs = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]

# Obtener los documentos originales para los resultados top-K
top_k_results = [(docs[doc_id - 1].track_name, docs[doc_id - 1].lyrics) for doc_id, _ in top_k_docs]

print("Documentos top-K más similares:")
for track_name, lyrics in top_k_results:
    print(f"Track Name: {track_name}, Lyrics: {lyrics}")
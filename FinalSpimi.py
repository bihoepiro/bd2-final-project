# FinalSpimi.py
import pandas as pd
import nltk
import math
import json
from nltk.stem.snowball import SnowballStemmer

nltk.download('punkt')
stemmer = SnowballStemmer('english')

# Leer el archivo CSV y eliminar columnas innecesarias
Dataf = pd.read_csv("C://Users//bepiquien//utec//bd2//spotify_songs.csv")

def preprocesamiento(doc):
    stoplist = ["a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if", "in", "into",
                "is", "it", "no", "not", "of", "on", "or", "such", "that", "the", "their", "then",
                "there", "these", "they", "this", "to", "was", "will", "with", "...", "/", "-", "&",
                ")", "(", ".", "..", "?", "'s"]
    row_text = ' '.join(doc.astype(str).tolist())
    row_text = nltk.word_tokenize(row_text.lower())
    row_text = [stemmer.stem(row_text[i]) for i in range(len(row_text))]
    doc_ = [word for word in row_text if word not in stoplist]
    return doc_

def recibir_query(query):
    stoplist = ["a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if", "in", "into",
                "is", "it", "no", "not", "of", "on", "or", "such", "that", "the", "their", "then",
                "there", "these", "they", "this", "to", "was", "will", "with", "...", "/", "-", "&",
                ")", "(", ".", "..", "?", "'s"]
    row_text = nltk.word_tokenize(query.lower())
    row_text = [stemmer.stem(row_text[i]) for i in range(len(row_text))]
    doc_ = [word for word in row_text if word not in stoplist]
    return doc_

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

def tf(term, doc_words):
    return doc_words.count(term)

def prepro_cancion(df):
    stoplist = ["a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if", "in", "into",
                "is", "it", "no", "not", "of", "on", "or", "such", "that", "the", "their", "then",
                "there", "these", "they", "this", "to", "was", "will", "with", "...", "/", "-", "&",
                ")", "(", ".", "..", "?", "'s"]
    diccionario_palabras = {}
    diccionario_docs = {}

    for index, row in df.iterrows():
        row_text = ' '.join(row.astype(str).tolist())
        row_text = nltk.word_tokenize(row_text.lower())
        words_ = [stemmer.stem(row_text[i]) for i in range(len(row_text))]
        words = [word for word in words_ if word not in stoplist]

        for word in words:
            diccionario_palabras.setdefault(word, {})[index + 1] = tf(word, words_)
            if "df" in diccionario_palabras[word]:
                diccionario_palabras[word]["df"] += 1
            else:
                diccionario_palabras[word]["df"] = 1

        diccionario_docs[index + 1] = words_

    return diccionario_palabras

def compute_tfidf(tf, df, cant_docs):
    return math.log10(1 + tf) * math.log10(cant_docs / df)

class Bloque:
    def __init__(self, limite):
        self.limite = limite
        self.entradas = {}
        self.next_block = None

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

    @staticmethod
    def cargar(filename):
        with open(filename, 'r') as file:
            data = json.load(file)
        bloque = Bloque(len(data['entradas']))
        bloque.entradas = data['entradas']
        bloque.next_block = data['next_block']
        return bloque

def crear_bloques(diccionario_ordenado, limite_bloque):
    bloques = []
    bloque_actual = Bloque(limite_bloque)
    bloques.append(bloque_actual)

    for palabra, docs in diccionario_ordenado.items():
        if not bloque_actual.agregar_entrada(palabra, docs):
            nuevo_bloque = Bloque(limite_bloque)
            nuevo_bloque.agregar_entrada(palabra, docs)
            bloque_actual.next_block = f'bloque_{len(bloques)}.json'
            bloques.append(nuevo_bloque)
            bloque_actual = nuevo_bloque

    return bloques

def guardar_bloques(bloques, prefix='bloque'):
    for i, bloque in enumerate(bloques):
        filename = f'{prefix}_{i}.json'
        bloque.guardar(filename)

def cargar_bloques_y_docs():
    # Cargar los bloques desde archivos JSON
    bloques_cargados = []
    for i in range(len(bloques)):
        filename = f'bloque_{i}.json'
        bloque_cargado = Bloque.cargar(filename)
        bloques_cargados.append(bloque_cargado)

    # Número total de documentos
    cant_docs = Dataf.shape[0]
    return bloques_cargados, cant_docs

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

    # Obtener detalles adicionales de los documentos principales
    resultados_finales = []
    for doc_id, score_info in top_k_documentos:
        doc_id_int = int(doc_id)
        doc_details = {
            'track_name': Dataf.loc[doc_id_int - 1, 'track_name'],
            'lyrics': Dataf.loc[doc_id_int - 1, 'lyrics'],
            'duration_ms': Dataf.loc[doc_id_int - 1, 'duration_ms'],
            'score': score_info
        }
        resultados_finales.append(doc_details)
    return resultados_finales



# Preprocesar las canciones y crear bloques
fuerte_dic = prepro_cancion(Dataf)
diccionario_ordenado = dict(sorted(fuerte_dic.items()))
limite_bloque = 512
bloques = crear_bloques(diccionario_ordenado, limite_bloque)
guardar_bloques(bloques)

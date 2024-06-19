# FinalSpimi.py
import pandas as pd
import nltk
import math
import os
import json
from nltk.stem.snowball import SnowballStemmer

nltk.download('punkt')
stemmer = SnowballStemmer('english')

# Leer el archivo CSV y eliminar columnas innecesarias
Dataf = pd.read_csv("only_letras.csv")

# DICCIONARIO DOCS
diccionario_docs = {}
def obtener_document_frequency(docs):
    df = {}
    for words in docs.values():
        unique_words = set(words)  # Para que solo cuente una palabra y no repetidas en la canción
        for word in unique_words:
            df[word] = df.get(word, 0) + 1
    return df

def obtener_idf(df, N):
    idf = {word: math.log(N / df[word]) for word in df}
    return idf

def preprocesamiento(doc):
    stoplist = ["a", "an", "and", "are", "as", "at", "be", "but", "by", "for", "if", "in", "into",
                "is", "it", "no", "not", "of", "on", "or", "such", "that", "the", "their", "then",
                "there", "these", "they", "this", "to", "was", "will", "with", "...", "/", "-", "&",
                ")", "(", ".", "..", "?", "'s"]
    row_text = ' '.join(doc.astype(str).tolist())

    # TOKENIZAR (DIVIDIR EL TEXTO EN PALABRAS)
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

""" De otro modo:
def tf(term, doc_words):
  times = 0
  for word in doc_words:
    if word == term:
      times +=1

  return times
"""

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
    #print(diccionario_palabras)
    return diccionario_palabras


def compute_tfidf(tf, df, cant_docs):
    return math.log10(1 + tf) * math.log10(cant_docs / df) #cant_docs=N

def determinar_bloque(i, limite):
    for j in range(1, limite + 1):
        # seleccionar bloque
        if i <= j * limite and i > (j - 1) * limite:
            return j
    return None

# Merge de bloques
"""
merged_blocks = {}
word_blocks = {}
for word, block in word_blocks.items():  # para cada palabra en los bloques
    if word not in merged_blocks:
        merged_blocks[word] = block.get_entries()[word]
    else:
        merged_blocks[word].update(block.get_entries()[word])
"""

class Bloque:
    def __init__(self, limite):
        self.limite = limite
        self.entradas = {}
        self.next_block = None

    def agregar_entrada(self, palabra, docs):
        #como cada bloque tiene un limite no debo pasar de el
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
    def cargar(filename): #almaceno en mem
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
            #cada bloque posee el termino y los documentos de docs y tf
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
        # la página en memoria secundaria (archivo JSON)
        filename = f'bloque_{i}.json'
        bloque_cargado = Bloque.cargar(filename)
        bloques_cargados.append(bloque_cargado)

    # Número total de documentos
    cant_docs = Dataf.shape[0]
    return bloques_cargados, cant_docs

# funcion de prueba para solo archivo.py
def procesar_consulta_prueba(query, k):
    query_terms = recibir_query(query)
    doc_scores = {}

    for term in query_terms:
        for bloque in bloques_cargados:
          #busco las palabras en los bloques, ya que estan ordenadas uso binary
            result = binary_search(bloque.entradas, term)
            #result va a guardar el docid y el tf de cada word(key)

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

#Funcion de procesar aplicado en API
def procesar_consulta(query, k, bloques_cargados, cant_docs):
    query_terms = recibir_query(query)
    doc_scores = {}

    for term in query_terms:
        for bloque in bloques_cargados:
            #aplico binary search de manera efectiva
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
            'score': score_info['score']
        }
        resultados_finales.append(doc_details)
    return resultados_finales

# Preprocesar las canciones y crear bloques
fuerte_dic = prepro_cancion(Dataf)
diccionario_ordenado = dict(sorted(fuerte_dic.items()))
limite_bloque = 2
bloques = crear_bloques(diccionario_ordenado, limite_bloque)
guardar_bloques(bloques)


# Cargar los bloques desde archivos JSON
bloques_cargados = []
for i in range(len(bloques)):
    filename = f'bloque_{i}.json'
    bloque_cargado = Bloque.cargar(filename)
    bloques_cargados.append(bloque_cargado)

# Ejemplo de consulta utilizando los bloques cargados
# Número total de documentos
"""
cant_docs = Dataf.shape[0]
query_text = "boy"
k = 5  # Número de documentos similares que queremos obtener
top_k_documentos = procesar_consulta_prueba(query_text, k)
print(top_k_documentos)
"""

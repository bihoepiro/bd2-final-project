# -*- coding: utf-8 -*-
"""Untitled10.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1ipUXvUyIUavt9nxH-pAapKaoi6L9G9vL
"""

import heapq
import pandas as pd
import os
import nltk
import math
import json
from collections import defaultdict
from nltk.stem.snowball import SnowballStemmer
from nltk.corpus import stopwords
nltk.download('punkt')
nltk.download('stopwords')

stemmer = SnowballStemmer('english')
stoplist = set(stopwords.words('english'))

def obtener_tf(index, word, diccionario_docs):
    frecuencia = 0
    words = diccionario_docs[index]
    for w in words:
        if w == word:
            frecuencia += 1
    return frecuencia

def obtener_document_frequency(docs):
    df = {}
    for words in docs.values():
        unique_words = set(words) #para que solo cuente una palabra y no repetidas en la cancion
        for word in unique_words:
            df[word] = df.get(word, 0) + 1
    return df

def obtener_idf(df, N):
    idf = {word: math.log(N / df[word]) for word in df}
    return idf

def spimi_invert_block(documents, block_size=1000):
    term_dictionary = defaultdict(list)
    block_count = 0

    for doc_id, terms in documents.items():
        for term in terms:
            if term not in stoplist:
                stemmed_term = stemmer.stem(term)
                term_dictionary[stemmed_term].append(doc_id)

        if len(term_dictionary) >= block_size:
            write_block_to_disk(term_dictionary, block_count)
            term_dictionary.clear()
            block_count += 1

    if term_dictionary:
        write_block_to_disk(term_dictionary, block_count)

def write_block_to_disk(term_dictionary, block_count):
    block_file_path = f'block_{block_count}.json'
    with open(block_file_path, 'w') as block_file:
        json.dump(term_dictionary, block_file)

def load_block_from_disk(block_count):
    block_file_path = f'block_{block_count}.json'
    with open(block_file_path, 'r') as block_file:
        return json.load(block_file)

def merge_blocks(block_count):
    merged_index = defaultdict(list)

    for block_index in range(block_count):
        block = load_block_from_disk(block_index)
        for term, doc_ids in block.items():
            merged_index[term].extend(doc_ids)

    # Remove duplicate doc_ids and sort them
    for term in merged_index:
        merged_index[term] = sorted(set(merged_index[term]))

    return merged_index

def cosine_similarity(query, document_vector):
    dot_product = sum(query[term] * document_vector.get(term, 0) for term in query)
    query_norm = math.sqrt(sum(value ** 2 for value in query.values()))
    document_norm = math.sqrt(sum(value ** 2 for value in document_vector.values()))

    if query_norm == 0 or document_norm == 0:
        return 0.0

    return dot_product / (query_norm * document_norm)

def query_processing(query, merged_index, idf, k):
    query_terms = nltk.word_tokenize(query)
    query_terms = [stemmer.stem(term) for term in query_terms if term not in stoplist]
    query_tf = {term: query_terms.count(term) for term in query_terms}
    query_vector = {term: tf * idf.get(term, 0) for term, tf in query_tf.items()}

    document_vectors = defaultdict(lambda: defaultdict(int))

    for term, doc_ids in merged_index.items():
        if term in query_vector:
            for doc_id in doc_ids:
                document_vectors[doc_id][term] += 1

    # Calcular las similitudes y mantener los top k en un heap
    min_heap = []
    for doc_id, doc_vector in document_vectors.items():
        score = cosine_similarity(query_vector, doc_vector)
        if len(min_heap) < k:
            heapq.heappush(min_heap, (score, doc_id))
        else:
            heapq.heappushpop(min_heap, (score, doc_id))

    # Ordenar los top k resultados antes de devolverlos
    top_k_results = sorted(min_heap, key=lambda item: item[0], reverse=True)
    return top_k_results

# Configuración de lectura de CSV y tokenización de texto
csv_file = 'data.csv'
df = pd.read_csv(csv_file)
documents = {}
for index, row in df.iterrows():
    row_text = ' '.join(row.astype(str).tolist())
    terms = nltk.word_tokenize(row_text)
    terms = [term.lower() for term in terms if term.isalnum()]
    documents[index] = terms

# Calcular frecuencias de documentos e IDF
df = obtener_document_frequency(documents)
N = len(documents)
idf = obtener_idf(df, N)

# Procesar bloques con SPIMI
spimi_invert_block(documents, block_size=1000)

# Merge de los bloques
block_count = len([name for name in os.listdir() if name.startswith('block_') and name.endswith('.json')])
merged_index = merge_blocks(block_count)


def insert_queryTOPK(query, k):
  results = query_processing(query,merged_index, idf, k)
  for  score, doc_id in results:
    return doc_id, score
      #print(f"Documento ID: {doc_id}, Similitud: {score}")


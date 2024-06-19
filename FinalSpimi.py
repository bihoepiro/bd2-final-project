# -*- coding: utf-8 -*-
"""Spimi-prepro.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1MY08p1RkM_5fJnp8og9KNjg8wn-3pL4M
"""

import pandas as pd
import os
import nltk
import math
nltk.download('punkt')
from nltk.stem.snowball import SnowballStemmer
stemmer = SnowballStemmer('english')

Dataf = pd.read_csv("only_letras.csv")
Dataf = Dataf.drop(columns=['Unnamed: 10','Unnamed: 11', 'Unnamed: 12', 'Unnamed: 13', 'Unnamed: 14', 'Unnamed: 15', 'Unnamed: 16', 'Unnamed: 17', 'Unnamed: 18', 'Unnamed: 19' ])

for index, row in Dataf.iterrows():
  row_text = ''.join(row.astype(str).tolist())
  print(row_text)

md = {}
md["word"] = [3, __]
print(md)

def preprocesamiento(doc):
  stoplist = ["a", "an", "and", "are", "as", "at", "be", "but", "by",
              "for", "if", "in", "into", "is", "it", "no", "not", "of",
              "on", "or", "such", "that", "the", "their", "then", "there",
              "these", "they", "this", "to", "was", "will", "with", "...", "/", "-", "&", ")", "(", ".", "..", "?", "'s"]
  row_text = ' '.join(doc.astype(str).tolist())
  row_text = nltk.word_tokenize(row_text.lower())
  row_text = [stemmer.stem(row_text[i]) for i in range(len(row_text))]
  doc_ = []
  for word in row_text:
    if word not in stoplist:
      doc_.append(word)
  return doc_

def recibir_query(query):
  stoplist = ["a", "an", "and", "are", "as", "at", "be", "but", "by",
              "for", "if", "in", "into", "is", "it", "no", "not", "of",
              "on", "or", "such", "that", "the", "their", "then", "there",
              "these", "they", "this", "to", "was", "will", "with", "...", "/", "-", "&", ")", "(", ".", "..", "?", "'s"]

  row_text = nltk.word_tokenize(query.lower())
  row_text = [stemmer.stem(row_text[i]) for i in range(len(row_text))]
  doc_ = []
  for word in row_text:
    if word not in stoplist:
      doc_.append(word)
  return doc_

#pages
def binary_search(pages, term):
  for page_num, page in pages.items():
          words = sorted(page.keys())
          low = 0
          high = len(words) - 1

          while low <= high:
              mid = (low + high) // 2
              mid_word = words[mid]

              if mid_word == term:
                  return page_num, term

              elif mid_word < term:
                  low = mid + 1

              else:
                  high = mid - 1
  return None, None

def tf(term, doc_words):
  times = 0
  for word in doc_words:
    if word == term:
      times +=1

  return times

def prepro_cancion(df):
  #tener en cuenta lo que va retornar esta función
  #tokenizar, reducir, eliminar stopwords
  stoplist = ["a", "an", "and", "are", "as", "at", "be", "but", "by",
              "for", "if", "in", "into", "is", "it", "no", "not", "of",
              "on", "or", "such", "that", "the", "their", "then", "there",
              "these", "they", "this", "to", "was", "will", "with", "...", "/", "-", "&", ")", "(", ".", "..", "?", "'s"]
  diccionario_palabras = {}
  diccionario_docs = {}
  lista_palabras = list(diccionario_palabras.keys())

  #aprovechar las iteraciones para calcular dfs e tdfs
  for index, row in df.iterrows():
      # Concatenar todos los atributos en una sola cadena
      row_text = ' '.join(row.astype(str).tolist())
      row_text = nltk.word_tokenize(row_text.lower())
      words_ = [stemmer.stem(row_text[i]) for i in range(len(row_text))]
      words = []
      for word in words_:
        if  word not in stoplist:
          words.append(word)
          #if word in diccionario_palabras:
          #  continue
          #else:
            #para garantizar el diccionario correcto
            #index me indica el doc (cancion)
            #diccionario_palabras me almacena info de la siguiente manera: "word":{df, }
          diccionario_palabras.setdefault(word, {})[index + 1] = tf(word,words_)
            #para el calculo del df, procuramos no contar dos veces un documento

          if "df" in diccionario_palabras[word]:
              diccionario_palabras[word]["df"] += 1
          else:
              diccionario_palabras[word]["df"] = 1
      diccionario_docs[index + 1] = words_
      #for word in words_:
      # diccionario_palabras.setdefault(word, {})[index+1] = obtener_tf(index +1, word)
  return diccionario_palabras

fuerte_dic = prepro_cancion(Dataf)

fuerte_dic["love"]

#indices locales
cant_docs = Dataf.shape[0]
limite_bloques = 100
bloques = {}
limite = int(cant_docs/limite_bloques)

#merge indices globales

def determinar_bloque(i, limite):
  for j in range(limite + 1):
    # seleccionar bloque
    if i <= j*limite and i > (j-1)*limite:
      return j

def compute_tfidf(tf, df):
    # Calcular el peso tf idf para un temrino en un doc
    tfidf = math.log10(1+tf)*math.log10(cant_docs/df)
    return tfidf

import json

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
            # El bloque está lleno, crear un nuevo bloque
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

diccionario_ordenado = dict(sorted(fuerte_dic.items()))

limite_bloque = 50
bloques = crear_bloques(diccionario_ordenado, limite_bloque)

# Guardar los bloques en archivos JSON
guardar_bloques(bloques)

# Cargar los bloques desde archivos JSON
bloques_cargados = []
for i in range(len(bloques)):
    filename = f'bloque_{i}.json'
    bloque_cargado = Bloque.cargar(filename)
    bloques_cargados.append(bloque_cargado)

# Ejemplo de consulta utilizando los bloques cargados
query_text = "your query text here"
k = 5  # Número de documentos similares que queremos obtener
top_k_documentos = procesar_consulta(query_text, k)
print(top_k_documentos)

from rtree import index
#usamos esta libreria para indexar todos los vectores caracteristicos
import pandas as pd
import numpy as np
import time

#data = pd.read_csv("feature_vectors.csv")
#ids = data.iloc[:,0].to_numpy()
#feature_vectors = data.iloc[:, 1:].astype(float).to_numpy()

class KNNRTree:
    def __init__(self):
        self.index = None
        self.collection = []
        self.id_to_vector = {}

    def load_features_from_csv(self, csv_path: str):
        df = pd.read_csv(csv_path)
        ids = df.iloc[:, 0].to_numpy()
        self.collection = df.iloc[:, 1:].astype(float).to_numpy()
        self.id_to_vector = {id_: vector for id_, vector in zip(ids, self.collection)}

    def build_index(self):
        d = self.collection.shape[1]
        p = index.Property()
        p.dimension = d
        self.index = index.Index(properties=p)
        for id_, vector in self.id_to_vector.items():
            self.index.insert(id_, (*vector, *vector))

    def knn_query(self, query_features: np.ndarray, k: int) -> list:
        if self.index is None:
            raise ValueError("Index has not been built.")

        nearest_neighbors = list(self.index.nearest(coordinates=tuple(query_features), num_results=k))
        results = []
        for nn in nearest_neighbors:
            vector = self.id_to_vector[nn]
            distance = np.linalg.norm(np.array(vector) - query_features)
            results.append((nn, distance))
        return results

# Cargar los datos
#data = pd.read_csv("feature_vectors.csv")
#ids = data.iloc[:, 0].to_numpy()
#feature_vectors = data.iloc[:, 1:].astype(float).to_numpy()

# Crear el objeto KNNRTree
#knn_rtree = KNNRTree()
#knn_rtree.load_features_from_csv("feature_vectors.csv")
#knn_rtree.build_index()

# Realizar una consulta KNN
#query_vector = feature_vectors[0]
#results = knn_rtree.knn_query(query_vector, k=5)
#print(results)

#myindexrtree = KNNRTree()
#myindexrtree.load_features_from_csv("feature_vectors.csv")
#tiempo_inicio = time.time()
#myindexrtree.build_index()
#tiempo_fin = time.time()
#tiempo_total = tiempo_fin - tiempo_inicio
#print(f"Tiempo de ejecución: {tiempo_total} segundos")

#prueba query knn
#myindexrtree.knn_query(feature_vectors[1], 5)

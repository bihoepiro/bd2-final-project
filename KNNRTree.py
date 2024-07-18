from rtree import index
import pandas as pd
import numpy as np

class KNNRTree:
    def __init__(self):
        self.index = None
        self.collection = []
        self.id_to_vector = {}

    def load_features_from_csv(self, csv_path: str):
        df = pd.read_csv(csv_path)
        ids = df.iloc[:, 0].astype(str).to_numpy()  # Asegurarse de que los IDs sean cadenas
        self.collection = df.iloc[:, 1:].astype(float).to_numpy()
        self.id_to_vector = {id_: vector for id_, vector in zip(ids, self.collection)}

    def build_index(self):
        d = self.collection.shape[1]
        p = index.Property()
        p.dimension = d
        self.index = index.Index(interleaved=True, properties=p)
        for id_, vector in self.id_to_vector.items():
            # Convertir id_ a entero
            id_int = int.from_bytes(id_.encode(), 'little')
            # Asegurarse de que las coordenadas sean números
            vector = np.array(vector, dtype=float)
            self.index.insert(id_int, (*vector, *vector), obj=id_)

    def knn_query(self, query_features: np.ndarray, k: int) -> list:
        if self.index is None:
            raise ValueError("Index has not been built.")
        query_tuple = tuple(query_features[0])
        nearest_neighbors = list(self.index.nearest(coordinates=query_tuple, num_results=k, objects='raw'))
        results = [(nn, np.linalg.norm(np.array(self.id_to_vector[nn]) - query_features)) for nn in nearest_neighbors]
        return results

# Ejemplo de uso:
# knn_rtree = KNNRTree()
# knn_rtree.load_features_from_csv("features_vectors.csv")
# knn_rtree.build_index()
# query_vector = np.array([feature_vector_a_consultar])
# results = knn_rtree.knn_query(query_vector, k=5)
# print(results)

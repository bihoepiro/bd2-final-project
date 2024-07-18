import pandas as pd
import numpy as np
import faiss
import time

class KNNHighD:
    def __init__(self, num_bits: int):
        self.num_bits = num_bits
        self.index = None
        self.collection = []

    def load_features_from_csv(self, csv_path: str):
        df = pd.read_csv(csv_path)
        #self.collection = [(row[1], np.array(row.drop(1), dtype=np.float32)) for _, row in df.iterrows()]
        self.collection = [(row.iloc[0], np.array(row.iloc[1:], dtype=np.float32)) for _, row in df.iterrows()]
        #print(f"Cargadas {len(self.collection)} características con dimensión {self.collection[0][1].shape[0]}")

    def build_index(self):
        if not self.collection:
            raise ValueError("No features loaded.")
        d = self.collection[0][1].shape[0]
        self.index = faiss.IndexLSH(d, self.num_bits)
        features = np.asarray([feat for _, feat in self.collection], dtype=np.float32)
        self.index.add(features)
        #print(f"Índice construido con características de dimensión {d}")

    def knn_query(self, query_features: np.ndarray, k: int) -> list:
        if self.index is None:
            raise ValueError("Index has not been built.")
        
        start_time = time.time()
        distances, indices = self.index.search(query_features.reshape(1, -1).astype('float32'), k)
        end_time = time.time()
        query_time = end_time - start_time
        
        results = [(self.collection[idx][0], distances[0][i]) for i, idx in enumerate(indices[0])]
        
        return results, query_time

  

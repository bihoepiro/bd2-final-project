from sklearn.neighbors import KDTree
import pandas as pd


df_caracteristicas = pd.read_csv('caracteristicas.csv')

# Crear la matriz de características
caracteristicas = df_caracteristicas.drop(columns=['track_id']).values
track_ids = df_caracteristicas['track_id'].values

# Construir el KDTree
tree = KDTree(caracteristicas)

def buscar_knn(consulta_id, k):
    consulta_vector = df_caracteristicas[df_caracteristicas['track_id'] == consulta_id].drop(columns=['track_id']).values
    distancias, indices = tree.query(consulta_vector, k=k)
    resultados = [(track_ids[i], distancias[0][j]) for j, i in enumerate(indices[0])]
    return resultados

def buscar_por_rango(consulta_id, radio):
    consulta_vector = df_caracteristicas[df_caracteristicas['track_id'] == consulta_id].drop(columns=['track_id']).values
    indices = tree.query_radius(consulta_vector, r=radio)
    resultados = [(track_ids[i], np.linalg.norm(caracteristicas[indices[0][j]] - consulta_vector)) for j in range(len(indices[0]))]
    return resultados

# Prueba
consulta_id = 'some_track_id'
k = 5
radio = 0.5

print("Top K resultados:")
print(buscar_knn(consulta_id, k))

print("Resultados por rango:")
print(buscar_por_rango(consulta_id, radio))

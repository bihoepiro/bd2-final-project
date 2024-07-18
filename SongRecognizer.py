import time
import base64
import hmac
import hashlib
import requests
import json
import os
import pandas as pd
import numpy as np

class SongRecognizer:
    def __init__(self, audiowav):
        self.audiowav = audiowav
        self.access_key = '4f1abb4878046fcb076f9980bf43655e'
        self.access_secret = 'J0CUxPvgvEFGsMcuc8gTBZVRKoGgLgvCyvdPoHGP'
        self.host = 'identify-us-west-2.acrcloud.com'

    def recognize_song(self):
        http_method = "POST"
        http_uri = "/v1/identify"
        data_type = "audio"
        signature_version = "1"
        timestamp = str(time.time())

        string_to_sign = f"{http_method}\n{http_uri}\n{self.access_key}\n{data_type}\n{signature_version}\n{timestamp}"
        sign = base64.b64encode(
            hmac.new(self.access_secret.encode('utf-8'), string_to_sign.encode('utf-8'),
                     digestmod=hashlib.sha1).digest()
        )

        files = {'sample': open(self.audiowav, 'rb')}
        data = {
            'access_key': self.access_key,
            'sample_bytes': os.path.getsize(self.audiowav),
            'timestamp': timestamp,
            'signature': sign,
            'data_type': data_type,
            'signature_version': signature_version
        }

        response = requests.post(f"http://{self.host}{http_uri}", files=files, data=data)
        return response.json()

    def extraer_fv(self, result, fea_p, spo_p):
        try:
            # Validar el resultado de la API
            if 'metadata' not in result or 'music' not in result['metadata']:
                raise ValueError("La estructura de respuesta no es válida.")

            primer_elemento = result['metadata']['music'][0]
            nombre_pista = primer_elemento['external_metadata']['spotify']['track']['name']
            nombre_artista = primer_elemento['external_metadata']['spotify']['artists'][0]['name']

            # Leer el archivo de características
            column_names = ['track_id'] + [f'column_{i}' for i in range(1, 82)]
            df = pd.read_csv(fea_p, header=None, names=column_names)

            # Leer el archivo de Spotify
            df1 = pd.read_csv(spo_p)

            spoty_data_complete = pd.merge(left=df, right=df1, on='track_id', how='left')
            result_df = spoty_data_complete[(spoty_data_complete['track_name'] == nombre_pista) &
                                            (spoty_data_complete['track_artist'] == nombre_artista)].head(1)

            if result_df.empty:
                raise ValueError("No se encontró coincidencia para la pista y artista especificados.")

            cod = result_df['track_id'].iloc[0]

            return cod

        except Exception as e:
            print(f"Error: {e}")
            raise


# Ejemplo de uso:


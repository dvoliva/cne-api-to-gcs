import requests
import json
from google.cloud import storage
import os  # Importa el módulo os para manejar rutas de archivos

def obtener_token(email, password):
    """Obtiene el token de autenticación."""
    auth_url = "https://api.cne.cl/api/login"
    params = {
        "email": email,
        "password": password
    }
    response = requests.post(auth_url, params=params)
    response.raise_for_status()
    return response.json().get("token")

def obtener_estaciones(token):
    """Obtiene los datos de las estaciones."""
    estaciones_url = "https://api.cne.cl/api/v4/estaciones"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(estaciones_url, headers=headers)
    response.raise_for_status()
    return response.json()

def guardar_ndjson_en_cloud_storage(data, ruta_archivo, bucket_name, credentials_json):
    """Guarda los datos en formato NDJSON en Google Cloud Storage."""
    credentials_dict = json.loads(credentials_json)  # Convierte el JSON de las credenciales a un diccionario
    storage_client = storage.Client.from_service_account_info(credentials_dict)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(ruta_archivo)

    with blob.open("w") as f:
        if isinstance(data, list):
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        elif isinstance(data, dict):
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
        else:
            f.write(json.dumps(str(data), ensure_ascii=False) + "\n")

if __name__ == "__main__":
    # Obtiene las credenciales del entorno
    email = os.environ.get("EMAIL")
    password = os.environ.get("PASSWORD")
    ruta_archivo_ndjson = "estaciones.json"
    bucket_name = "archivos-pipeline-dta"
    credentials_file = os.environ.get("CREDENTIALS_FILE")

    # Validar que las variables de entorno estén configuradas
    if not email or not password or not credentials_file:
        print("Error: Las variables de entorno EMAIL, PASSWORD o CREDENTIALS_FILE no están configuradas.")
        exit(1)

    try:
        token = obtener_token(email, password)
        estaciones_data = obtener_estaciones(token)

        if isinstance(estaciones_data, dict) and "data" in estaciones_data and isinstance(estaciones_data["data"], list):
            estaciones_lista = estaciones_data["data"]
        elif isinstance(estaciones_data, list):
            estaciones_lista = estaciones_data
        else:
            estaciones_lista = [estaciones_data]

        guardar_ndjson_en_cloud_storage(estaciones_lista, ruta_archivo_ndjson, bucket_name, credentials_file)
        print(f"Datos guardados en {ruta_archivo_ndjson} en Google Cloud Storage (bucket: {bucket_name}).")

    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP: {e}")
    except Exception as e:
        print(f"Error: {e}")
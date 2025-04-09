import requests
import json

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

def guardar_ndjson(data, ruta_archivo):
    """Guarda los datos en formato NDJSON."""
    with open(ruta_archivo, "w", encoding="utf-8") as f:
        if isinstance(data, list):
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        elif isinstance(data, dict):
            f.write(json.dumps(data, ensure_ascii=False) + "\n")
        else:
            f.write(json.dumps(str(data), ensure_ascii=False) + "\n")

if __name__ == "__main__":
    # Ingresa tus credenciales directamente aquí (solo para pruebas locales)
    email = "venegasolivad@gmail.com"  # Reemplaza con tu correo
    password = "brsWBht4u7Kgat2"  # Reemplaza con tu contraseña
    ruta_archivo_ndjson = "estaciones.ndjson"

    try:
        token = obtener_token(email, password)
        estaciones_data = obtener_estaciones(token)

        if isinstance(estaciones_data, dict) and "data" in estaciones_data and isinstance(estaciones_data["data"], list):
            estaciones_lista = estaciones_data["data"]
        elif isinstance(estaciones_data, list):
            estaciones_lista = estaciones_data
        else:
            estaciones_lista = [estaciones_data]

        guardar_ndjson(estaciones_lista, ruta_archivo_ndjson)
        print(f"Datos guardados en {ruta_archivo_ndjson} en formato NDJSON")

    except requests.exceptions.HTTPError as e:
        print(f"Error HTTP: {e}")
    except Exception as e:
        print(f"Error: {e}")
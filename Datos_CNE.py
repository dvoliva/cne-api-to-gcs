import requests
import json
from google.cloud import storage
import os

# --- Cloud Storage Configuration ---
# Set your Google Cloud project ID and bucket name
PROJECT_ID = "pipeline-dta"  # Replace with your project ID
BUCKET_NAME = "archivos-pipeline-dta"  # Replace with your bucket name
JSON_FILE_NAME = "estaciones_data.json"  # Name of the JSON file in Cloud Storage

# --- Credentials (Consider using environment variables or a more secure method) ---
email = "venegasolivad@gmail.com"
password = "brsWBht4u7Kgat2"

# --- API URLs ---
auth_url = "https://api.cne.cl/api/login"
estaciones_url = "https://api.cne.cl/api/v3/combustible/calefaccion/callcenters"

# --- Authentication ---
def get_auth_token(email, password):
    """Authenticates with the API and returns the token."""
    params = {"email": email, "password": password}
    response = requests.post(auth_url, params=params)
    if response.status_code == 200:
        data = response.json()
        return data.get("token")
    else:
        print(f"Error al obtener el token: {response.status_code} {response.text}")
        return None

# --- Data Fetching ---
def get_estaciones_data(token):
    """Fetches the estaciones data using the provided token."""
    headers = {"Authorization": f"Bearer {token}"}
    response_estaciones = requests.get(estaciones_url, headers=headers)
    if response_estaciones.status_code == 200:
        return response_estaciones.json()
    else:
        print(f"Error al obtener estaciones: {response_estaciones.status_code} {response_estaciones.text}")
        return None

# --- Cloud Storage Upload ---
def upload_to_gcs(bucket_name, file_name, data):
    """Uploads data to Google Cloud Storage as a JSON file."""
    try:
        # Initialize the Cloud Storage client
        client = storage.Client(project=PROJECT_ID)
        bucket = client.bucket(bucket_name)
        blob = bucket.blob(file_name)

        # Convert data to JSON string
        json_data = json.dumps(data, ensure_ascii=False, indent=2)

        # Upload the JSON string to Cloud Storage
        blob.upload_from_string(json_data, content_type="application/json")

        print(f"Data uploaded to gs://{bucket_name}/{file_name}")
        return True
    except Exception as e:
        print(f"Error uploading to Cloud Storage: {e}")
        return False

# --- Main Execution ---
def main():
    """Main function to orchestrate the process."""
    token = get_auth_token(email, password)
    if token:
        estaciones_data = get_estaciones_data(token)
        if estaciones_data:
            upload_to_gcs(BUCKET_NAME, JSON_FILE_NAME, estaciones_data)

if __name__ == "__main__":
    main()

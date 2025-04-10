import json

# Abrir archivo original
with open("marcas_combustible.json", "r", encoding="utf-8") as f:
    data = json.load(f)  # esto carga el array

# Escribir NDJSON (una línea por registro)
with open("marcas_ndjson.json", "w", encoding="utf-8") as f:
    for obj in data:
        f.write(json.dumps(obj, ensure_ascii=False) + "\n")

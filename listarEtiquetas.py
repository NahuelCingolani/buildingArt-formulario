import requests
import os
from dotenv import load_dotenv

load_dotenv()

# ⚙️ Variables del entorno
url_odoo = os.getenv("ODOO_URL")
db = os.getenv("ODOO_DB")
user = os.getenv("ODOO_USER")
password = os.getenv("ODOO_PASSWORD")

# 🔐 Login
auth_payload = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "service": "common",
        "method": "login",
        "args": [db, user, password]
    },
    "id": 1
}

response = requests.post(url_odoo, json=auth_payload)
uid = response.json()["result"]

# 📦 Consultar etiquetas CRM
tag_payload = {
    "jsonrpc": "2.0",
    "method": "call",
    "params": {
        "service": "object",
        "method": "execute_kw",
        "args": [
            db,
            uid,
            password,
            "crm.tag",
            "search_read",
            [],
            {"fields": ["id", "name"]}
        ]
    },
    "id": 2
}

tag_response = requests.post(url_odoo, json=tag_payload)
tags = tag_response.json().get("result", [])

# 📋 Mostrar resultado
print("📌 Etiquetas disponibles:")
for tag in tags:
    print(f"🟦 ID: {tag['id']} | Nombre: {tag['name']}")

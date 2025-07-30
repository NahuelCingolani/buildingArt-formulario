from flask import Flask, request, render_template_string
import requests
from dotenv import load_dotenv
import os

load_dotenv()  # 🔑 Carga las variables desde el archivo .env

app = Flask(__name__)

# 🔧 Variables desde .env
url_odoo = os.getenv("ODOO_URL")
db = os.getenv("ODOO_DB")
user = os.getenv("ODOO_USER")
password = os.getenv("ODOO_API_KEY")

HTML_FORM = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Formulario de Consulta</title>
</head>
<body>
  <h2>Dejanos tus datos y te contactamos</h2>
  <form method="post">
    <label>Nombre y Apellido:</label><br>
    <input type="text" name="nombre" required><br><br>
    <label>Celular:</label><br>
    <input type="text" name="telefono" required><br><br>
    <label>Email:</label><br>
    <input type="email" name="email" required><br><br>
    <label>Tipo de Proyecto:</label><br>
    <input type="text" name="tipo_proyecto" required><br><br>
    <label>Nivel de Urgencia:</label><br>
    <input type="text" name="urgencia" required><br><br>
    <label>Comentarios:</label><br>
    <textarea name="comentarios" rows="4" cols="40"></textarea><br><br>
    <button type="submit">Enviar</button>
  </form>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        crear_lead_en_odoo(request.form)
        return "<h3>✅ ¡Gracias! Te estaremos contactando pronto.</h3>"
    return render_template_string(HTML_FORM)

def crear_lead_en_odoo(data):
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
    print("🔍 STATUS:", response.status_code)
    print("🔍 TEXTO:", response.text)

    try:
        uid = response.json()["result"]
    except Exception as e:
        print("❌ Error interpretando JSON de Odoo:", e)
        return

    lead_payload = {
        "jsonrpc": "2.0",
        "method": "call",
        "params": {
            "service": "object",
            "method": "execute_kw",
            "args": [
                db,
                uid,
                password,
                "crm.lead",
                "create",
                [{
                    "name": f"Oportunidad de {data['nombre']}",
                    "contact_name": data['nombre'],
                    "phone": data['telefono'],
                    "email_from": data['email'],
                    "description": (
                        f"📝 Tipo de proyecto: {data['tipo_proyecto']}\n"
                        f"🚀 Urgencia: {data['urgencia']}\n"
                        f"📌 Comentarios: {data['comentarios']}"
                    )
                }]
            ]
        },
        "id": 2
    }

    lead_response = requests.post(url_odoo, json=lead_payload)
    print("📨 Respuesta al crear lead:", lead_response.status_code, lead_response.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)




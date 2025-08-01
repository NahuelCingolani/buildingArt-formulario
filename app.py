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
password = os.getenv("ODOO_PASSWORD")

HTML_FORM = """
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <title>Formulario de Consulta</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      background-color: #f4f6f8;
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
    }
    .container {
      background-color: white;
      padding: 30px 40px;
      border-radius: 12px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.1);
      max-width: 500px;
      width: 100%;
    }
    h2 {
      text-align: center;
      color: #004080;
    }
    label {
      font-weight: bold;
      display: block;
      margin-top: 15px;
      color: #333;
    }
    input, textarea {
      width: 100%;
      padding: 10px;
      margin-top: 5px;
      border: 1px solid #ccc;
      border-radius: 6px;
    }
    button {
      margin-top: 20px;
      width: 100%;
      padding: 12px;
      background-color: #004080;
      color: white;
      border: none;
      border-radius: 6px;
      font-size: 16px;
      cursor: pointer;
    }
    button:hover {
      background-color: #0059b3;
    }
    .logo {
      display: block;
      margin: 0 auto 20px auto;
      max-width: 120px;
    }
  </style>
</head>
<body>
  <div class="container">
    <img src="/static/logo.png" alt="Logo" class="logo">
    <h2>Dejanos tus datos y te contactamos</h2>
    <form method="post">
      <label>Nombre y Apellido:</label>
      <input type="text" name="nombre" required>

      <label>Celular:</label>
      <input type="text" name="telefono" pattern="^[0-9]{8,15}$" title="Ingresá entre 8 y 15 números" required>

      <label>Email:</label>
      <input type="email" name="email" required>

      <label>Provincia:</label>
      <input type="text" name="provincia" required>

      <label>Localidad:</label>
      <input type="text" name="localidad" required>

      <label>Fecha:</label>
      <input type="date" name="fecha" required>

      <label>Tipo de Proyecto:</label>
      <input type="text" name="tipo_proyecto" required>

      <label>Productos de Interés:</label>
      <input type="text" name="productos_de_interes" required>

      <label>Nivel de Urgencia:</label>
      <input type="text" name="urgencia" required>

      <label>Comentarios:</label>
      <textarea name="comentarios" rows="4"></textarea>

      <button type="submit">Enviar</button>
    </form>
  </div>
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
    # Paso 1: Autenticación
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

    # Paso 2: Crear el lead
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
                    "provincia": data['provincia'],
                    "localidad": data['localidad'],
                    "fecha": data['fecha'],
                    "description": (
                        f"📝 Tipo de proyecto: {data['tipo_proyecto']}\n"
                        f"📦 Productos de interés: {data['productos_de_interes']}\n"
                        f"🚀 Urgencia: {data['urgencia']}\n"
                        f"📌 Comentarios: {data['comentarios']}"
                    ),
                    "tag_ids": [[6, 0, [24]]],  # ← Reemplazá 51 por el ID de tu etiqueta si querés otra
                }]
            ]
        },
        "id": 2
    }

    lead_response = requests.post(url_odoo, json=lead_payload)
    print("📨 Resultado JSON:", lead_response.json())
    print("📨 Respuesta al crear lead:", lead_response.status_code, lead_response.text)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)




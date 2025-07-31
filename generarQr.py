import qrcode

url = "https://buildingart-formulario.onrender.com"
img = qrcode.make(url)
img.save("formulario_qr.png")

print("✅ QR generado como formulario_qr.png")

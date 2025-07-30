import qrcode

url = "https://gfitness-formulario.onrender.com/"
img = qrcode.make(url)
img.save("formulario_qr.png")

print("✅ QR generado como formulario_qr.png")

import os
from flask import Flask, request, jsonify
import broadlink

app = Flask(__name__)

# Leemos las variables de entorno para no dejar contraseñas expuestas en GitHub
TOKEN_SECRETO = os.environ.get("TOKEN_SECRETO", "mi_clave_123")
BROADLINK_IP = os.environ.get("BROADLINK_IP", "192.168.1.50")
BROADLINK_MAC = os.environ.get("BROADLINK_MAC", "aabbccddeeff")

# Código HEX enviado por el control remoto para apagar el aire (reemplazar con el tuyo)
# Puedes obtener este código capturándolo previamente con la app o la librería python-broadlink
HEX_APAGAR_AIRE = "260024001a2b1b2a1a2b1b2a1a2b1b2a1a2b1b2a1a2b1b2a" 

@app.route('/apagar-aire', methods=['GET', 'POST'])
def apagar_aire():
    # 1. Validar el token de seguridad enviado por la URL
    token = request.args.get('token')
    if token != TOKEN_SECRETO:
        return jsonify({"status": "error", "message": "Token no válido"}), 403

    try:
        # 2. Convertir la dirección MAC de texto a bytes
        mac_bytes = bytes.fromhex(BROADLINK_MAC.replace(":", "").replace("-", ""))
        
        # 3. Conectarse directamente al RM4 Mini en la red local
        device = broadlink.gendevice(0x6539, (BROADLINK_IP, 80), mac_bytes) # 0x6539 suele ser el código de devtype del RM4 Mini
        device.auth()
        
        # 4. Enviar el paquete Infrarrojo
        payload = bytes.fromhex(HEX_APAGAR_AIRE)
        device.send_data(payload)
        
        return jsonify({"status": "success", "message": "Comando enviado al RM4 Mini para apagar el aire"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return "Servidor Webhook BroadLink Activo", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

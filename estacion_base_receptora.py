import paho.mqtt.client as mqtt
import json

# --- CONFIGURACIÓN DE LA CONEXIÓN ---
BROKER = "test.mosquitto.org"
PUERTO = 1883
TOPIC_SUSCRIPCION = "tesis/dron_inspeccion/alertas"

# --- FUNCIONES DE CONTROL ---
def al_conectar(cliente, userdata, flags, rc):
    """Esta función se ejecuta apenas logramos conectarnos al servidor."""
    if rc == 0:
        print(f"[*] CONEXIÓN EXITOSA AL SERVIDOR MQTT ({BROKER})")
        # Una vez conectados, nos suscribimos al canal del dron
        cliente.subscribe(TOPIC_SUSCRIPCION)
        print(f"[*] Escuchando alertas en el canal: '{TOPIC_SUSCRIPCION}'...\n")
    else:
        print(f"[!] Error de conexión. Código: {rc}")

def al_recibir_mensaje(cliente, userdata, mensaje):
    """Esta función se dispara AUTOMÁTICAMENTE cada vez que llega un mensaje."""
    print("="*50)
    print("       ¡NUEVA ALERTA RECIBIDA DESDE EL DRON!       ")
    print("="*50)
    
    try:
        # Decodificamos el mensaje JSON que llegó por internet
        datos_recibidos = json.loads(mensaje.payload.decode('utf-8'))
        
        # Mostramos los datos clave de forma amigable para el operador
        print(f"📡 ID Dron      : {datos_recibidos.get('dron_id', 'Desconocido')}")
        print(f"⏱️  Hora         : {datos_recibidos.get('timestamp', 'Sin fecha')}")
        print(f"⚠️  Tipo         : {datos_recibidos.get('tipo_alerta', 'Alerta')}")
        print("-" * 50)
        
        termicos = datos_recibidos.get('datos_termicos', {})
        print(f"🔥 Temp Máxima  : {termicos.get('temperatura_maxima_c', 'N/A')} °C")
        print(f"📊 Mediana Panel: {termicos.get('temperatura_mediana_c', 'N/A')} °C")
        print(f"📈 Umbral Disparo: {termicos.get('umbral_disparo_c', 'N/A')} °C")
        print("="*50 + "\n")
        
    except json.JSONDecodeError:
        print("[!] Se recibió un mensaje, pero no tiene formato JSON válido.")
        print(f"Mensaje crudo: {mensaje.payload.decode('utf-8')}")

# --- INICIO DEL PROGRAMA PRINCIPAL ---
print("Iniciando Estación Base de Monitoreo...")

# 1. Creamos el cliente receptor
cliente_receptor = mqtt.Client()

# 2. Asignamos las funciones que definimos arriba a los "eventos" del cliente
cliente_receptor.on_connect = al_conectar
cliente_receptor.on_message = al_recibir_mensaje

# 3. Nos conectamos al servidor
cliente_receptor.connect(BROKER, PUERTO, 60)

# 4. Dejamos el programa escuchando infinitamente
try:
    cliente_receptor.loop_forever()
except KeyboardInterrupt:
    print("\n[*] Apagando Estación Base...")
    cliente_receptor.disconnect()
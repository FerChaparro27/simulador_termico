import numpy as np
import cv2
import json
from datetime import datetime
import paho.mqtt.client as mqtt
# --- MÓDULO 1: ADQUISICIÓN DE DATOS ---
def simular_lectura_sensor():
    """Simula la captura de datos del MLX90640 y añade un hotspot."""
    matriz = np.random.uniform(low=30.0, high=35.0, size=(24, 32))
    matriz[5:8, 22:25] = 70.0  # Hotspot inyectado artificialmente
    return matriz

# --- MÓDULO 2: PROCESAMIENTO VISUAL ---
def procesar_visualizacion(matriz):
    """Normaliza, interpola y aplica el mapa de calor a la matriz cruda."""
    temp_min = np.min(matriz)
    temp_max = np.max(matriz)
    matriz_norm = np.uint8((matriz - temp_min) / (temp_max - temp_min) * 255)
    
    imagen_interp = cv2.resize(matriz_norm, (640, 480), interpolation=cv2.INTER_CUBIC)
    imagen_color = cv2.applyColorMap(imagen_interp, cv2.COLORMAP_INFERNO)
    
    return imagen_color, temp_max

# --- MÓDULO 3: INTELIGENCIA DE DETECCIÓN (EDGE AI) ---
def detectar_hotspots(matriz, imagen_color, temp_max):
    """Aplica umbral dinámico, encuentra anomalías y las resalta visualmente."""
    mediana = np.median(matriz)
    umbral = mediana + 15.0
    
    mascara = np.where(matriz > umbral, 255, 0).astype(np.uint8)
    mascara_esc = cv2.resize(mascara, (640, 480), interpolation=cv2.INTER_NEAREST)
    
    contornos, _ = cv2.findContours(mascara_esc, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    anomalias_detectadas = []
    
    for contorno in contornos:
        x, y, w, h = cv2.boundingRect(contorno)
        
        # Dibujo de alertas en pantalla
        cv2.rectangle(imagen_color, (x, y), (x+w, y+h), (0, 255, 0), 2)
        cv2.putText(imagen_color, f"ANOMALIA: {temp_max:.1f} C", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Guardar coordenadas para la telemetría
        anomalias_detectadas.append({"x": x, "y": y, "ancho": w, "alto": h})
        
    return imagen_color, anomalias_detectadas, mediana, umbral

# --- MÓDULO 4: TELEMETRÍA Y COMUNICACIÓN ---
def guardar_telemetria(anomalias, temp_max, mediana, umbral):
    """Genera el payload JSON y lo transmite a la nube vía MQTT."""
    if not anomalias:
        return # Si no hay anomalías, no hacemos nada
        
    payload = {
        "timestamp": datetime.now().isoformat(),
        "dron_id": "UAV-TESIS-01",
        "tipo_alerta": "HOTSPOT_DETECTADO",
        "datos_termicos": {
            "temperatura_maxima_c": round(temp_max, 2),
            "temperatura_mediana_c": round(mediana, 2),
            "umbral_disparo_c": round(umbral, 2)
        },
        "posicion_imagen": anomalias[0] 
    }
    
    # Convertimos el diccionario a un string JSON
    payload_json = json.dumps(payload)
    
    # Configuración del servidor MQTT Público
    broker = "test.mosquitto.org"
    puerto = 1883
    topic_publicacion = "tesis/dron_inspeccion/alertas"
    
    try:
        # Creamos el cliente, conectamos, disparamos el mensaje y cerramos
        cliente_mqtt = mqtt.Client()
        cliente_mqtt.connect(broker, puerto, 60)
        cliente_mqtt.publish(topic_publicacion, payload_json)
        cliente_mqtt.disconnect()
        print(f"-> EXITO: Telemetría enviada a la nube (Topic: {topic_publicacion})")
    except Exception as e:
        print(f"-> ERROR MQTT: No se pudo enviar el paquete. Detalles: {e}")
        
    # Mantenemos el guardado local como si fuera la "Caja Negra" del dron
    archivo = "alerta_mqtt_payload.json"
    with open(archivo, "w") as f:
        f.write(json.dumps(payload, indent=4))


def main():
    print("Iniciando Sistema Edge AI de Inspección...")
    
    # 1. Adquisición
    matriz_termica = simular_lectura_sensor()
    
    # 2. Visión
    imagen_base, temp_max = procesar_visualizacion(matriz_termica)
    
    # 3. Detección
    imagen_final, anomalias, mediana, umbral = detectar_hotspots(matriz_termica, imagen_base, temp_max)
    
    # 4. Telemetría
    if anomalias:
        print(f"¡ALERTA! Se detectó un hotspot.")
        guardar_telemetria(anomalias, temp_max, mediana, umbral)
    
    # 5. Salida por pantalla
    cv2.imshow("Plataforma de Inspeccion - Tesis", imagen_final)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Punto de entrada estándar en Python
if __name__ == "__main__":
    main()
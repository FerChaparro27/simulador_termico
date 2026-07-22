import numpy as np
import cv2
import json
from datetime import datetime
import paho.mqtt.client as mqtt
import time


# --- MÓDULO 1: ADQUISICIÓN DE DATOS ---
def simular_lectura_sensor(probabilidad_falla=0.1):
    """Simula la captura de datos. A veces inyecta un hotspot, a veces no."""
    matriz = np.random.uniform(low=30.0, high=35.0, size=(24, 32))
    
    # Hay un 10% de probabilidad de que aparezca una falla en este frame
    if np.random.rand() < probabilidad_falla:
        matriz[5:8, 22:25] = 70.0  
        
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

def enviar_heartbeat(mediana):
    """Envía un pulso de vida indicando que el sistema está operando bien."""
    payload = {
        "timestamp": datetime.now().isoformat(),
        "dron_id": "UAV-TESIS-01",
        "tipo_alerta": "HEARTBEAT",
        "estado": "SISTEMA_OK",
        "temperatura_promedio_panel": round(mediana, 2)
    }
    
    broker = "test.mosquitto.org"
    topic = "tesis/dron_inspeccion/alertas"
    
    try:
        cliente_mqtt = mqtt.Client()
        cliente_mqtt.connect(broker, 1883, 60)
        cliente_mqtt.publish(topic, json.dumps(payload))
        cliente_mqtt.disconnect()
        print(f"-> [💙 HEARTBEAT] Pulso enviado. Temp normal: {mediana:.1f} C")
    except Exception as e:
        pass # Si falla el latido, lo ignoramos silenciosamente para no frenar el vuelo

def main():
    print("Iniciando Sistema Edge AI de Inspección...")
    print("Presiona la tecla 'q' en la ventana de video para apagar el dron.")
    
    ultimo_latido = 0
    intervalo_latido = 5 # Enviaremos un latido cada 5 segundos
    
    while True: # BUCLE INFINITO (Simulando el vuelo)
        
        # 1. Adquisición continua
        matriz_termica = simular_lectura_sensor()
        
        # 2. Visión y Detección
        imagen_base, temp_max = procesar_visualizacion(matriz_termica)
        imagen_final, anomalias, mediana, umbral = detectar_hotspots(matriz_termica, imagen_base, temp_max)
        
        # 3. Telemetría de Fallas (Solo si detecta algo)
        if anomalias:
            print(f"\n¡ALERTA! Hotspot detectado a {temp_max:.1f} C")
            guardar_telemetria(anomalias, temp_max, mediana, umbral)
            
        # 4. Lógica de Heartbeat (Latido de Salud)
        tiempo_actual = time.time()
        if tiempo_actual - ultimo_latido >= intervalo_latido:
            enviar_heartbeat(mediana)
            ultimo_latido = tiempo_actual # Reiniciamos el cronómetro
            
        # 5. Salida por pantalla (Video)
        cv2.imshow("Plataforma de Inspeccion - Tesis", imagen_final)
        
        # El waitKey(100) hace que espere 100 milisegundos (10 FPS aprox)
        # Si presionas 'q', rompe el bucle y apaga el sistema
        if cv2.waitKey(1000) & 0xFF == ord('q'):
            print("Apagando motores y sistema de visión...")
            break

    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
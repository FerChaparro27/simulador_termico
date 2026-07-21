import numpy as np
import cv2
import json
from datetime import datetime

# 1. Simulación de la Matriz del MLX90640 
# se crea una matriz de 24x32 con valores aleatorios entre 30 y 35 grados Celsius
# se indica un hotspot en la región de 5:8 filas y 22:25 columnas con un valor de 70 grados Celsius
matriz_termica = np.random.uniform(low=30.0, high=35.0, size=(24, 32))
matriz_termica[5:8, 22:25] = 70.0 # Nuestro Hotspot inyectado

# 2. Normalización e Interpolación (La base visual)
# Normalizamos la matriz para que los valores estén entre 0 y 255
# temp_min sirve para obtener el valor mínimo de la matriz, y temp_max para el máximo    
# le damos una nueva resolución de 640x480 para que se vea más grande y clara
# la interpolacion se lleva a cabo haciendo un rezise de la matriz normalizada usando el método INTER_CUBIC
# para hacer la normalización, restamos el valor mínimo de la matriz y dividimos por el rango (max-min), luego multiplicamos por 255 para escalarlo a 8 bits
# cv2.resize se utiliza para cambiar el tamaño de la imagen, y cv2.INTER_CUBIC es un método de interpolación que produce resultados más suaves
temp_min = np.min(matriz_termica)
temp_max = np.max(matriz_termica)
matriz_normalizada = np.uint8((matriz_termica - temp_min) / (temp_max - temp_min) * 255)

ancho_nuevo = 640
alto_nuevo = 480
imagen_interpolada = cv2.resize(matriz_normalizada, (ancho_nuevo, alto_nuevo), interpolation=cv2.INTER_CUBIC)
imagen_termica = cv2.applyColorMap(imagen_interpolada, cv2.COLORMAP_INFERNO)

# --- AQUI EMPIEZA LA INTELIGENCIA ARTIFICIAL (EDGE AI) ---

# 3. Cálculo del Umbral Dinámico
mediana_temp = np.median(matriz_termica)
# Definimos que una anomalía es cualquier cosa 15 grados por encima de la mediana
umbral_falla = mediana_temp + 15.0 

# 4. Creación de Máscara Binaria (Separamos el hotspot del fondo)
# Si la temperatura supera el umbral, asignamos 255 (blanco), si no 0 (negro)
mascara_fallas = np.where(matriz_termica > umbral_falla, 255, 0).astype(np.uint8)

# Escalamos la máscara para que coincida con el tamaño de nuestra imagen visual
# (Usamos INTER_NEAREST para no difuminar los bordes de la máscara)
mascara_escalada = cv2.resize(mascara_fallas, (ancho_nuevo, alto_nuevo), interpolation=cv2.INTER_NEAREST)

# 5. Detección de Contornos con OpenCV
contornos, _ = cv2.findContours(mascara_escalada, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

for contorno in contornos:
    #los ejes w y h  son para  el ancho y alto de la caja delimitadora
    x, y, w, h = cv2.boundingRect(contorno)
    
    # Dibujamos en pantalla
    # en estas dos lineas hacemos  el dibujo de la caja delimitadora
    cv2.rectangle(imagen_termica, (x, y), (x+w, y+h), (0, 255, 0), 2)
    cv2.putText(imagen_termica, f"ANOMALIA: {temp_max:.1f} C", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    # 6. Construimos el Payload (Paquete de datos) JSON
    # el mensaje dependera de la temperatura máxima detectada, la mediana y el umbral de disparo
    payload_alerta = {
        "timestamp": datetime.now().isoformat(),
        "dron_id": "UAV-TESIS-01",
        "tipo_alerta": "HOTSPOT_DETECTADO",
        "datos_termicos": {
            "temperatura_maxima_c": round(temp_max, 2),
            "temperatura_mediana_c": round(mediana_temp, 2),
            "umbral_disparo_c": round(umbral_falla, 2)
        },
        "posicion_imagen": {
            "x": x, "y": y, "ancho": w, "alto": h
        }
    }
    
    # 7. Guardamos el archivo JSON simulando la salida MQTT
    nombre_archivo = "alerta_mqtt_payload.json"
    with open(nombre_archivo, "w") as archivo_json:
        json.dump(payload_alerta, archivo_json, indent=4)
        
    print(f"¡ALERTA! Hotspot detectado a {temp_max:.1f} C.")
    print(f"-> Telemetría guardada exitosamente en el archivo: {nombre_archivo}")

# 6. Etiquetado Automático (Dibujar las cajas)
for contorno in contornos:
    # Obtenemos las coordenadas y dimensiones de la caja que encierra la falla
    x, y, w, h = cv2.boundingRect(contorno)
    
    # Dibujamos un rectángulo verde fosforescente
    cv2.rectangle(imagen_termica, (x, y), (x+w, y+h), (0, 255, 0), 2)
    
    # Preparamos el texto de alerta con la temperatura máxima
    texto_alerta = f"ANOMALIA: {temp_max:.1f} C"
    
    # Imprimimos el texto justo arriba de la caja
    cv2.putText(imagen_termica, texto_alerta, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    
    # Simulamos el envío de telemetría por consola
    print(f"¡ALERTA! Hotspot detectado en coordenadas de imagen (X:{x}, Y:{y}) con temperatura de {temp_max:.1f} C")

# --- FIN DE LA IA ---

# 7. Mostramos el resultado final
cv2.imshow("Sistema Autonomo de Deteccion", imagen_termica)
cv2.waitKey(0)
cv2.destroyAllWindows()
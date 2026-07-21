import numpy as np
import cv2

# 1. Simulación de la Matriz del MLX90640 (Igual que antes)
matriz_termica = np.random.uniform(low=30.0, high=35.0, size=(24, 32))
matriz_termica[5:8, 22:25] = 70.0 # Nuestro Hotspot inyectado

# 2. Normalización e Interpolación (La base visual)
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
	1. Creamos un simulador termico para comenzar a dar vida a la vision digital del proyecto.
-Se simula una matriz la cual va a ser reemplazada por el visor de temperatura. Esta matriz presenta 32x34 pixeles 
tilizando numpy.
-Estableciendo temperaturas aleatorias entre 30 y 35 ºC para simular un panel solar con temperatura estable
y se inyecta un hotspot de 70ºC en un sector especifico para comprobar la deteccion del sistema.
	2. Los rangos de temperatura se normalizan a un rango de 0 a 255 (8b) para poder trabajar con OpenCV.
Para arreglar la baja resolucion nativa del sensor de 
(768px) se aplica una interpolacion bicubica que lo escala 
a una resolucion de 640x480. Posteriormente se aplica un mapa de color (INFERNO), para una representacion
adecuada de las temperaturas tomadas, facilitando la visualizacion de las mismas.
	3.Se creo la logica del umbral dinamico.
En lugar de usar el calor de temperatura fijo para alertar sobre fallas, el algoritmo calcula la
temperatura mediana de toda la matriz. El umbral de falla se define dinamicamente sumando
una constante de toleracncia en este caso 15 grados a la mediana.
	T(umbral)= T(mediana)+15º
	4.Binatizacion y aislamiento de la falla
Se crea una mascara binaria evaluando los pixeles de la matriz que superan la T(umbral), 
los pixeles anomalos toman el valor max 255, y el resto se descarta. Esta misma mascara se interpola
para evitar la difuminacion de los bordes y mantener la precision del area afectada.
	5.Extracion de contronos y telemetria
Se usa la funcion findCountors de OpenCv, el sistema identifica geometricamente las 
anomalias de la mascara bianria, se calcula el rectanfulo delimitador (bounding box) alrededor 
del area detectada, dibujando un rectangulo extrayendo las cordenadas de la imagen y el valor termico
preparando todo para el envio de datos.
	6.Mandamos un mensaje json.
recorremos todos los contornos de la matriz en busqueda de anomalias.

----------------------------------------------------------------------------------------------------

Pasamos a una nueva version del simulador de manera mas estructurada
En esta fase del desarrollo, el prototipo evolucionó de un script 
de ejecución secuencial a una arquitectura de software modular,
preparando el sistema para su implementación nativa en el hardware (Raspberry Pi) y 
su integración con redes IoT (Internet de las Cosas). 
Los avances implementados se dividen en dos pilares fundamentales:

	1. Refactorización y Separación de Responsabilidades
Módulo de Adquisición: Aísla la interacción con el sensor. 
(Actualmente simula la matriz; a futuro leerá el bus I2C 
del sensor MLX90640 físico sin afectar el resto del programa).

Módulo de Procesamiento Visual: Dedicado estrictamente a 
la normalización matricial y la interpolación bicúbica.

Módulo de Inteligencia (Edge AI): Contiene la lógica del 
umbral dinámico para la extracción matemática de las anomalías térmicas.

Módulo de Telemetría: Gestiona el almacenamiento y transmisión de las alertas.

	2. Estructuración de Telemetría (Carga Útil JSON)
Marca de tiempo (Timestamp): Generada en formato ISO 8601 para un registro cronológico exacto.

Métricas térmicas: Registro de la temperatura máxima anómala, la mediana 
térmica del panel y el umbral estadístico que disparó la alerta.

Datos espaciales (Visión Artificial): Coordenadas relativas (X, Y) y dimensiones
 del área afectada dentro de la matriz, preparando el sistema para su futura 
correlación con la telemetría GPS del dron.

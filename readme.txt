	1. Creamos un simulador termico para comenzar a dar vida a la vision digital del proyecto.
-Se simula una matriz la cual va a ser reemplazada por el visor de temperatura. Esta matriz presenta 32x34 pixeles utilizando numpy.
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



# Arquitectura v0.2

La app tiene un cliente estático y un puente local opcional. `sim.js` implementa el mundo, movimiento, rayos y dinámica angular; `workshop.js` contiene cálculos de masa y generación de STL; `app.js` conecta entradas, visualización y exportación.

La simulación no conecta a motores. El servidor local Python expone un puente de lectura macOS y caché de adaptadores; cámara, audio y ubicación funcionan mediante APIs del navegador con permiso. El almacenamiento local solo recuerda el tema. Sesiones y modelos se descargan por acción del usuario.

El futuro robot separará Raspberry Pi (interfaz, video y registro) del MCU (IMU, encoders y control). Esa arquitectura aún no está implementada. El documento original conserva las decisiones conceptuales y los gates físicos.

## Limitaciones numéricas

Integrador Euler semiimplícito con paso 0.02 s. La gravedad linealizada usa un coeficiente ilustrativo de 10, sin identificación física. Se limita la integral a ±0.5 y la salida a ±20. El movimiento del mapa no está acoplado a la masa, el radio ni el par; no usar resultados para dimensionar actuadores.

La suma estática de momentos verticales del taller permite explorar una ubicación de contrapeso. Para optimizar estabilidad se necesitan posiciones 3D, tensor de inercia, fricción, masa de ruedas, motores, retardos y modelo acoplado. El momento angular no es una media: depende de inercia y velocidad angular. Un filtro de media reduce ruido a costa de retardo; esta versión no implementa fusión IMU.

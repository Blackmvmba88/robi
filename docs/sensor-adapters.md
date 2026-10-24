# Base de sensores externos

La app detecta hardware de la Mac y ofrece una interfaz común para añadir sensores externos. No existe un protocolo universal: I²C, SPI y UART requieren un puente y configuración adecuados. No conectar directamente señales eléctricas a un puerto USB.

## Contrato JSONL v1

Un objeto JSON por línea, máximo 8192 bytes. Ejemplo **sintético de formato**, no una lectura real:

```json
{"schema":"sentinel.sensor.v1","sensor_id":"ambient-01","model":"modelo-a-definir","metrics":[{"name":"temperature","value":24.5,"unit":"degC"},{"name":"humidity","value":45,"unit":"percent"}]}
```

Identificador estable y nombres de métricas de hasta 64 caracteres ASCII (`A-Z a-z 0-9 _ . -`); entre 1 y 32 métricas, valores numéricos finitos, unidad explícita hasta 24 caracteres, modelo hasta 120. No se ejecuta código recibido. El colector añade hora de recepción y transporte, no confía en la hora del dispositivo.

Un Arduino/ESP32 puede traducir el protocolo del sensor a este contrato. GPS externo puede emitir latitude/longitude en deg, accuracy en m; IMU puede emitir acceleration_x en m/s^2, angular_rate_z en rad/s. Las unidades no se convierten automáticamente. No mezclar ángulos Euler ni convenciones de eje sin documentarlos.

## Captura opcional por puerto serie

Identifica el puerto en el panel de la Mac. Después ejecuta desde el proyecto, reemplazando el puerto por el de tu dispositivo:

```sh
python3 local/collect.py --port /dev/cu.usbmodemTU_DISPOSITIVO --baud 115200
```

Soporta macOS/POSIX, 8N1, sin comandos salientes. Abrir el puerto puede reiniciar ciertas placas; no abrir dispositivos ajenos o en uso por otra aplicación. La captura se inicia únicamente con este comando. Ctrl+C restaura la configuración serie.

Para otro programa que traduzca datos a JSONL:

```sh
python3 mi_adaptador.py | python3 local/collect.py --stdin
```

El colector conserva la última muestra de hasta 64 sensores en `local/runtime/sensors.json` (ignorado por Git). La app local lee `/api/external-sensors`, muestra unidades y marca muestras de más de 5 s como caducadas. No controla el robot ni publica datos. No ejecutar varios colectores a la vez en esta primera versión.

## Extender

Implementa `SensorAdapter.read()` para devolver `normalize(payload)` o `None` sin inventar datos. La clase base y el parser JSONL están en `local/adapters/`. Un nuevo adaptador necesita documentar modelo, transporte, unidades, frecuencia, calibración, ejes y errores esperados. La frecuencia real y la detección de desconexión dependen del dispositivo; no están declaradas por el contrato v1. Se puede conservar metadatos de calibración en una futura versión de contrato.

## Sensores de la Mac

- Temperaturas IOHID: lectura experimental, interna, sin root. La disponibilidad cambia según equipo/macOS; no se etiquetan automáticamente como temperatura ambiente o CPU.
- Micrófono: nivel RMS/dBFS sin calibración acústica, sin grabación ni subida.
- Cámara: vista local solo tras permiso, no profundidad ni reconocimiento real.
- Ubicación: navegador/macOS y sus servicios; no confirma GPS físico, precisión reportada por sistema. No se registra ni exporta.
- Movimiento: escucha eventos del navegador; si no hay eventos válidos se informa sin datos.
- Mando: lectura de ejes, activación explícita para conducir el juego.
- Inventario audio/USB/serie: detección de conexión; no implica interpretación de sus datos.

El puente HTTP escucha únicamente en 127.0.0.1, verifica Host/Origin y no permite CORS. La versión alojada no llama a localhost; solo ofrece capacidades del navegador, y explica que el puente está ausente. Los datos locales no se incorporan a commits ni despliegues.

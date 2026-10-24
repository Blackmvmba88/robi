# BLACKMAMBA SENTINEL B-01 · Virtual Lab

Un laboratorio jugable para explorar un robot de dos ruedas antes de construirlo.

**Versión 0.2.0: app web implementada; hardware conceptual, no construido ni validado.**

## Jugar y experimentar

Desde esta carpeta:

```sh
npm start
```

Abre http://localhost:8080. No requiere instalar dependencias ni credenciales; requiere Python 3 para servir archivos. La app funciona en un navegador moderno. Las fuentes web son opcionales y tienen respaldo local.

1. Pulsa **Iniciar misión**.
2. Conduce con WASD, flechas o botones táctiles. Visita las tres balizas.
3. Cambia entre ToF, LiDAR, ultrasonido y cámara de profundidad idealizada; modifica el ruido.
4. Inyecta perturbaciones, corta el enlace o usa el paro virtual (Espacio).
5. Ajusta Kp, Ki y Kd. Observa inclinación, velocidad angular, integral y salida limitada.
6. Exporta la sesión JSON con muestras sintéticas, estados y trayectoria.

Cuatro temas: Oscuro, Plata, Morado y Océano. La preferencia se guarda en el navegador.

## Taller de impresión y contrapesos

Tres presets de **placa**: Compact, Explorer y Cargo. Ajusta ancho, fondo, espesor y material para descargar una placa rectangular sólida STL en milímetros. Es una pieza conceptual cerrada de 12 triángulos, sin perforaciones ni soportes. **No es un robot completo listo para imprimir.**

El taller calcula volumen y masa sólida con densidades nominales; el laminador, relleno, paredes, soportes y pieza real darán otra masa. Introduce masa y centro del conjunto restante, altura de placa, centro objetivo y ubicación del contrapeso.

```text
masa_placa = ancho × fondo × espesor × densidad / 1000
centro = Σ(masa × altura) / Σ(masa)
contrapeso = masa_total × (centro_actual - centro_objetivo)
             / (centro_objetivo - altura_contrapeso)
```

Las masas se expresan en g y las alturas en mm respecto del eje. Un resultado negativo o denominador cero se marca como objetivo no alcanzable en esa ubicación. Este balance es vertical y estático: no estima resistencia, par motor, estabilidad dinámica, reparto lateral ni inercia completa. El centro objetivo positivo no garantiza estabilidad. Más contrapeso también aumenta las exigencias al actuador.

## Alcance de la simulación

- Mapa cenital 2D de 12 × 12 unidades interpretadas como metros; obstáculos circulares, sensores de rayos y ruido uniforme.
- La cámara es un abanico de distancias, sin imágenes ni reconocimiento.
- Modelo angular educativo: `theta'' = 10 theta + u + 0.4 referencia`, con `u = -Kp theta + Ki integral - Kd theta_dot`, integral y salida limitadas.
- Integración fija a 50 Hz con tiempo de cuadro acotado; no es un lazo embebido de tiempo real.
- Traslación simplificada independiente del modelo angular; la configuración de masas **no cambia la dinámica del juego**.
- Paro inmediato del juego, batería sintética y detección de fallo por ángulo. No reproduce la caída física al cortar motores.
- Sin UART, motores, sensores reales, video, IA, navegación autónoma ni firmware funcional.
- Ganancias de simulación adimensionales: no trasladarlas a un robot real.

## Estructura

```text
dist/                       App estática, simulación y taller
shared/protocol/             Borrador de contrato, sin transporte implementado
docs/concepto-original.md    Documento original proporcionado
docs/architecture.md        Arquitectura actual y evolución
docs/test-plan.md           Verificación y gates físicos pendientes
hardware/bom/               Datos requeridos antes de seleccionar hardware
firmware/balance-controller/ Estado y próximos pasos del MCU
raspberry/teleop/            Estado y próximos pasos de la pasarela
tests/                      Pruebas del modelo y cálculos
```

## Validar

Node.js 24 o compatible con el runner de pruebas incorporado:

```sh
npm test
```

Pruebas de movimiento desarmado, pérdida de enlace, paro/caída, rayos, sensores, puntuación, contrapesos, STL y respuesta PID. No sustituyen pruebas físicas.

## Siguiente etapa

- [x] App virtual, sensores intercambiables, misión y telemetría.
- [x] PID angular ajustable y fallos virtuales.
- [x] Estimación estática de masas y contrapeso; exportador de placa STL.
- [ ] Modelo físico acoplado con inercia, ruedas y saturación de par identificadas.
- [ ] CAD ensamblable con anclajes reales y cajetines de contrapesos.
- [ ] Selección de motores, encoders, IMU, batería y drivers con mediciones.
- [ ] Firmware MCU y pasarela Raspberry Pi con CRC, expiración y pruebas de fallo.
- [ ] Validación en banco y gates G0–G6 del concepto original.

El código de esta versión no tiene una licencia de reutilización explícita todavía.

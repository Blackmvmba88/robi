# Validación

## Automatizada

`npm test`: nueve pruebas de invariantes y respuesta del modelo. `node --check dist/app.js`: sintaxis del cliente.

## Navegador

Comprobar inicio, selección LiDAR, perturbación, corte de enlace, paro, reinicio y actualización de presupuesto de masas. Verificados por controles: temas Plata y Atardecer ámbar, pausa y persistencia de preferencias al recargar. La captura visual y viewport móvil requieren un navegador con esas capacidades habilitadas.

## Puente Mac y adaptadores

Cuatro pruebas Python de contrato: trama válida, valores inválidos/no finitos, esquema/duplicados y límites JSONL. Puente consultado por HTTP: temperaturas reales disponibles; Host/Origin externo rechazado con HTTP 403. Verificada lectura de temperaturas en la interfaz. No se abrió ningún puerto serie físico ni se activó captura de cámara/micrófono/ubicación durante QA.

La API de captura de pantalla no estuvo disponible; revisión visual por captura y matriz completa de viewports pendientes.

## Hardware

Ninguna prueba física realizada. Antes de fabricar: identificar componentes y masas reales, comprobar anclajes, analizar piezas impresas y validar en banco con soporte. Nunca transferir ganancias del juego al hardware. Aplican G0–G6 del concepto original; no se declara ninguno aprobado con esta app.

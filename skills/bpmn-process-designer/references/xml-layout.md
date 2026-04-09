# Reglas de Posicionamiento para XML BPMN 2.0

## 1. Ejes y Espaciado

| Regla | Valor |
|---|---|
| StartEvent — posición X inicial | X = 200 |
| Dirección del flujo | Izquierda → Derecha |
| Gap entre centros de elementos | 140 px |
| Altura fija por Lane | 180 px |
| Buffer entre Pools | ≥ 150 px |

**Incremento X**: si el elemento actual está en X y tiene ancho W, el siguiente empieza en X + W + 40 (margen), asegurando 140px entre centros.

## 2. Dimensiones estándar (dc:Bounds)

| Elemento | width | height |
|---|---|---|
| Task (cualquier tipo) | 100 | 80 |
| Start / End Event | 36 | 36 |
| Intermediate Event | 36 | 36 |
| Gateway | 50 | 50 |
| Sub-Process colapsado | 100 | 80 |
| Sub-Process expandido | variable | variable (múltiplo de 180) |
| Data Object | 36 | 50 |
| Annotation | variable | variable |

## 3. Posición vertical en Lane

Centrar verticalmente: `y_elemento = lane.y + (lane.height - elem.height) / 2`

Ejemplo: Lane en Y=100, altura 180, Task altura 80 → Task en Y = 100 + (180-80)/2 = 150.

## 4. Orden de Lanes (vertical)

- Arriba: roles de supervisión / negocio
- Abajo: roles operativos / sistemas

## 5. Puntos de anclaje para di:waypoint

### Tareas y Eventos
| Conexión | Punto |
|---|---|
| Entrada (input) | Cara izquierda: (x, y + height/2) |
| Salida (output) | Cara derecha: (x + width, y + height/2) |

### Gateways (50×50)
| Conexión | Punto |
|---|---|
| Entrada | Cara izquierda: (gw.x, gw.y + 25) |
| Salida 1 — camino principal | Cara derecha: (gw.x + 50, gw.y + 25) |
| Salida 2 — camino alternativo | Cara inferior: (gw.x + 25, gw.y + 50) |
| Salida 3 (si aplica) | Cara superior: (gw.x + 25, gw.y) |

## 6. Enrutamiento ortogonal

- **Prohibidas** las líneas diagonales.
- Si una conexión sale de la cara inferior de un gateway, bajar ≥ 40px antes de girar.
- **Cruce entre Lanes** — usar escalera ortogonal:
  ```
  (X1, Y1) → (X1+40, Y1) → (X1+40, Y2) → (X2, Y2)
  ```

## 7. Message Flow entre Pools

- Usar waypoints verticales limpios.
- Dejar buffer ≥ 150px de espacio vacío entre el Pool interno y el Pool externo.

## 8. Estructura del XML final

El archivo `.bpmn` debe incluir:
1. `bpmn:definitions` con namespaces correctos.
2. `bpmn:process` con toda la lógica: elementos, sequence flows, message flows.
3. `bpmndi:BPMNDiagram` con `BPMNPlane` conteniendo `BPMNShape` y `BPMNEdge` para cada elemento.
4. Código bien indentado, sin comentarios innecesarios, listo para importar en Camunda, Bizagi, Signavio, etc.

### Namespaces mínimos requeridos
```xml
xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
```

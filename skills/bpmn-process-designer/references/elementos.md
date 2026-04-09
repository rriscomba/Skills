# Taxonomía de Elementos BPMN 2.0

## §1 — Eventos

### Eventos de Inicio
| Tipo | Marcador | Cuándo usarlo |
|---|---|---|
| None (simple) | Círculo vacío | Inicio manual sin trigger específico |
| Message | Sobre | El proceso arranca al recibir un mensaje externo |
| Timer | Reloj | Arranca en fecha/hora fija o periódicamente |
| Conditional | Hoja con líneas | Arranca cuando se cumple una condición de negocio |
| Signal | Triángulo | Arranca ante una señal broadcast (puede activar varios procesos) |
| Multiple | Pentágono | Arranca si cualquiera de varios triggers ocurre |
| Parallel Multiple | Pentágono + | Arranca solo si TODOS los triggers ocurren simultáneamente |

### Eventos Intermedios (Catching — esperan que algo ocurra)
| Tipo | Modo | Cuándo usarlo |
|---|---|---|
| Message | Inline o Boundary | Espera un mensaje en mitad del flujo o desde una tarea |
| Timer | Inline o Boundary | Espera un tiempo antes de continuar o vence un plazo |
| Conditional | Inline o Boundary | Continúa cuando se cumple una condición |
| Error | Solo Boundary interrupting | Captura un error lanzado por una tarea o subproceso |
| Escalation | Boundary int. o non-int. | Captura una escalación lanzada desde subproceso |
| Cancel | Solo Boundary interrupting | Captura cancelación dentro de Transaction Sub-Process |
| Compensation | Boundary | Activa actividades de compensación cuando se deshace trabajo |
| Signal | Inline o Boundary | Captura señal broadcast |
| Event-Based Gateway + | Sigue a EBG | La primera rama que "dispara" gana; el resto se cancela |

### Eventos Intermedios (Throwing — el proceso lanza algo)
| Tipo | Cuándo usarlo |
|---|---|
| Message | El proceso envía un mensaje a otro participante |
| Escalation | El proceso escala a un nivel superior |
| Compensation | Activa proceso de compensación |
| Signal | Emite señal que puede activar múltiples procesos |
| Link | Conector dentro de la misma página (evitar spaghetti en diagramas grandes) |

### Eventos de Fin
| Tipo | Marcador | Cuándo usarlo |
|---|---|---|
| None (simple) | Círculo borde grueso | Fin sin efecto especial |
| Terminate | Círculo relleno | Cancela TODAS las actividades activas del proceso; usar con precaución |
| Message | Sobre relleno | El proceso termina enviando un mensaje |
| Error | Estrella rellena | Termina lanzando un error que debe capturarse |
| Escalation | Flecha rellena | Termina escalando a proceso padre |
| Cancel | X rellena | Solo dentro de Transaction Sub-Process; activa compensación |
| Compensation | Retroceso relleno | Termina activando compensación general |
| Signal | Triángulo relleno | Termina emitiendo señal broadcast |

### Boundary Events — Reglas de uso
- **Interrupting** (borde sólido): cancela la actividad base cuando se activa. Usar para timeouts, errores, cancelaciones.
- **Non-interrupting** (borde punteado): la actividad base continúa en paralelo. Usar para escalaciones informativas, notificaciones.
- Un boundary event puede adjuntarse a: Task, Sub-Process, Call Activity.
- No puede adjuntarse a: Gateways, Events.

---

## §2 — Tipos de Tarea

| Tipo | Marcador | Cuándo usarlo |
|---|---|---|
| Abstract Task | Sin marcador | Nivel descriptivo; tipo no definido aún |
| User Task | Silueta persona | Persona trabaja apoyada en interfaz de sistema (formulario, pantalla) |
| Service Task | Engranaje | Automatización mediante API, web service o integración |
| Send Task | Sobre saliente | La tarea consiste en enviar un mensaje a participante externo |
| Receive Task | Sobre entrante | La tarea espera recibir un mensaje de participante externo |
| Manual Task | Mano | Trabajo completamente manual, sin sistema de información |
| Script Task | Rollo | Ejecuta script o código interno automáticamente |
| Business Rule Task | Tabla | Invoca motor de reglas de negocio externo |

**Nota**: para nivel descriptivo, usar Abstract Task. Para nivel analítico, especificar el tipo correcto.

---

## §3 — Gateways

### Selección de tipo
```
¿La decisión depende de UN EVENTO que ocurra primero?
  → Event-Based Gateway (EBG)
  → Solo puede tener Intermediate Events o Receive Tasks como salidas

¿Solo UNA ruta es válida (condiciones mutuamente excluyentes)?
  → Exclusive (XOR) Gateway
  → Etiquetar cada arco de salida con su condición
  → Incluir condición "else" o "default" para cubrir todos los casos

¿TODAS las rutas se activan siempre en paralelo?
  → Parallel (AND) Gateway
  → OBLIGATORIO: gateway de convergencia AND emparejado antes de continuar

¿UNA O MÁS rutas pueden activarse según condiciones?
  → Inclusive (OR) Gateway
  → OBLIGATORIO: gateway de convergencia OR emparejado; espera todas las ramas activas
  → Etiquetar cada arco de salida con su condición

¿La lógica de enrutamiento es compleja y no encaja en ninguno de los anteriores?
  → Complex Gateway (último recurso; documentar la lógica en anotación)
```

### Regla de pareo — tabla resumen
| Gateway de split | Gateway de join obligatorio |
|---|---|
| Parallel (AND) split | Parallel (AND) join |
| Inclusive (OR) split | Inclusive (OR) join |
| Exclusive (XOR) split | XOR join si varias ramas convergen; puede omitirse si cada rama lleva a End Event propio |
| Event-Based | No requiere join propio; cada rama fluye hacia su propio camino |

**Error común**: omitir el join de un Parallel o Inclusive Gateway provoca que el proceso ejecute actividades posteriores N veces (una por cada rama activa).

---

## §3b — Conditional Sequence Flow

El Conditional Sequence Flow **no es un Gateway**. Es una condición sobre un conector que controla si el flujo avanza o no desde una actividad hacia el siguiente elemento. Se representa con un mini-diamante al inicio del arco.

### Cuándo usarlo
- Sale desde una **actividad** (Task o Sub-Process) y hay un único arco condicional opcional.
- La condición es verdad → el token avanza. Es falsa → el token no pasa.

### Cuándo NO usarlo
| Situación | Por qué no | Alternativa |
|---|---|---|
| Dos o más caminos salen de la misma actividad | Es una bifurcación real, no una condición opcional | Gateway XOR o OR según corresponda |
| Sale desde un Evento | Los eventos no admiten condición de salida | Usar Event-Based Gateway o Conditional Event |
| Sale desde Gateway Parallel, Event-Based o Complex | Estas gateways no admiten condición en sus salidas | Rediseñar con el gateway correcto |

### Regla de selección: Gateway vs. Conditional Sequence Flow
```
¿Hay DOS O MÁS caminos alternativos o paralelos saliendo de un punto?
  → Gateway (siempre)

¿Hay UN SOLO arco saliendo de una actividad que puede o no ejecutarse?
  → Conditional Sequence Flow (mini-diamante)

¿Hay VARIOS arcos con mini-diamante saliendo de la misma actividad?
  → ANTI-PATRÓN A8 — reemplazar por Gateway XOR o OR
```

---

## §4 — Subprocesos

| Tipo | Cuándo usarlo |
|---|---|
| Embedded Sub-Process (expandido) | Lógica interna visible en el mismo diagrama; comparte contexto con proceso padre |
| Collapsed Sub-Process | Simplifica el diagrama; detalle en diagrama separado |
| Call Activity | Lógica reutilizable en múltiples procesos; independiente del proceso padre |
| Transaction Sub-Process | Grupo de actividades todo-o-nada; soporte para compensación, cancelación y error |
| Event Sub-Process | Sub-proceso activado por un evento; puede ser interrupting o non-interrupting; no tiene Start Event de flujo |

### Transaction Sub-Process — protocolo
Tres resultados posibles de una transacción:
1. **Éxito**: flujo normal continúa.
2. **Cancelación**: se activa Cancel End Event dentro → Cancel Boundary Event en el sub-proceso → flujo de excepción en proceso padre.
3. **Error**: Error End Event dentro → Error Boundary Event → flujo de excepción.

Para cancelación, cada actividad que puede necesitar deshacerse debe tener un **Compensation Boundary Event** con su **Compensation Activity** asociada.

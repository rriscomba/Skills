# Taxonomía de Elementos BPMN 2.0
## Versión 2.0 — Referencia técnica completa

---

## §1 — Eventos

### Eventos de Inicio (línea de borde delgada)
Solo pueden *atrapar* (Catch) un detonante o ser un inicio indefinido.

| Tipo | Marcador | Cuándo usarlo |
|---|---|---|
| None (simple) | Círculo vacío | Inicio manual o sin trigger específico conocido |
| Message | Sobre | El proceso arranca al recibir un mensaje externo (cliente envía formulario, sistema notifica) |
| Timer | Reloj | Arranca en fecha/hora fija o periódicamente ("Todos los viernes a las 5 PM", "El 1 de cada mes") |
| Conditional | Hoja con líneas | Arranca cuando se cumple una condición de negocio |
| Signal | Triángulo | Arranca ante una señal broadcast (puede activar varios procesos simultáneamente) |
| Multiple | Pentágono | Arranca si cualquiera de varios triggers ocurre (OR lógico) |
| Parallel Multiple | Pentágono + | Arranca solo si TODOS los triggers ocurren simultáneamente (AND lógico) |

### Eventos Intermedios (línea de borde doble)
Pueden ser *Atrapadores* (Catch — esperan que algo ocurra) o *Lanzadores* (Throw — generan el evento).

#### Catching — inline en el flujo
| Tipo | Cuándo usarlo |
|---|---|
| Message | Espera un mensaje asíncrono en mitad del flujo. **NUNCA usar una tarea para "esperar".** |
| Timer | Espera un tiempo antes de continuar ("esperar 24 horas"). **NUNCA usar una tarea para "esperar".** |
| Conditional | Continúa cuando se cumple una condición de negocio evaluada periódicamente |
| Signal | Espera señal broadcast de otro proceso |
| Link (Catch) | Receptor de un Link Throw en la misma página. Par obligatorio con Link Throw. |

#### Catching — Boundary (pegados al borde de Task o Sub-Process)
| Tipo | Modo | Cuándo usarlo |
|---|---|---|
| Timer | **Interrupting** (borde sólido) | Timeout que cancela la tarea. Ej: "Si pasan 48h, cancelar la orden." |
| Timer | **Non-interrupting** (borde punteado) | Timeout que notifica sin cancelar. Ej: "Si pasan 24h sin respuesta, enviar recordatorio y seguir esperando." |
| Error | Solo Interrupting | Captura error técnico lanzado por una tarea automática |
| Escalation | Interrupting o Non-interrupting | Captura escalación lanzada desde subproceso |
| Cancel | Solo Interrupting | Captura cancelación dentro de Transaction Sub-Process |
| Compensation | Boundary | Activa actividades de compensación cuando se deshace trabajo |
| Message | Interrupting o Non-interrupting | Captura mensaje externo mientras la tarea está activa |
| Signal | Interrupting o Non-interrupting | Captura señal broadcast mientras la tarea está activa |

> **Regla crítica Boundary Events**:
> - **Interrupting** (borde sólido continuo): cancela la actividad base inmediatamente → el token toma la ruta de excepción. Usar para timeouts que abortan, errores críticos, cancelaciones formales.
> - **Non-interrupting** (borde punteado): la actividad original continúa en paralelo → se dispara un flujo adicional. Usar para recordatorios, notificaciones informativas, escalaciones no bloqueantes.
> - Solo pueden adjuntarse a: Task, Sub-Process, Call Activity. **No** a Gateways ni Events.

#### Throwing — inline en el flujo
| Tipo | Cuándo usarlo |
|---|---|
| Message | El proceso envía un mensaje a otro participante en mitad del flujo |
| Escalation | El proceso escala a un nivel superior |
| Compensation | Activa proceso de compensación |
| Signal | Emite señal broadcast que puede activar múltiples procesos |
| Link (Throw) | Conector hacia otra parte del mismo diagrama para evitar "código espagueti". Par obligatorio con Link Catch. Equivalente a "continúa en la página 2". |

> **Link Events — regla de uso**:
> Usar para conectar dos partes distantes de un diagrama en la misma página (o entre páginas del mismo proceso). Se modelan en pares: **Link Throw** (emisor) + **Link Catch** (receptor) con el mismo nombre. No pueden cruzar pools.

### Eventos de Fin (línea de borde gruesa)

| Tipo | Marcador | Cuándo usarlo |
|---|---|---|
| None (simple) | Círculo borde grueso | Fin sin efecto especial. **Termina solo el token de ese camino; otros tokens paralelos siguen activos.** |
| **Terminate** | Círculo relleno | **Aniquila TODOS los tokens activos de la instancia.** Usar cuando un fallo o condición exige abortar el proceso completo. Usar con máxima precaución en procesos con flujos paralelos. |
| Message | Sobre relleno | El proceso termina enviando un mensaje a un participante externo |
| Error | Estrella rellena | Termina lanzando un error que debe capturarse en un nivel superior |
| Escalation | Flecha rellena | Termina escalando a proceso padre |
| Cancel | X rellena | Solo dentro de Transaction Sub-Process; activa la compensación |
| Compensation | Retroceso relleno | Termina activando compensación general |
| Signal | Triángulo relleno | Termina emitiendo señal broadcast |

> **Distinción crítica None vs. Terminate**:
> - **End None**: si hay 3 flujos paralelos activos y uno llega a End None, los otros 2 continúan. El proceso sigue vivo.
> - **End Terminate**: si cualquier flujo llega a End Terminate, el proceso completo se cierra inmediatamente, sin importar cuántos tokens paralelos estén activos. Documentar siempre la justificación de su uso.

---

## §2 — Tipos de Tarea

| Tipo | Marcador | Cuándo usarlo | Criterio de selección |
|---|---|---|---|
| Abstract Task | Sin marcador | Nivel descriptivo; tipo no definido aún | Usar en modelos de alto nivel |
| User Task | Silueta persona | Persona interactúa con interfaz de sistema (formulario, pantalla ERP, aprobación en portal) | ¿Hay un humano que usa una interfaz? |
| Service Task | Engranaje | Automatización mediante API, web service o integración; el sistema actúa sin intervención humana | ¿El sistema actúa solo, invisible para el usuario? |
| Send Task | Sobre saliente | La tarea consiste **exclusivamente** en enviar un mensaje a un participante externo; el motor BPMS lo contabiliza como trabajo cuantificable | Preferir sobre Throw Message Event cuando el envío implica trabajo registrable |
| Receive Task | Sobre entrante | La tarea consiste **exclusivamente** en esperar un mensaje de un participante externo; el motor lo contabiliza como trabajo cuantificable | Preferir sobre Catch Message Event cuando la espera implica trabajo registrable |
| Manual Task | Mano | Trabajo físico completamente manual, sin sistema de información rastreable (cargar cajas, instalar cableado) | ¿Es trabajo físico sin sistema? |
| Script Task | Rollo | Ejecuta script o código interno automáticamente (Python, Groovy, JS dentro del motor BPMS) | ¿Es código interno del motor? |
| Business Rule Task | Tabla | **Invoca un motor de reglas externo (BRMS/DMN)** para tomar una decisión compleja basada en parámetros, antes de llegar a un gateway | ¿La decisión requiere un motor de reglas separado? |

> **Send/Receive Task vs. Message Event — criterio de selección**:
> - Usar **Send/Receive Task** cuando el BPMS debe registrar el envío/recepción como *trabajo cuantificable y auditable* (tiene duración, responsable, trazabilidad de SLA).
> - Usar **Evento de Mensaje** (Throw/Catch) cuando es solo un trigger o notificación sin "trabajo" asociado, o cuando la semántica es puramente de señalización entre participantes.

> **Business Rule Task — contrato técnico**:
> No toma la decisión por sí misma. Su función es alimentar datos al gateway siguiente con la evaluación del motor de reglas. El flujo es: Business Rule Task → datos evaluados → XOR Gateway que enruta según el resultado.

> **Lanes para sistemas**: los carriles representan a quienes **ejecutan** el trabajo. No crear un lane para "Base de Datos" o "ERP". Si el sistema es usado por un humano → User Task en el lane del humano. Si el sistema actúa solo → Service Task en el lane del área responsable. Si el sistema es externo → Pool separado (black-box).

---

## §3 — Gateways (Compuertas)

Las compuertas **no toman decisiones**: solo enrutan los tokens según condiciones o eventos.

### Regla de Pureza (Split/Join Purity) — OBLIGATORIA

Una compuerta realiza **una sola función**:
- **Diverging (split)**: exactamente 1 entrada, múltiples salidas.
- **Converging (join)**: múltiples entradas, exactamente 1 salida.

**Prohibido**: una compuerta con múltiples entradas Y múltiples salidas al mismo tiempo. Si el flujo lo requiere, usar dos compuertas en secuencia (join → split).

En XML: cada gateway debe declarar `gatewayDirection="Diverging"` o `gatewayDirection="Converging"` explícitamente.

### Selección de tipo

```
¿La decisión depende de UN EVENTO que ocurra primero (no de datos)?
  → Event-Based Gateway (hexágono interior)
  → Solo puede tener Intermediate Events o Receive Tasks como salidas
  → Variante instanciadora exclusiva (Start EBG): inicia el proceso cuando ocurre 1 de N eventos posibles
  → Variante instanciadora paralela: inicia el proceso y arranca múltiples caminos a medida que suceden eventos

¿Solo UNA ruta es válida (condiciones mutuamente excluyentes)?
  → Exclusive Gateway (XOR — rombo vacío o con X)
  → Etiquetar cada arco de salida con su condición
  → OBLIGATORIO: incluir un arco "default" (barra diagonal) para el caso residual

¿TODAS las rutas se activan siempre en paralelo?
  → Parallel Gateway (AND — rombo con +)
  → OBLIGATORIO: gateway de convergencia AND emparejado antes de continuar
  → No admite condiciones en los arcos de salida

¿UNA O MÁS rutas pueden activarse según condiciones?
  → Inclusive Gateway (OR — rombo con O)
  → OBLIGATORIO: gateway de convergencia OR emparejado
  → Etiquetar cada arco de salida con su condición
  → OBLIGATORIO: incluir un arco "default" (barra diagonal)

¿La lógica de enrutamiento es rara y no encaja en ninguno de los anteriores?
  → Complex Gateway (asterisco) — último recurso
  → Documentar la lógica de activación en una anotación adjunta

¿Se divide el flujo y cada rama depende de qué evento ocurra primero?
  → Event-Based Gateway — las ramas son eventos intermedios o Receive Tasks
```

### Flujo por defecto (Default Flow) — OBLIGATORIO en XOR y OR

Toda compuerta XOR u OR debe tener exactamente **un arco de salida marcado como default**. Este arco se activa si ninguna otra condición evaluada es verdadera, evitando deadlocks por ausencia de ruta válida.

En XML:
```xml
<bpmn:exclusiveGateway id="GW_Validacion" name="¿Documentos válidos?" 
    gatewayDirection="Diverging" default="SF_Default">
  ...
</bpmn:exclusiveGateway>
<bpmn:sequenceFlow id="SF_Default" sourceRef="GW_Validacion" targetRef="Task_Rechazo"/>
<!-- El SF_Default NO lleva <conditionExpression> -->
```

### Regla de pareo — tabla resumen

| Gateway de split | Gateway de join obligatorio | Nota |
|---|---|---|
| Parallel (AND) split | Parallel (AND) join | Sin join: actividad posterior se ejecuta N veces |
| Inclusive (OR) split | Inclusive (OR) join | Sin join: no hay sincronización de tokens activos |
| Exclusive (XOR) split | XOR join explícito por defecto | Omitir solo si cada rama va a su propio End Event |
| Event-Based | No requiere join | Cada rama fluye a su propio camino |
| Complex | Complex join (del mismo tipo) | Documentar la regla de activación |

---

## §3b — Conditional Sequence Flow

El Conditional Sequence Flow **no es un Gateway**. Es una condición sobre un conector que controla si el flujo avanza o no desde una actividad. Se representa con un mini-diamante al inicio del arco.

### Cuándo usarlo
- Sale desde una **actividad** y hay un único arco condicional opcional.
- La condición es verdad → el token avanza. Es falsa → el token no pasa.

### Cuándo NO usarlo
| Situación | Por qué no | Alternativa |
|---|---|---|
| Dos o más caminos salen de la misma actividad | Es una bifurcación real | Gateway XOR o OR |
| Sale desde un Evento | Los eventos no admiten condición de salida | Event-Based Gateway o Conditional Event |
| Sale desde Gateway Parallel, Event-Based o Complex | Estas gateways no admiten condición en sus salidas | Rediseñar con el gateway correcto |
| Múltiples mini-diamantes salen de la misma actividad | Replica Gateway Inclusivo sin declararlo | Gateway XOR o OR explícito |

---

## §4 — Subprocesos

| Tipo | Borde | Cuándo usarlo |
|---|---|---|
| Embedded Sub-Process expandido | Sólido simple | Lógica interna visible en el mismo diagrama; comparte datos del proceso padre. Usar cuando el diagrama supera ~15 elementos o cuando un Boundary Event debe aplicarse a un grupo de tareas completo. |
| Collapsed Sub-Process | Sólido simple con +  | Simplifica el diagrama; los detalles se modelan en un diagrama separado. |
| **Call Activity** | **Borde muy grueso** | **Lógica genérica y reutilizable en múltiples procesos distintos de la empresa** (ej. "Verificación de Antecedentes", "Cobro con Tarjeta"). Invoca un proceso externo independiente. NO usar para lógica específica de un solo proceso. |
| Transaction Sub-Process | Doble borde | Grupo todo-o-nada con protocolo de compensación, cancelación y error. |
| **Event Sub-Process** | **Borde punteado** | **No tiene sequence flows de entrada ni de salida.** Se detona por un evento en cualquier momento del nivel donde habita. Usar para manejar excepciones globales sin repetir la condición en cada paso (ej. "Si en CUALQUIER momento el cliente cancela, ejecutar las tareas de cancelación"). |

### Event Sub-Process — Regla de Oro
- Se dibuja **dentro** del proceso o subproceso padre con borde punteado.
- **NO se conecta** al flujo normal mediante sequence flows.
- Se detona por un Start Event (Message, Timer, Error, Signal, etc.) cuando ese evento ocurre en cualquier punto del proceso padre.
- Puede ser **interrupting** (cancela el proceso padre) o **non-interrupting** (se ejecuta en paralelo).

### Call Activity — Criterio de selección
Usar **Call Activity** cuando:
1. La lógica del subproceso es **idéntica** en al menos 2 procesos distintos de la organización.
2. El subproceso tiene **vida propia** e independencia del proceso que lo invoca.
3. Se desea gestionar, versionar o gobernar el subproceso de forma centralizada.

No usar Call Activity cuando la lógica solo aplica a ese proceso. En ese caso, usar Sub-proceso embebido o colapsado.

### Transaction Sub-Process — protocolo
Tres resultados posibles:
1. **Éxito**: flujo normal continúa.
2. **Cancelación**: Cancel End Event dentro → Cancel Boundary Event en el sub-proceso → flujo de excepción en proceso padre.
3. **Error**: Error End Event dentro → Error Boundary Event → flujo de excepción.

Para cancelación, cada actividad que puede necesitar deshacerse debe tener un **Compensation Boundary Event** con su **Compensation Activity** asociada.

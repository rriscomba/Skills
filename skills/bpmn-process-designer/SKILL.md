---
name: bpmn-process-designer
description: >
  Analiza documentos de negocio y construye una especificación intermedia,
  rigurosa y validada de un proceso en BPMN 2.0 antes de generar notación XML.
  Úsala SIEMPRE que el usuario entregue procedimientos, manuales, políticas,
  narrativas operativas, casos de uso, instrucciones de trabajo, flujos o
  cualquier descripción de proceso que deba convertirse en un modelo BPMN
  correcto, claro, completo y consistente. También activa esta skill cuando
  el usuario pida identificar participantes, decisiones, excepciones, gateways
  o eventos en un documento, o quiera validar si un proceso está listo para
  diagramarse o convertirse a XML.
license: MIT
compatibility: markdown-skill
metadata:
  domain: business-process-modeling
  standard: BPMN 2.0
  language: es
  output_mode: structured-markdown
  reasoning_style: deterministic
  downstream_target: BPMN-XML
  references:
    - references/elementos.md
    - references/antipatrones.md
    - references/xml-layout.md
---

# BPMN Process Designer Skill
## Versión 2.0 — Method & Style + Interoperabilidad

## 1. Propósito

Convierte documentos narrativos o procedimentales en una **especificación intermedia BPMN 2.0**
que permita diseñar el proceso antes del XML, validar su lógica, detectar vacíos o
ambigüedades, y preparar una salida reutilizable para diagramado o serialización posterior.

Esta skill **NO genera XML de inmediato** salvo que se solicite después de completar y validar
la especificación, y el usuario haya aprobado explícitamente la arquitectura propuesta.

> **Archivos de referencia disponibles:**
> - `references/elementos.md` → taxonomía completa de eventos, tareas, gateways y subprocesos
> - `references/antipatrones.md` → catálogo de errores frecuentes y cómo detectarlos
> - `references/xml-layout.md` → reglas de posicionamiento para la capa visual del XML

---

## 2. Cuándo usar / no usar esta skill

**Activa** si el usuario:
- entrega documentos que describen un proceso o procedimiento;
- pide convertir narrativa de negocio en BPMN;
- quiere estructurar, validar o revisar procesos antes del XML;
- quiere identificar pools, lanes, tareas, eventos, gateways, mensajes o subprocesos;
- quiere comprobar si un proceso está listo para modelarse formalmente.

**No activa** si el usuario:
- solo pide una definición breve de BPMN;
- solo solicita una imagen o rediseño visual sin semántica de proceso;
- aporta una especificación formal completa y pide directamente el XML.

---

## 3. Principios obligatorios

1. **No inventar**: si un dato no está en la fuente, registrarlo en `Supuestos y Vacíos`.
2. **Pensar antes de diagramar**: primero lógica semántica, luego representación BPMN.
3. **Flujo continuo**: todo proceso recorre un camino sin cortes desde inicio hasta fin.
4. **Separar sequence flow de message flow**: nunca cruzar pools con sequence flow ni usar message flow dentro del mismo pool.
5. **Parear gateways divergentes con convergentes**: todo split (fork) necesita su join del mismo tipo (ver §7).
6. **Modelar más que el happy path**: incluir alternos y excepciones relevantes.
7. **Nombrar con precisión**: tareas = verbo+objeto; gateways = pregunta cerrada; eventos de fin = resultado de negocio; eventos = objeto + participio.
8. **Etiquetar el origen del dato**: `[FUENTE]` / `[INFERIDO]` / `[SUPUESTO]`.
9. **Distinguir Gateway de Conditional Sequence Flow**: cuando hay bifurcación real (dos o más caminos), siempre usar Gateway. Nunca reemplazar un Gateway por múltiples Conditional Sequence Flows saliendo de la misma actividad.
10. **Compuertas de convergencia obligatorias**: AND e OR siempre requieren gateway de merge explícito. XOR debe incluirlo por defecto salvo justificación documentada.
11. **Pureza de compuertas (Split/Join Purity)**: una compuerta SOLO diverge (split) O SOLO converge (join). Nunca recibe múltiples flechas entrantes y emite múltiples flechas salientes en el mismo rombo. Si se requiere ambas funciones, usar dos compuertas separadas.
12. **Happy path como línea recta visual**: el flujo principal de éxito debe avanzar de izquierda a derecha en línea continua. Las excepciones se desvían hacia abajo, se tratan, y terminan en un End Event independiente o retornan al flujo principal.
13. **Flujo por defecto obligatorio en XOR/OR**: toda compuerta XOR u OR debe tener exactamente un arco de salida marcado como *default flow* (barra diagonal en el conector) para cubrir el caso en que ninguna condición evaluada sea verdadera.
14. **Consultoría iterativa antes del XML**: la metodología de trabajo es en dos fases. La Fase 1 es obligatoria antes de generar cualquier XML.

---

## 4. Método de trabajo obligatorio — Dos Fases

### ─── FASE 1: Consultoría, Refinamiento y Aprobación ───

Ejecutar en este orden exacto. **No generar XML durante esta fase.**

#### Paso 0: Pre-análisis del documento fuente

Antes de modelar, caracterizar el documento:

| Criterio | Pregunta |
|---|---|
| Tipo de fuente | ¿Narrativa libre, procedimiento formal, política, caso de uso, manual técnico? |
| Completitud | ¿Describe inicio, actividades, decisiones y fin? ¿Falta algún tramo? |
| Actores | ¿Menciona personas, roles, sistemas, organizaciones? |
| Flujo lógico | ¿El orden de actividades es explícito o hay que inferirlo? |
| Excepciones | ¿Se mencionan errores, rechazos, tiempos vencidos, cancelaciones? |
| Nivel de detalle | ¿Descriptivo (alto nivel) o analítico (detalle implementable)? |

Según el nivel detectado:
- **Descriptivo**: usar subprocesos colapsados, eventos simples, gateways sin detalle técnico.
- **Analítico**: especificar tipos de tarea (User, Service, etc.), eventos con triggers exactos, criterios explícitos en gateways.

#### Paso 1: Objetivo y alcance del proceso
- ¿Qué logra el proceso?
- ¿Cuál es su disparador inicial y sus resultados posibles (éxito y excepción)?
- ¿Es proceso interno, colaboración B2B, vista abstracta o subproceso?

#### Paso 2: Identificar participantes
- **Pools**: entidades organizacionales independientes que se comunican por mensajes.
- **Lanes**: roles, áreas o sistemas dentro del mismo pool.
- **Actores externos abstractos**: si un participante externo solo envía/recibe mensajes sin lógica interna, representarlo como **black-box pool** (pool vacío sin actividades visibles).

#### Paso 3: Extraer y clasificar eventos

Para cada evento, consultar `references/elementos.md §1` y aplicar:

| Si el documento dice… | Tipo sugerido |
|---|---|
| "el proceso arranca cuando se recibe X" | Start Message |
| "el proceso arranca en un horario" | Start Timer |
| "el proceso arranca si se cumple condición Y" | Start Conditional |
| "notificar a Z al finalizar" | End Message |
| "cancelar todo si falla la transacción" | End Cancel / End Terminate |
| "el proceso termina sin más" | End None |
| "si termina un camino pero otros siguen activos" | End None (NO Terminate) |
| "si todo el proceso debe abortarse" | End Terminate |
| "si no responde en N días, escalar" | Intermediate Timer Boundary (non-interrupting) |
| "si no responde en N días, cancelar" | Intermediate Timer Boundary (interrupting) |
| "si ocurre error en integración, redirigir" | Intermediate Error Boundary (interrupting) |
| "si el cliente confirma antes de que venza el tiempo" | Event-Based Gateway |
| "esperar 24 horas" | Intermediate Timer Catching (inline) — NUNCA una tarea |
| "conectar partes distantes del diagrama" | Link Event (Throw + Catch) |

**Distinción crítica End None vs. End Terminate**:
- **End None**: termina solo el token de ese camino. Si hay otros tokens paralelos activos, éstos continúan. Usar cuando un ramal concluye pero el proceso principal puede seguir.
- **End Terminate**: aniquila inmediatamente todos los tokens activos de toda la instancia. Usar solo cuando un fallo o condición exige abortar el proceso completo. Usar con precaución en procesos con flujos paralelos.

#### Paso 4: Extraer y clasificar actividades

Para cada actividad, determinar:
- **Nombre**: Verbo + Objeto (ej. "Verificar identidad del cliente")
- **Tipo de tarea** (ver `references/elementos.md §2`):
  - `User Task` → persona trabaja con interfaz de sistema (formulario, pantalla ERP)
  - `Service Task` → sistema automatizado / API / web service sin intervención humana
  - `Send Task` → su función exclusiva es enviar un mensaje; el motor lo contabiliza como trabajo
  - `Receive Task` → su función exclusiva es esperar un mensaje; el motor lo contabiliza como trabajo. *Diferencia con Evento de Mensaje*: usar Send/Receive Task cuando el BPMS debe registrar el envío/recepción como trabajo cuantificable y auditable; usar Evento de Mensaje cuando es solo un trigger o notificación sin "trabajo" asociado.
  - `Script Task` → lógica automatizada interna (código Python, Groovy, JS dentro del motor)
  - `Manual Task` → trabajo físico completamente manual, sin sistema de información
  - `Business Rule Task` → invoca un motor de reglas externo (BRMS/DMN) para tomar una decisión compleja basada en parámetros antes de llegar a un gateway. No decide por sí misma; alimenta la compuerta siguiente.
- **Responsable**: lane o pool asignado
- **Entradas y salidas**: datos u objetos relevantes mencionados

#### Paso 5: Reconstruir el flujo principal (happy path)
- Ordenar actividades desde inicio hasta fin con sequence flow.
- El happy path debe ser una línea recta de izquierda a derecha. Las excepciones se ramifican hacia abajo.
- Verificar que cada actividad tiene al menos un arco de entrada y uno de salida.
- **Anti-patrón crítico**: actividad sin secuencia de entrada → Start Event implícito; sin salida → End Event implícito. Ambos deben ser explícitos.

#### Paso 6: Detectar decisiones y sincronizaciones — selección de gateway

Aplicar esta lógica de decisión:

```
¿La elección depende de un EVENTO (no de datos)?
  → Event-Based Gateway
  → Solo puede tener Intermediate Events o Receive Tasks como salidas
  → Variante instanciadora exclusiva: cuando el evento inicia el proceso (Start EBG)
  → Variante instanciadora paralela: cuando múltiples eventos en paralelo instancian el proceso

¿Solo UNA rama puede activarse?
  → Exclusive Gateway (XOR) — nombrar con pregunta, condición en cada salida
  → OBLIGATORIO: incluir un arco "default" (barra diagonal) para cubrir casos no previstos

¿TODAS las ramas se activan siempre?
  → Parallel Gateway (AND) — DEBE tener gateway de convergencia AND emparejado

¿UNA O MÁS ramas pueden activarse según condición?
  → Inclusive Gateway (OR) — DEBE tener gateway de convergencia OR emparejado
  → OBLIGATORIO: incluir un arco "default" (barra diagonal)

¿La lógica es compleja y no encaja en ninguno de los anteriores?
  → Complex Gateway (último recurso; justificar explícitamente con anotación)
```

**Regla de pureza (Split/Join Purity)**:
Una compuerta realiza UNA de estas dos funciones, nunca ambas simultáneamente:
- **Diverging (split)**: recibe un arco entrante, emite múltiples arcos salientes.
- **Converging (join)**: recibe múltiples arcos entrantes, emite un arco saliente.
Si el flujo requiere divergir y luego converger en el mismo punto, modelar dos compuertas separadas en secuencia.

**Regla de flujo por defecto (Default Flow)**:
Todo gateway XOR u OR debe tener exactamente un arco de salida marcado como *default*. Este arco se activa solo si ninguna otra condición es verdadera. En XML: atributo `default` en el gateway referenciando el ID del sequence flow por defecto, y ese sequence flow sin condición `<conditionExpression>`.

**Regla de pareo obligatoria**:
| Gateway split | Gateway join obligatorio |
|---|---|
| Parallel (AND) split | Parallel (AND) join |
| Inclusive (OR) split | Inclusive (OR) join |
| Exclusive (XOR) split | XOR join explícito por defecto |
| Event-Based | No requiere join; cada rama fluye a su propio camino |

**Reglas de convergencia**:

| Origen de los flujos convergentes | Compuerta de merging | Razón |
|---|---|---|
| Vienen de AND | **Obligatoria** — Parallel join | Sin join, la actividad siguiente se ejecuta N veces |
| Vienen de OR | **Obligatoria** — Inclusive join | Sin join, no hay sincronización de tokens activos |
| Vienen de XOR | **Por defecto: XOR join explícito.** Omitir solo con justificación documentada. | Degrada legibilidad y puede generar advertencias en motores |
| Fuentes distintas sin relación | **Obligatoria** — join correspondiente | Sin gateway, la semántica de convergencia es ambigua |

> **Regla prescriptiva de XOR merge — criterio por defecto:**
> Cuando dos o más sequence flows llegan a una misma actividad, modelar **siempre** un gateway
> de convergencia explícito del tipo correspondiente. Para flujos XOR, la omisión del merge
> debe ser la excepción documentada, no la práctica habitual. La justificación de omisión
> debe registrarse en la sección de Supuestos y Vacíos de la especificación.
> **Motivos para incluir siempre el XOR join:**
> 1. Legibilidad: el lector identifica de inmediato la convergencia intencional.
> 2. Compatibilidad: motores como Camunda 7 y Flowable emiten advertencias ante múltiples flujos entrantes sin gateway.
> 3. Auditoría ISO: el diagrama documenta explícitamente la lógica de control del flujo.
> 4. Mantenibilidad: si en el futuro se agrega un nuevo ramal, el join ya está modelado.

**Conditional Sequence Flow vs. Gateway — regla de selección**:

```
¿Hay DOS O MÁS caminos alternativos o paralelos saliendo de un punto?
  → Usar Gateway (compuerta) — siempre

¿La salida de una actividad puede o no continuar hacia el siguiente elemento
  según una condición, pero NO hay bifurcación real?
  → Usar Conditional Sequence Flow (mini-diamante en el conector)
  → Solo válido saliendo de: Actividades, Gateways Exclusivas e Inclusivas
  → NO válido saliendo de: Eventos, Gateways Paralelas, Basadas en Eventos, Complejas

¿Múltiples Conditional Sequence Flows salen de la misma actividad?
  → ANTI-PATRÓN: reemplazar por Gateway Exclusiva o Inclusiva según corresponda
```


#### Paso 7: Detectar colaboración y mensajería
- Message flow solo entre pools distintos.
- Registrar: emisor, receptor, nombre del mensaje, trigger, efecto esperado.
- Si el participante externo es una "caja negra", usar abstract pool sin contenido interno.

#### Paso 8: Detectar excepciones y caminos alternos

| Situación | Patrón BPMN |
|---|---|
| Tiempo vencido en tarea → cancelar | Boundary Timer Event **interrupting** (borde sólido) — cancela la tarea |
| Tiempo vencido en tarea → notificar sin cancelar | Boundary Timer Event **non-interrupting** (borde punteado) — la tarea sigue viva, se dispara flujo paralelo |
| Error en tarea automática | Boundary Error Event (interrupting) |
| Escalación desde subproceso | Boundary Escalation Event |
| Cancelar todo dentro de transacción | Boundary Cancel Event en Transaction Sub-Process |
| Deshacer tareas completadas por falla | Compensation Event + Compensation Activities |
| Rechazar y terminar | Exclusive Gateway + End Event con resultado claro |
| Reproceso | Loop o gateway con retorno al paso anterior |
| Cancelación global en cualquier punto del proceso | Event Sub-Process (borde punteado, no tiene sequence flow de entrada ni salida) |

**Boundary Events — criterio de selección**:
- **Interrupting** (borde sólido continuo): el evento cancela inmediatamente la actividad a la que está adjunto y redirige el token al flujo de excepción. Usar para timeouts que abortan, errores críticos.
- **Non-interrupting** (borde punteado): el evento dispara un flujo paralelo pero la actividad original continúa ejecutándose. Usar para recordatorios, notificaciones, escalaciones informativas.

#### Paso 9: Evaluar descomposición en subprocesos

| Tipo | Cuándo usarlo |
|---|---|
| Sub-proceso embebido (expandido) | Lógica interna visible; comparte contexto con proceso padre. Usar cuando el diagrama tiene más de 15 elementos o se necesita aplicar un Boundary Event a un grupo de tareas a la vez. |
| Sub-proceso colapsado | Simplifica visualmente; detalles en diagrama separado. |
| **Call Activity** (borde grueso marcado) | Cuando la lógica es **genérica y reutilizable en múltiples procesos distintos de la empresa** (ej. "Verificación de antecedentes", "Cobro con tarjeta"). Invoca un proceso externo independiente. No usar para lógica específica de un solo proceso. |
| Transaction Sub-Process | Grupo todo-o-nada; soporte para compensación, cancelación y error. |
| **Event Sub-Process** (borde punteado) | Se dibuja dentro del proceso pero **NO tiene sequence flows de entrada ni de salida**. Se detona por un evento (ej. cancelación por el cliente) en cualquier momento del nivel donde habita. Usar para manejar excepciones globales sin repetir la condición en cada tarea. |

#### Paso 10: Registrar datos y artefactos
- **Data Object**: documento, formulario, archivo, registro. Se conecta a tareas con *asociaciones* (línea punteada simple), nunca con sequence flow.
- **Data Store**: base de datos, repositorio persistente.
- **Annotation**: aclaración de reglas de negocio; no afecta el flujo.
- **Group**: agrupación visual para documentación.
- **Link Event**: usar para conectar partes distantes del mismo diagrama y evitar "código espagueti" (líneas que cruzan toda la página). Son equivalentes a "ir a la página 2". Se modelan como par: Link Throw + Link Catch.

> **Regla de artefactos**: los Data Objects se unen a las tareas mediante Asociaciones (línea punteada). NUNCA deben interferir la línea de sequence flow principal. No crear una "Tarea" cuya única función sea representar la existencia de un documento.

#### Paso 11: Validar — detectar anti-patrones

Consultar `references/antipatrones.md` y verificar explícitamente:

**Correctitud:**
- [ ] Toda actividad tiene secuencia de entrada Y de salida (no implícitas).
- [ ] No se usa message flow dentro del mismo pool.
- [ ] No se usa sequence flow entre pools distintos.
- [ ] Los gateways divergentes están emparejados correctamente con convergentes del mismo tipo.
- [ ] Flujos AND e OR tienen gateway de merging obligatorio — nunca conectados directamente a una actividad sin join.
- [ ] Toda actividad con dos o más sequence flows entrantes tiene un gateway de merge explícito. Si se omite para flujos XOR, la justificación está documentada en Supuestos y Vacíos.
- [ ] No hay múltiples Conditional Sequence Flows saliendo de la misma actividad (anti-patrón — debe ser Gateway).
- [ ] Conditional Sequence Flows solo salen de actividades o de Gateways Exclusivas/Inclusivas — nunca de eventos ni de Gateways Paralelas, Basadas en Eventos o Complejas.
- [ ] Los boundary events están asociados a la actividad correcta.
- [ ] No hay actividades aisladas sin justificación.
- [ ] Si hay lanes: existe `<bpmn:laneSet>` en el proceso con `<flowNodeRef>` para cada elemento.
- [ ] Cada pool black-box tiene un `<bpmn:process>` vacío referenciado por `processRef` en su `<bpmn:participant>`.
- [ ] Participantes de la misma organización modelados como Lanes, no como Pools separados (salvo justificación explícita).
- [ ] **PUREZA**: cada compuerta SOLO diverge O SOLO converge, nunca ambas simultáneamente.
- [ ] **DEFAULT FLOW**: toda compuerta XOR u OR tiene exactamente un arco de salida marcado como default.
- [ ] **END TERMINATE vs. END NONE**: el uso de End Terminate está justificado (aborta TODOS los tokens); en procesos paralelos se usó End None cuando solo termina un ramal.
- [ ] **EVENT SUB-PROCESS**: no tiene sequence flows de entrada ni de salida.
- [ ] **CALL ACTIVITY**: su uso está justificado porque la lógica es reutilizable en múltiples procesos.
- [ ] **LINK EVENTS**: aparecen en pares (Throw + Catch) y no cruzan pools.

**Claridad:**
- [ ] Nombres de tareas: verbo + objeto (no sustantivos vagos como "Proceso de aprobación").
- [ ] Gateways con pregunta explícita y condición etiquetada en cada arco de salida.
- [ ] Gateways de convergencia nombrados explícitamente cuando el contexto pueda prestarse a confusión.
- [ ] Eventos con trigger o resultado comprensible sin asumir contexto.
- [ ] Mensajes con nombre que indica contenido o propósito.
- [ ] Pools y lanes con nombre del rol/entidad, no de la acción.
- [ ] Lanes NO representan sistemas pasivos (BD, ERP): los sistemas pasivos son Service Tasks en el lane del actor que los usa, o un Pool externo.

**Completitud:**
- [ ] Happy path recorrible de inicio a fin.
- [ ] Alternos documentados en la fuente están representados.
- [ ] Excepciones documentadas en la fuente están representadas.
- [ ] Timeouts y condiciones temporales representados (Boundary Timer, no tareas de "esperar").
- [ ] Datos relevantes para entender decisiones mencionados.

**Consistencia:**
- [ ] Convenciones de nomenclatura uniformes en todo el modelo.
- [ ] Misma semántica para negocio e implementación.
- [ ] Coherencia entre proceso principal y subprocesos.
- [ ] Sin ambigüedades que permitirían interpretaciones distintas del flujo.

#### Paso 12: Formular preguntas aclaratorias (Fase 1 — cierre)

Después de la auditoría y antes de la aprobación, formular entre **1 y 3 preguntas críticas** que cierren los agujeros lógicos identificados. Priorizar preguntas sobre:
1. Límites del proceso (trigger y estados finales no definidos).
2. Actores con responsabilidad ambigua.
3. Reglas de negocio incompletas en gateways.

No avanzar a la Fase 2 hasta recibir respuesta o confirmación explícita del usuario.

#### Paso 13: Propuesta de arquitectura y llamado a la acción

Presentar:
- Lista de Pools, Lanes, Tareas (con tipo), Eventos y Gateways propuestos.
- Justificación del tipo elegido para cada elemento no obvio.
- Preguntas aclaratorias del Paso 12.
- Terminar con: *"Por favor, confirma si esta estructura es correcta o responde las preguntas. Una vez aprobado, procederé a generar la especificación formal y el XML."*

#### Paso 14: Emitir especificación estructurada

Ver §5 (Contrato de salida). Emitir solo tras aprobación del usuario.

---

### ─── FASE 2: Generación del Código BPMN 2.0 XML ───

**Trigger del usuario**: "Aprobado", "Genera el XML", o confirmación equivalente.

Esta fase se activa exclusivamente después de que el usuario apruebe la arquitectura de la Fase 1.

---

## 5. Contrato de salida obligatorio

Devolver SIEMPRE en este orden:

```
# Especificación Intermedia BPMN 2.0

## 1. Metadatos del proceso
- Nombre del proceso
- Objetivo
- Nivel de detalle: Descriptivo / Analítico
- Tipo de proceso: Interno / Colaboración / Abstracto / Subproceso
- Fuente documental
- Estado de madurez: Listo para diagramar / Listo con supuestos / No listo para XML

## 2. Participantes
### 2.1 Pools (nombre, tipo: interno / black-box)
### 2.2 Lanes (nombre, rol/área, pool al que pertenece)

## 3. Flow Objects
### 3.1 Eventos de inicio (nombre, tipo, trigger)
### 3.2 Actividades (nombre, tipo de tarea, lane, entradas, salidas)
### 3.3 Gateways (nombre/pregunta, tipo, gatewayDirection, condiciones en cada salida, default flow, gateway de convergencia emparejado)
### 3.4 Eventos intermedios (nombre, tipo, modo: boundary interrupting / non-interrupting / inline)
### 3.5 Eventos de fin (nombre, tipo, resultado de negocio, justificación si es Terminate)

## 4. Sequence Flow
### 4.1 Happy path (lista ordenada de pasos — de izquierda a derecha)
### 4.2 Flujos alternos
### 4.3 Flujos de excepción
### 4.4 Tabla formal de secuencia
| Desde | Hacia | Condición / Trigger | Default |
|---|---|---|---|

## 5. Message Flow
| Emisor | Receptor | Mensaje | Trigger | Efecto |
|---|---|---|---|---|

## 6. Datos y artefactos
- Data objects relevantes
- Data stores relevantes
- Link Events (pares Throw/Catch si aplica)
- Annotations necesarias

## 7. Reglas de negocio
| Regla | Punto del proceso | Impacto |
|---|---|---|

## 8. Subprocesos y reutilización
- Subprocesos propuestos (tipo: embebido / colapsado / transaccional / evento)
- Call activities propuestas (justificación de reutilización)
- Nivel de zoom recomendado por diagrama

## 9. Supuestos, ambigüedades y vacíos
| Tipo | Fragmento fuente | Explicación | Elemento BPMN afectado | Pregunta de aclaración |
|---|---|---|---|---|

## 10. Validación BPMN
### Correctitud: [lista de ítems verificados con ✓ o ✗ + comentario]
### Claridad: [idem]
### Completitud: [idem]
### Consistencia: [idem]

## 11. Estado final
- Listo para diagramar visualmente: Sí / No
- Listo para XML BPMN 2.0: Sí / No
- Anti-patrones detectados: [lista o "ninguno"]
- Riesgos pendientes: [lista o "ninguno"]
- Próximo paso recomendado:

## 12. Preguntas aclaratorias (máx. 3)
1. [Pregunta crítica sobre límite / actor / regla de negocio]
2. [...]
3. [...]
```

---

## 6. Reglas de estilo de salida

- Español claro y técnico.
- Listas estructuradas sobre párrafos largos.
- Distinguir siempre: `[FUENTE]` / `[INFERIDO]` / `[SUPUESTO]`.
- No mezclar recomendaciones con hechos documentados.
- Si algo falta en la fuente, marcarlo explícitamente; no inventar.

---

## 7. Criterio de cierre de Fase 1

La Fase 1 finaliza solo cuando:
1. se ha emitido la especificación completa;
2. se ha ejecutado la validación (Paso 11);
3. se han formulado las preguntas aclaratorias (Paso 12);
4. se ha declarado el estado final con respecto a XML;
5. el usuario ha confirmado la aprobación.

Si el proceso no está listo, indicar: qué falta, qué preguntas hacer, qué parte puede diagramarse y qué no debe serializarse aún.

---

## 8. Generación de XML — Fase 2

### Checklist pre-emisión XML (ejecutar antes de escribir el archivo)
- [ ] ¿El proceso tiene lanes? → declarar `laneSet` con todos los `flowNodeRef`
- [ ] ¿Hay pools externos? → declarar proceso vacío + `processRef`
- [ ] ¿Todos los participantes internos son lanes, no pools? → verificar decisión
- [ ] ¿Cada sequence flow tiene `sourceRef` y `targetRef` válidos?
- [ ] ¿Cada gateway divergente AND o OR tiene su join emparejado del mismo tipo?
- [ ] ¿Hay flujos paralelos o inclusivos confluyendo directamente en una actividad sin join? → corregir antes de serializar.
- [ ] ¿Hay actividades con dos o más sequence flows entrantes sin gateway de merge? → agregar XOR join explícito salvo justificación documentada.
- [ ] ¿Cada gateway tiene atributo `gatewayDirection="Diverging"` o `gatewayDirection="Converging"` explícito?
- [ ] ¿Toda compuerta XOR u OR tiene el atributo `default` apuntando al ID del sequence flow por defecto?
- [ ] ¿El End Terminate se usó solo donde se justificó abortar todos los tokens?
- [ ] ¿Los Data Objects están vinculados con `dataInputAssociation` / `dataOutputAssociation`, no con sequence flows?
- [ ] ¿Los Event Sub-Processes no tienen sequence flows de entrada ni de salida?
- [ ] ¿Cada Call Activity referencia correctamente el proceso global reutilizable?

Leer `references/xml-layout.md` para reglas de posicionamiento.

### Reglas semánticas de interoperabilidad

Namespaces mínimos requeridos:
```xml
xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
```

**Mandatorio para interoperabilidad (Bizagi, Camunda, Signavio)**:
- Cada gateway DEBE tener `gatewayDirection="Converging"` o `gatewayDirection="Diverging"` explícito.
- Los Data Objects se vinculan exclusivamente con `<bpmn:dataInputAssociation>` o `<bpmn:dataOutputAssociation>`.
- El `default` flow de XOR/OR: declarar en el gateway el atributo `default="ID_del_flow"` y en ese sequence flow NO incluir `<conditionExpression>`.
- Los IDs deben ser consistentes: los `sourceRef` y `targetRef` deben coincidir exactamente con los IDs de los elementos.

### Reglas estructurales obligatorias del modelo semántico

**Lanes**: si el proceso tiene lanes, OBLIGATORIO declarar `<bpmn:laneSet>` dentro de `<bpmn:process>` con un `<bpmn:lane>` por cada lane. Cada lane DEBE contener un `<bpmn:flowNodeRef>` por cada elemento que le pertenece. Sin esto, las herramientas ignoran los lanes aunque estén en el DI.

**Pools black-box**: todo participante externo (sin lógica interna modelada) DEBE declararse como `<bpmn:process id="Proc_X" isExecutable="false"/>` vacío Y referenciarlo con `processRef="Proc_X"` en su `<bpmn:participant>`. Sin `processRef`, la mayoría de herramientas descarta el pool.

**Pools internos vs. externos**: usar un Pool separado solo cuando la entidad es organizacionalmente independiente (proveedor, banco, cliente). Áreas o departamentos de la misma organización van como Lanes dentro del mismo Pool, aunque intercambien comunicaciones formales internas.

### Reglas para la capa visual (bpmndi:BPMNDiagram)

Leer `references/xml-layout.md`. Resumen:
- StartEvent: X=200; avanzar izquierda a derecha; gap entre elementos = 140px.
- Cada Lane: altura fija 180px; elementos centrados verticalmente.
- Task 100×80; Event 36×36; Gateway 50×50.
- Anclaje entrada: cara izquierda (x, y+h/2); salida: cara derecha (x+w, y+h/2).
- Gateways: entrada izquierda; salida 1 (happy path) derecha; salida 2 (excepción) inferior; salida 3 superior.
- Sin líneas diagonales; flujo ortogonal.
- Buffer mínimo 150px entre pools.
- Salida: XML bien indentado, listo para guardar como `.bpmn`.

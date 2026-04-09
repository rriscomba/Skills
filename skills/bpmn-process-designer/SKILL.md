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
---

# BPMN Process Designer Skill

## 1. Propósito

Convierte documentos narrativos o procedimentales en una **especificación intermedia BPMN 2.0**
que permita diseñar el proceso antes del XML, validar su lógica, detectar vacíos o
ambigüedades, y preparar una salida reutilizable para diagramado o serialización posterior.

Esta skill **NO genera XML de inmediato** salvo que se solicite después de completar y validar
la especificación.

> **Archivos de referencia disponibles:**
> - `references/elementos.md` → taxonomía completa de eventos, tareas y gateways con criterios de selección
> - `references/antipatrones.md` → catálogo de errores frecuentes y cómo detectarlos

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
7. **Nombrar con precisión**: tareas = verbo+objeto; gateways = pregunta; eventos de fin = resultado de negocio.
8. **Etiquetar el origen del dato**: `[FUENTE]` / `[INFERIDO]` / `[SUPUESTO]`.
9. **Distinguir Gateway de Conditional Sequence Flow**: una condición sobre un conector (mini-diamante) solo aplica saliendo de una actividad hacia un único camino opcional. Cuando hay bifurcación real (dos o más caminos), siempre usar Gateway. Nunca reemplazar un Gateway por múltiples Conditional Sequence Flows saliendo de una misma actividad.
10. **Compuertas de convergencia: obligatoriedad según tipo**: las compuertas de merging son obligatorias para flujos AND e OR. Para flujos XOR, la regla por defecto es **incluir siempre un XOR gateway de merge explícito** cuando dos o más sequence flows llegan al mismo elemento; omitirlo es la excepción y debe justificarse documentalmente. Conectar múltiples flujos paralelos o inclusivos directamente a una actividad sin gateway de convergencia es un anti-patrón que produce ejecuciones múltiples no intencionadas.

---

## 4. Método de trabajo obligatorio

Ejecutar en este orden exacto:

### Paso 0: Pre-análisis del documento fuente

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

### Paso 1: Objetivo y alcance del proceso
- ¿Qué logra el proceso?
- ¿Cuál es su disparador inicial y sus resultados posibles?
- ¿Es proceso interno, colaboración B2B, vista abstracta o subproceso?

### Paso 2: Identificar participantes
- **Pools**: entidades organizacionales independientes que se comunican por mensajes.
- **Lanes**: roles, áreas o sistemas dentro del mismo pool.
- **Actores externos abstractos**: si un participante externo solo envía/recibe mensajes y no necesita modelarse internamente, representarlo como **black-box pool** (pool vacío sin actividades visibles).

### Paso 3: Extraer y clasificar eventos

Para cada evento detectado en el documento, consultar `references/elementos.md §1` para seleccionar el tipo correcto. Pregunta clave:

| Si el documento dice… | Tipo sugerido |
|---|---|
| "el proceso arranca cuando se recibe X" | Start Message |
| "el proceso arranca en un horario" | Start Timer |
| "el proceso arranca si se cumple condición Y" | Start Conditional |
| "notificar a Z al finalizar" | End Message |
| "cancelar todo si falla la transacción" | End Cancel |
| "el proceso termina sin más" | End None / Terminate |
| "si no responde en N días, escalar" | Intermediate Timer (boundary interrupting) |
| "si ocurre error en integración, redirigir" | Intermediate Error (boundary) |
| "si el cliente confirma antes de que venza el tiempo" | Event-Based Gateway |

### Paso 4: Extraer y clasificar actividades

Para cada actividad, determinar:
- **Nombre**: Verbo + Objeto (ej. "Verificar identidad del cliente")
- **Tipo de tarea** (ver `references/elementos.md §2`):
  - `User Task` → persona trabaja con interfaz
  - `Service Task` → sistema automatizado / API
  - `Send / Receive Task` → envía o espera un mensaje externo
  - `Script Task` → lógica automatizada interna
  - `Manual Task` → trabajo manual sin sistema
  - `Business Rule Task` → decisión delegada a motor de reglas
- **Responsable**: lane o pool asignado
- **Entradas y salidas**: datos u objetos relevantes mencionados

### Paso 5: Reconstruir el flujo principal (happy path)
- Ordenar actividades desde inicio hasta fin con sequence flow.
- Verificar que cada actividad tiene al menos un arco de entrada y uno de salida.
- **Anti-patrón crítico**: actividad sin secuencia de entrada implica Start Event implícito; actividad sin secuencia de salida implica End Event implícito. Ambos deben ser explícitos.

### Paso 6: Detectar decisiones y sincronizaciones — selección de gateway

Aplicar esta lógica de decisión:

```
¿La elección depende de un EVENTO (no de datos)?
  → Event-Based Gateway

¿Solo UNA rama puede activarse?
  → Exclusive Gateway (XOR) — nombrar con pregunta, condición en cada salida

¿TODAS las ramas se activan siempre?
  → Parallel Gateway (AND) — DEBE tener gateway de convergencia emparejado

¿UNA O MÁS ramas pueden activarse según condición?
  → Inclusive Gateway (OR) — DEBE tener gateway de convergencia emparejado

¿La lógica es compleja y no encaja en ninguno de los anteriores?
  → Complex Gateway (último recurso; justificar explícitamente)
```

**Regla de pareo obligatoria**:
- Parallel split → Parallel join
- Inclusive split → Inclusive join
- Exclusive split → **XOR join explícito por defecto** (ver tabla de convergencia abajo)

**Reglas de convergencia (merging) — obligatoriedad**:

| Origen de los flujos convergentes | Compuerta de merging | Razón |
|---|---|---|
| Vienen de una AND (todos ocurrieron en paralelo) | **Obligatoria** — Parallel join | Sin join, la actividad siguiente se ejecuta N veces |
| Vienen de una OR (uno o más ocurrieron) | **Obligatoria** — Inclusive join | Sin join, no hay sincronización de los tokens activos |
| Vienen de una XOR (solo uno ocurrió) | **Por defecto: incluir XOR join explícito.** Omitir solo si se documenta la justificación. | La omisión es técnicamente válida cuando los flujos son mutuamente excluyentes en tiempo, pero degrada la legibilidad, dificulta auditoría y puede generar advertencias en motores de ejecución |
| Flujos de fuentes distintas sin relación entre sí | **Obligatoria** — XOR join o tipo correspondiente | Sin gateway, la semántica de convergencia es ambigua para herramientas y auditores |

> **Regla prescriptiva de XOR merge — criterio por defecto:**
> Cuando dos o más sequence flows llegan a una misma actividad, modelar **siempre** un gateway
> de convergencia explícito del tipo correspondiente. Para flujos XOR, la omisión del merge
> debe ser la excepción documentada, no la práctica habitual. La justificación de omisión
> debe registrarse en la sección de Supuestos y Vacíos de la especificación.
> **Motivos para incluir siempre el XOR join:**
> 1. Legibilidad: el lector identifica de inmediato la convergencia intencional.
> 2. Compatibilidad: motores como Camunda 7 y Flowable emiten advertencias ante múltiples
>    flujos entrantes sin gateway.
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

### Paso 7: Detectar colaboración y mensajería
- Message flow solo entre pools distintos.
- Registrar: emisor, receptor, nombre del mensaje, trigger, efecto esperado.
- Si el participante externo es una "caja negra", usar abstract pool (pool sin contenido interno).

### Paso 8: Detectar excepciones y caminos alternos

Para cada excepción identificada, elegir el patrón correcto:

| Situación | Patrón BPMN |
|---|---|
| Tiempo vencido en una tarea | Boundary Timer Event (interrupting o non-interrupting) |
| Error en tarea automática | Boundary Error Event (interrupting) |
| Escalación desde subproceso | Boundary Escalation Event |
| Cancelar todo dentro de una transacción | Boundary Cancel Event en Transaction Sub-Process |
| Deshacer tareas ya completadas por falla | Compensation Event + Compensation Activities |
| Rechazar y terminar | Exclusive Gateway + End Event con resultado claro |
| Reproceso | Loop o gateway con retorno al paso anterior (modelar el ciclo) |

### Paso 9: Evaluar descomposición en subprocesos
- **Sub-proceso embebido**: si la actividad tiene lógica interna compleja dentro del mismo proceso.
- **Sub-proceso colapsado**: para simplificar visualmente; los detalles van en diagrama separado.
- **Call Activity**: si la lógica es reutilizable en múltiples procesos (destacar con bordes gruesos).
- **Transaction Sub-Process**: si el grupo de actividades requiere protocolo todo-o-nada (compensación, cancelación, error).

### Paso 10: Registrar datos y artefactos
- **Data Object**: documento, formulario, archivo, registro.
- **Data Store**: base de datos, repositorio persistente.
- **Annotation**: aclaración que no afecta el flujo.
- **Group**: agrupación visual para documentación.

### Paso 11: Validar — detectar anti-patrones

Consultar `references/antipatrones.md` y verificar explícitamente:

**Correctitud:**
- [ ] Toda actividad tiene secuencia de entrada Y de salida (no implícitas).
- [ ] No se usa message flow dentro del mismo pool.
- [ ] No se usa sequence flow entre pools distintos.
- [ ] Los gateways divergentes están emparejados correctamente con convergentes.
- [ ] Flujos AND e OR tienen gateway de merging obligatorio — nunca conectados directamente a una actividad sin join.
- [ ] Toda actividad con dos o más sequence flows entrantes tiene un gateway de merge explícito. Si se omite para flujos XOR, la justificación está documentada en Supuestos y Vacíos.
- [ ] No hay múltiples Conditional Sequence Flows saliendo de la misma actividad (anti-patrón — debe ser Gateway).
- [ ] Conditional Sequence Flows solo salen de actividades o de Gateways Exclusivas/Inclusivas — nunca de eventos ni de Gateways Paralelas, Basadas en Eventos o Complejas.
- [ ] Los boundary events están asociados a la actividad correcta.
- [ ] No hay actividades aisladas sin justificación.
- [ ] Si hay lanes: existe `<bpmn:laneSet>` en el proceso con `<flowNodeRef>` para cada elemento — no solo shapes en el DI.
- [ ] Cada pool black-box tiene un `<bpmn:process>` vacío referenciado por `processRef` en su `<bpmn:participant>`.
- [ ] Participantes de la misma organización modelados como Lanes, no como Pools separados, salvo justificación explícita.

**Claridad:**
- [ ] Nombres de tareas: verbo + objeto (no sustantivos vagos como "Proceso de aprobación").
- [ ] Gateways con pregunta explícita y condición etiquetada en cada arco de salida.
- [ ] Gateways de convergencia (merge) nombrados explícitamente cuando el contexto pueda prestarse a confusión.
- [ ] Eventos con trigger o resultado comprensible sin asumir contexto.
- [ ] Mensajes con nombre que indica contenido o propósito.
- [ ] Pools y lanes con nombre del rol/entidad, no de la acción.

**Completitud:**
- [ ] Happy path recorrible de inicio a fin.
- [ ] Alternos documentados en la fuente están representados.
- [ ] Excepciones documentadas en la fuente están representadas.
- [ ] Timeouts y condiciones temporales representados.
- [ ] Datos relevantes para entender decisiones mencionados.

**Consistencia:**
- [ ] Convenciones de nomenclatura uniformes en todo el modelo.
- [ ] Misma semántica para negocio e implementación.
- [ ] Coherencia entre proceso principal y subprocesos.
- [ ] Sin ambigüedades que permitirían interpretaciones distintas del flujo.

### Paso 12: Emitir especificación estructurada

Ver §5 (Contrato de salida).

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
### 3.3 Gateways (nombre/pregunta, tipo, condiciones en cada salida, gateway de convergencia emparejado)
### 3.4 Eventos intermedios (nombre, tipo, modo: boundary interrupting / non-interrupting / inline)
### 3.5 Eventos de fin (nombre, tipo, resultado de negocio)

## 4. Sequence Flow
### 4.1 Happy path (lista ordenada de pasos)
### 4.2 Flujos alternos
### 4.3 Flujos de excepción
### 4.4 Tabla formal de secuencia
| Desde | Hacia | Condición / Trigger |
|---|---|---|

## 5. Message Flow
| Emisor | Receptor | Mensaje | Trigger | Efecto |
|---|---|---|---|---|

## 6. Datos y artefactos
- Data objects relevantes
- Data stores relevantes
- Annotations necesarias

## 7. Reglas de negocio
| Regla | Punto del proceso | Impacto |
|---|---|---|

## 8. Subprocesos y reutilización
- Subprocesos propuestos (tipo: embebido / colapsado / transaccional)
- Call activities propuestas
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
```

---

## 6. Reglas de estilo de salida

- Español claro y técnico.
- Listas estructuradas sobre párrafos largos.
- Distinguir siempre: `[FUENTE]` / `[INFERIDO]` / `[SUPUESTO]`.
- No mezclar recomendaciones con hechos documentados.
- Si algo falta en la fuente, marcarlo explícitamente; no inventar.

---

## 7. Criterio de cierre

La skill finaliza solo cuando:
1. se ha emitido la especificación completa;
2. se ha ejecutado la validación (§4 Paso 11);
3. se ha declarado el estado final con respecto a XML.

Si el proceso no está listo, indicar: qué falta, qué preguntas hacer, qué parte puede diagramarse y qué no debe serializarse aún.

---

## 8. Generación de XML (cuando se solicite)

### Checklist pre-emisión XML (ejecutar antes de escribir el archivo)
- [ ] ¿El proceso tiene lanes? → declarar `laneSet` con todos los `flowNodeRef`
- [ ] ¿Hay pools externos? → declarar proceso vacío + `processRef`
- [ ] ¿Todos los participantes internos son lanes, no pools? → verificar decisión
- [ ] ¿Cada sequence flow tiene `sourceRef` y `targetRef` válidos?
- [ ] ¿Cada gateway divergente AND o OR tiene su join emparejado del mismo tipo?
- [ ] ¿Hay flujos paralelos o inclusivos confluyendo directamente en una actividad sin join? → corregir antes de serializar.
- [ ] ¿Hay actividades con dos o más sequence flows entrantes sin gateway de merge? → agregar XOR join explícito salvo justificación documentada.

Leer `references/xml-layout.md` para reglas de posicionamiento.

Reglas esenciales:
- StartEvent: X=200; flujo avanza de izquierda a derecha; gap entre elementos = 140px.
- Cada Lane: altura fija 180px; elementos centrados verticalmente.
- Dimensiones estándar: Task 100×80; Event 36×36; Gateway 50×50.
- Anclaje: entrada = cara izquierda (x, y+h/2); salida = cara derecha (x+w, y+h/2).
- Gateways: entrada izquierda; salida 1 derecha; salida 2 inferior; salida 3 superior.
- Flujo ortogonal: sin líneas diagonales; al cruzar lanes usar "escalera" de 90°.
- Message Flow entre pools: buffer mínimo 150px entre pools.
- Salida: bloque de código XML bien indentado, listo para guardar como `.bpmn`, sin comentarios innecesarios.

### Reglas estructurales obligatorias del modelo semántico

**Lanes**: si el proceso tiene lanes, OBLIGATORIO declarar `<bpmn:laneSet>` dentro de `<bpmn:process>` con un `<bpmn:lane>` por cada lane. Cada lane DEBE contener un `<bpmn:flowNodeRef>` por cada elemento que le pertenece. Sin esto, las herramientas ignoran los lanes aunque estén en el DI.

**Pools black-box**: todo participante externo (sin lógica interna modelada) DEBE declararse como `<bpmn:process id="Proc_X" isExecutable="false"/>` vacío Y referenciarlo con `processRef="Proc_X"` en su `<bpmn:participant>`. Sin `processRef`, la mayoría de herramientas descarta el pool.

**Pools internos vs. externos**: usar un Pool separado solo cuando la entidad es organizacionalmente independiente (proveedor, banco, cliente). Áreas o departamentos de la misma organización van como Lanes dentro del mismo Pool, aunque intercambien comunicaciones formales internas.

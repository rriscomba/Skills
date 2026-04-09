# Catálogo de Anti-patrones BPMN 2.0

Basado en: Radulian (2020) *Rethinking BPMN*, Silver (2012) *BPMN Method and Style*,
White (2004) *Introduction to BPMN*, Bizagi (2017) *BPMN Quick Start Guide*.

---

## A. Anti-patrones de Correctitud

### A1 — Actividad sin secuencia de entrada
**Problema**: una tarea o evento no tiene arco de sequence flow entrante.
**Efecto BPMN**: el motor interpreta un Start Event implícito → el proceso puede iniciarse desde cualquier actividad aislada.
**Detección**: buscar en el documento fuente frases como "también se hace X" sin conectar con lo anterior.
**Corrección**: añadir sequence flow desde la actividad predecesora, o declarar un Start Event explícito si realmente es un trigger independiente.

### A2 — Actividad sin secuencia de salida
**Problema**: una tarea o evento no tiene arco de sequence flow saliente.
**Efecto BPMN**: el motor interpreta un End Event implícito → el proceso termina prematuramente o la actividad siguiente no se ejecuta nunca.
**Detección**: buscar actividades mencionadas al final de un párrafo sin descripción de qué sigue.
**Corrección**: añadir sequence flow hacia la siguiente actividad, o declarar un End Event explícito.

### A3 — Message Flow dentro del mismo Pool
**Problema**: se usa message flow (línea discontinua) para conectar actividades dentro del mismo pool.
**Efecto BPMN**: inválido; los motores BPMN lo rechazan.
**Detección**: el documento describe comunicación entre áreas o roles de la misma organización.
**Corrección**: usar sequence flow. Si las áreas son organizaciones realmente independientes, separarlas en pools distintos.

### A4 — Sequence Flow entre Pools distintos
**Problema**: se usa sequence flow (línea sólida) para conectar actividades en pools diferentes.
**Efecto BPMN**: inválido; el sequence flow no puede cruzar fronteras de pool.
**Corrección**: usar message flow + eventos de mensaje (Send/Receive) o Message Start/End Events.

### A5 — Gateway divergente sin gateway convergente
**Problema**: un Parallel o Inclusive Gateway abre ramas pero no hay un gateway de join correspondiente antes de que el flujo continúe.
**Efecto BPMN**: las actividades posteriores al punto de convergencia se ejecutan múltiples veces (una por cada rama activa).
**Detección**: el documento menciona "en paralelo" o "simultáneamente" pero no indica cuándo se sincronizan.
**Corrección**: añadir Parallel Join (o Inclusive Join) antes de continuar. Ver `elementos.md §3`.

### A6 — Conditions sin etiqueta en gateway
**Problema**: un Exclusive o Inclusive Gateway tiene arcos de salida sin condición.
**Efecto BPMN**: semánticamente ambiguo; el motor no sabe qué ruta tomar.
**Detección**: el documento menciona una decisión pero no especifica los criterios.
**Corrección**: etiquetar cada arco de salida con su condición. Si no se conoce, registrar en Vacíos. Siempre incluir un arco "else" o "default".

### A7 — Uso incorrecto de Association como Sequence Flow
**Problema**: se usa una asociación (línea punteada) para indicar flujo de trabajo.
**Efecto BPMN**: las asociaciones no transfieren tokens; el flujo está roto.
**Detección**: el modelador conectó un data object al siguiente paso asumiendo que eso indica secuencia.
**Corrección**: usar sequence flow para el flujo; usar association solo para conectar artefactos (data objects, annotations) con actividades.

### A8 — Múltiples Conditional Sequence Flows saliendo de la misma actividad
**Problema**: se usan dos o más Conditional Sequence Flows (mini-diamante) saliendo de una misma tarea para representar una bifurcación.
**Efecto BPMN**: semánticamente incorrecto; el Conditional Sequence Flow no es un mecanismo de enrutamiento sino una condición opcional de paso. Usar varios sobre la misma actividad replica el comportamiento de un Gateway Inclusivo sin declararlo, generando ambigüedad sobre qué pasa si ninguna condición es verdadera.
**Detección**: múltiples arcos con mini-diamante saliendo del mismo nodo de actividad.
**Corrección**: reemplazar por Gateway Exclusiva (si solo un camino puede activarse) o Gateway Inclusiva (si uno o más pueden activarse). El Conditional Sequence Flow solo es válido cuando hay un único arco condicional saliendo de una actividad.

### A9 — Flujos paralelos o inclusivos convergiendo directamente en una actividad sin gateway de join
**Problema**: ramas abiertas por una Gateway AND o OR confluyen directamente sobre una actividad sin gateway de convergencia.
**Efecto BPMN**: la actividad destino se ejecuta tantas veces como tokens lleguen (N ejecuciones no intencionadas).
**Detección**: múltiples sequence flows entrantes a una actividad que provienen de ramas abiertas por un split AND o OR.
**Corrección**: insertar la gateway de join del mismo tipo (Parallel join para AND; Inclusive join para OR) antes de la actividad destino. Solo en caso de XOR, la convergencia directa a una actividad es aceptable semánticamente (aunque se recomienda gateway de join para claridad).

---

## B. Anti-patrones de Claridad

### B1 — Nombre de tarea como sustantivo vago
**Problema**: nombres como "Aprobación", "Revisión del proceso", "Gestión de solicitud".
**Efecto**: ambigüedad; no indica quién hace qué.
**Corrección**: Verbo + Objeto. Ej: "Aprobar solicitud de crédito", "Revisar documentos del cliente".

### B2 — Nombre de gateway sin pregunta
**Problema**: el gateway se llama "Decisión" o "Verificación" en lugar de indicar la pregunta que se está respondiendo.
**Efecto**: el lector no puede entender sin contexto adicional qué criterio se está evaluando.
**Corrección**: nombrar con pregunta. Ej: "¿Información completa?", "¿Monto > $10,000?".

### B3 — Evento de inicio ambiguo
**Problema**: el Start Event se llama "Inicio" o "Comienzo" sin indicar el trigger.
**Efecto**: no se sabe qué lo dispara: ¿un mensaje? ¿un horario? ¿una acción manual?
**Corrección**: nombrar el resultado/trigger. Ej: "Solicitud recibida", "Fecha de corte alcanzada".

### B4 — Evento de fin sin resultado de negocio
**Problema**: el End Event se llama "Fin" o "Terminar".
**Efecto**: no se sabe en qué estado queda el proceso al terminar.
**Corrección**: nombrar el outcome. Ej: "Crédito aprobado", "Solicitud rechazada", "Pedido entregado".

### B5 — Múltiples End Events con el mismo nombre
**Problema**: dos o más End Events con el mismo nombre sugieren el mismo resultado pero representan salidas distintas.
**Efecto**: confusión sobre cuándo y por qué termina el proceso de cada forma.
**Corrección**: cada End Event debe tener un nombre único que refleje exactamente su resultado.

### B6 — Pool o Lane con nombre de acción en lugar de rol
**Problema**: un lane se llama "Revisar solicitud" en lugar del rol que la revisa.
**Corrección**: nombrar con el rol/área/entidad. Ej: "Analista de crédito", "Sistema ERP".

---

## C. Anti-patrones de Completitud

### C1 — Solo happy path
**Problema**: el modelo describe solo el camino exitoso.
**Detección**: buscar en el documento palabras como "si no", "en caso de rechazo", "cuando vence el plazo", "en caso de error", "si no hay respuesta".
**Corrección**: modelar todos los caminos alternativos y de excepción documentados en la fuente.

### C2 — Timeout no modelado
**Problema**: el documento menciona plazos o tiempos de espera pero el modelo no los representa.
**Corrección**: usar Boundary Timer Event (interrupting para cancelar, non-interrupting para notificar sin cancelar).

### C3 — Colaboración externa no representada
**Problema**: el proceso interactúa con un cliente, proveedor o sistema externo pero todo se modela en un solo pool.
**Corrección**: si el actor externo solo envía/recibe mensajes, añadir un black-box pool. Si su flujo interno importa, modelarlo en un segundo pool con sus actividades.

### C4 — Datos de decisión omitidos
**Problema**: un gateway toma una decisión pero no se documenta qué datos o regla la determina.
**Corrección**: asociar un Data Object o Business Rule Task que alimenta la decisión. Al menos anotarlo.

---

## D. Anti-patrones de Consistencia

### D1 — Nomenclatura mixta
**Problema**: algunas tareas usan "Verbo + Objeto", otras usan sustantivos, otras mezclan idiomas.
**Corrección**: definir y aplicar una convención única desde el inicio.

### D2 — Mismo concepto con nombres distintos
**Problema**: "solicitud", "pedido" y "requerimiento" se usan para referirse al mismo objeto de datos.
**Corrección**: elegir un término canónico y usarlo en todo el modelo.

### D3 — Niveles de abstracción mezclados
**Problema**: algunas actividades son de alto nivel (subproceso potencial) y otras son tareas atómicas, sin distinguir visualmente la diferencia.
**Corrección**: usar Sub-Process para actividades que contienen lógica detallable; usar Task solo para actividades atómicas. Ser consistente en el nivel de detalle de cada diagrama.

### D4 — Gateway convergente de tipo incorrecto
**Problema**: un Parallel split converge en un Exclusive join (o viceversa).
**Efecto**: el proceso se comporta diferente a lo que muestra el diagrama.
**Corrección**: el tipo de gateway de join debe coincidir con el tipo del split correspondiente.

---

## E. Checklist rápido de revisión

Antes de emitir la especificación, verificar:

```
Correctitud:
[ ] Toda actividad: ≥1 secuencia entrada + ≥1 secuencia salida
[ ] No hay message flow dentro del mismo pool
[ ] No hay sequence flow entre pools distintos
[ ] Todo Parallel/Inclusive split tiene su join emparejado del mismo tipo
[ ] No hay flujos AND/OR convergiendo directamente en una actividad sin gateway de join
[ ] No hay múltiples Conditional Sequence Flows saliendo de la misma actividad
[ ] Conditional Sequence Flows solo salen de actividades o Gateways XOR/OR — nunca de eventos ni AND/EBG
[ ] Boundary events adjuntos a la actividad correcta
[ ] No hay actividades aisladas sin justificación

Claridad:
[ ] Tareas: verbo + objeto
[ ] Gateways: pregunta explícita + condición en cada salida
[ ] Eventos de inicio: trigger nombrado
[ ] Eventos de fin: resultado de negocio nombrado
[ ] Pools/Lanes: nombre de rol/entidad, no de acción

Completitud:
[ ] Happy path completo
[ ] Todos los alternos del documento fuente representados
[ ] Todas las excepciones del documento fuente representadas
[ ] Timeouts y plazos modelados
[ ] Actores externos representados (al menos como black-box pool)

Consistencia:
[ ] Nomenclatura uniforme en todo el modelo
[ ] Un solo término por concepto
[ ] Nivel de abstracción uniforme dentro de cada diagrama
[ ] Tipos de gateway de join coinciden con sus splits
```

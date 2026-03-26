# Épica 5: Planificación docente

> Planificación del clase a clase por momentos, con asistencia de IA y feedback post-dictado.

**Estado:** MVP (parcial — bitácora y repropuesta son post-MVP)
**Fase de implementación:** Fase 5

---

## Problema

Los docentes planifican sus clases sin una conexión clara con lo acordado a nivel área, ni con lo que están dictando en clases los otros docentes. Re-planificar en base a lo que ocurrió en clases anteriores es algo que depende 100% del docente, de su energía y su memoria. Falta un sistema que alinee, proponga, recuerde y aprenda del día a día del aula.

## Objetivos

- Que cada clase planificada esté alineada con el documento de coordinación del área
- Que cada clase sea coherente con lo que se está dictando en otras disciplinas
- Generar una propuesta inicial de actividades por momento (apertura, desarrollo, cierre)
- Incorporar el feedback de clases anteriores para mejorar las propuestas futuras
- Permitir personalización del docente sin perder la alineación curricular

## Alcance MVP

**Incluye:**

- Visualización del cronograma de clases heredado del documento de coordinación
- Edición del objetivo de clase
- Selección de actividades por momento (apertura, desarrollo, cierre) con recomendaciones de IA
- Personalización: el docente puede anclar la clase a un recurso (canción, lectura, etc.) o a un comentario personalizado
- Generación de la propuesta detallada de clase
- Edición directa y asistida por IA de la propuesta
- Gestión de estados de las planificaciones (pending → planned)

**Post-MVP:**

- Bitácora de cotejo: el docente reporta cómo fue la clase (soporta audio)
- Recolección de datos: Alizia pregunta activamente por información faltante o alumnos con un caso que merezca seguimiento
- Repropuesta: En base a la bitácora proponemos cambios a las siguientes clases ya planificadas y tendremos eso en cuenta para la generación de las pendientes

**No incluye:**

- Offline / conectividad limitada → horizonte
- Informe de proceso (resumen de progreso del alumno por área) → horizonte
- Trayectorias de refuerzo personalizadas → horizonte
- Creación de recursos didácticos → ver Contenido

---

## Historias de usuario

| # | Historia | Descripción | Fase | Tareas |
|---|---------|-------------|------|--------|
| HU-5.1 | [Modelo de datos planificación](./HU-5.1-modelo-datos-planificacion/HU-5.1-modelo-datos-planificacion.md) | Tablas para lesson plans y actividades por momento | Fase 5 | 4 |
| HU-5.2 | [Cronograma del docente](./HU-5.2-cronograma-docente/HU-5.2-cronograma-docente.md) | El docente ve sus clases heredadas del documento de coordinación | Fase 5 | 3 |
| HU-5.3 | [Planificación por momentos](./HU-5.3-planificacion-por-momentos/HU-5.3-planificacion-por-momentos.md) | Crear y editar planificación con actividades, fuentes y notas | Fase 5 | 4 |
| HU-5.4 | [Generación con IA](./HU-5.4-generacion-ia/HU-5.4-generacion-ia.md) | Generar propuesta detallada de clase con Azure OpenAI | Fase 5 | 4 |
| HU-5.5 | [Estados de planificación](./HU-5.5-estados-planificacion/HU-5.5-estados-planificacion.md) | Gestión de estados pending → planned y reglas de visibilidad | Fase 5 | 3 |
| HU-5.6 | [Bitácora de cotejo](./HU-5.6-bitacora-cotejo/HU-5.6-bitacora-cotejo.md) | Post-clase: el docente reporta cómo fue (audio + texto) | Post-MVP | — |
| HU-5.7 | [Repropuesta](./HU-5.7-repropuesta/HU-5.7-repropuesta.md) | IA sugiere cambios a clases futuras basándose en bitácoras | Post-MVP | — |

---

## Decisiones técnicas

- Se asume **un docente por materia por curso**. Si excepcionalmente hay dos, opera first-come-first-serve.
- La planificación debe poder **exportarse como PDF** (template configurable por org).
- Los **momentos didácticos** (apertura, desarrollo, cierre) son fijos como estructura; los tipos de actividad dentro de cada momento son configurables por org (ver [HU-3.6](../03-integracion/HU-3.6-actividades-didacticas/HU-3.6-actividades-didacticas.md)).
- Cuando existe el feature flag de **clases coordinadas**, la planificación muestra indicador de clase compartida y se enriquece con contexto de la otra materia.
- La **bitácora de cotejo** (post-MVP) funciona por audio libre: el docente graba lo que pasó y el sistema lo procesa.

## Decisiones de cada cliente

- Los tipos de actividad disponibles por momento se definen con cada equipo pedagógico provincial
- El formato y profundidad de la bitácora de cotejo requiere validación
- La planificación debe poder exportarse como PDF para integración con plataformas provinciales

## Épicas relacionadas

- **[Épica 3: Integración](../03-integracion/03-integracion.md)** — Actividades didácticas (HU-3.6), course_subjects, grilla horaria
- **[Épica 4: Documento de coordinación](../04-documento-coordinacion/04-documento-coordinacion.md)** — Provee el cronograma y objetivos de clase
- **[Épica 6: Asistente IA](../06-assistente-ia/06-asistente-ia.md)** — Azure OpenAI para generación de propuestas
- **[Épica 8: Contenido y recursos](../08-contenido-recursos/08-contenido-recursos.md)** — Recursos disponibles para incorporar en la planificación

## Test cases asociados

- Fase 5: Tests 5.1–5.21 (modelo de datos, cronograma, planificación, generación IA, estados)

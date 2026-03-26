# HU-5.7: Repropuesta

> Como docente, necesito que Alizia sugiera cambios a mis próximas clases basándose en lo que pasó en las anteriores.

**Fase:** Post-MVP
**Prioridad:** Baja
**Estimación:** —

---

## Criterios de aceptación

- [ ] Cuando se completa una bitácora, el sistema evalúa si hay impacto en clases futuras
- [ ] Si detecta ajustes necesarios, genera sugerencias concretas para las próximas N clases
- [ ] Las sugerencias pueden ser: cambiar actividad, reasignar topics, modificar objetivo, agregar recurso
- [ ] El docente puede aceptar, rechazar o modificar cada sugerencia
- [ ] Las sugerencias se presentan como diff visual (antes → después)
- [ ] Los ajustes aceptados se aplican automáticamente al lesson plan

## Concepto

La repropuesta es la proactividad del sistema: no espera a que el docente planifique de cero, sino que propone cambios inteligentes basados en datos reales del aula.

### Escenarios de ejemplo

1. **Tiempo insuficiente:** La bitácora dice "no llegué a hacer el cierre" → Alizia sugiere acortar el desarrollo en la próxima clase similar

2. **Topic no comprendido:** El docente reporta "los alumnos no entendieron ecuaciones de primer grado" → Alizia sugiere reforzar ese topic en la siguiente clase, quizás cambiando la actividad

3. **Recurso exitoso:** "El video funcionó muy bien" → Alizia sugiere usar recursos similares en clases futuras con topics relacionados

4. **Alumno con dificultad:** El docente menciona un alumno específico → Alizia registra y sugiere actividades inclusivas

### Consideraciones

- Las sugerencias deben ser opt-in — el docente decide, no el sistema
- La calidad de las sugerencias depende directamente de la calidad de las bitácoras
- Requiere un modelo que "entienda" la progresión curricular para no sugerir retrocesos innecesarios
- Las sugerencias afectan planes en estado `pending` y `planned` (el docente decide si acepta el cambio)

## Dependencias

- [HU-5.6: Bitácora de cotejo](../HU-5.6-bitacora-cotejo/HU-5.6-bitacora-cotejo.md) — Fuente de datos
- [HU-5.4: Generación con IA](../HU-5.4-generacion-ia/HU-5.4-generacion-ia.md) — Regeneración de propuestas
- [Épica 6: Asistente IA](../../06-assistente-ia/06-asistente-ia.md) — Análisis y generación de sugerencias

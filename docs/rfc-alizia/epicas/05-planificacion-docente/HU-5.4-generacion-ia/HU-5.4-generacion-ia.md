# HU-5.4: Generación con IA

> Como docente, necesito que Alizia genere una propuesta detallada de clase basada en mis selecciones (actividades, fuente) y el contexto del documento de coordinación.

**Fase:** 5 — Planificación docente
**Prioridad:** Alta
**Estimación:** —

---

## Criterios de aceptación

- [ ] Endpoint `POST /api/v1/lesson-plans/:id/generate` genera la propuesta de clase
- [ ] La propuesta es un texto narrativo que describe el desarrollo de la clase paso a paso
- [ ] El prompt incluye: título, objetivo, actividades seleccionadas por momento, fuente anclada, topics de la clase, estrategia metodológica del documento
- [ ] Si la clase es compartida, incluye contexto de la otra materia
- [ ] La propuesta se guarda en el campo `proposal` del lesson plan
- [ ] Se puede regenerar (sobreescribe la propuesta anterior)
- [ ] Solo el docente asignado puede generar
- [ ] Si no hay actividades seleccionadas → 422 (primero debe configurar la clase)

## Tareas

| # | Tarea | Archivo | Estado |
|---|-------|---------|--------|
| 5.4.1 | [Prompt y schema para generación](./tareas/T-5.4.1-prompt-schema.md) | src/core/usecases/ | ⬜ |
| 5.4.2 | [Usecase: generar propuesta](./tareas/T-5.4.2-usecase-generar.md) | src/core/usecases/ | ⬜ |
| 5.4.3 | [Endpoint POST generate](./tareas/T-5.4.3-endpoint-generate.md) | src/entrypoints/ | ⬜ |
| 5.4.4 | [Tests](./tareas/T-5.4.4-tests.md) | tests/ | ⬜ |

## Dependencias

- [HU-5.3: Planificación por momentos](../HU-5.3-planificacion-por-momentos/HU-5.3-planificacion-por-momentos.md) — Plan con actividades configuradas
- [HU-4.3: Secciones dinámicas](../../04-documento-coordinacion/HU-4.3-secciones-dinamicas/HU-4.3-secciones-dinamicas.md) — Estrategia metodológica como contexto
- [Épica 6: Asistente IA](../../06-assistente-ia/06-asistente-ia.md) — Azure OpenAI

## Diseño técnico

### Contexto del prompt

El system prompt incluye:

1. **Clase:** título, objetivo, class_number
2. **Actividades seleccionadas:** por momento con nombre, descripción y nota del docente
3. **Fuente anclada:** si existe, URL o texto
4. **Topics:** categorías/temas asignados a esta clase desde el coord doc
5. **Documento de coordinación:** estrategia metodológica, eje problemático
6. **Clase compartida:** si is_shared, incluir materia y topics de la otra materia

### Output esperado

Texto narrativo en español, estructurado por momentos:

```
## Apertura (15 min)
[Descripción detallada de cómo iniciar la clase usando la actividad "Pregunta disparadora"...]

## Desarrollo (60 min)
### Actividad 1: Trabajo en grupo (30 min)
[Descripción detallada...]
### Actividad 2: Resolución de problemas (30 min)
[Descripción detallada...]

## Cierre (15 min)
[Descripción detallada de cómo cerrar con "Puesta en común"...]
```

### Flujo

```
POST /api/v1/lesson-plans/:id/generate
  → Verificar que el plan tiene actividades
  → Armar contexto (plan + coord doc + activities + source + topics)
  → Enviar a Azure OpenAI
  → Guardar proposal en el plan
  → Retornar plan actualizado
```

## Test cases

- 5.17: POST generate con plan completo → proposal generada
- 5.18: POST generate sin actividades → 422
- 5.19: POST generate en clase compartida → contexto incluye otra materia
- 5.20: Regenerar → proposal sobreescrita

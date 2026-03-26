# HU-5.3: Planificación por momentos

> Como docente, necesito crear y editar la planificación de cada clase seleccionando actividades por momento (apertura, desarrollo, cierre) y opcionalmente anclando la clase a un recurso o fuente.

**Fase:** 5 — Planificación docente
**Prioridad:** Alta
**Estimación:** —

---

## Criterios de aceptación

- [ ] Endpoint `POST /api/v1/lesson-plans` crea una planificación para una clase
- [ ] El plan hereda title y objective del coord_doc_class (editables por el docente)
- [ ] El docente selecciona actividades por momento: 1 apertura, 1-N desarrollo, 1 cierre
- [ ] La cantidad máxima de actividades en desarrollo viene de `config.desarrollo_max_activities`
- [ ] Cada actividad puede tener una custom_note opcional
- [ ] Endpoint `PATCH /api/v1/lesson-plans/:id` permite editar title, objective, activities y fuente
- [ ] El docente puede anclar la clase a una fuente: tipo resource (URL) o custom (texto libre)
- [ ] Solo el docente asignado puede crear/editar planificaciones
- [ ] Solo se puede planificar sobre documentos publicados

## Tareas

| # | Tarea | Archivo | Estado |
|---|-------|---------|--------|
| 5.3.1 | [Usecase: crear planificación](./tareas/T-5.3.1-usecase-crear.md) | src/core/usecases/ | ⬜ |
| 5.3.2 | [Usecase: editar planificación](./tareas/T-5.3.2-usecase-editar.md) | src/core/usecases/ | ⬜ |
| 5.3.3 | [Endpoints POST y PATCH](./tareas/T-5.3.3-endpoints.md) | src/entrypoints/ | ⬜ |
| 5.3.4 | [Tests](./tareas/T-5.3.4-tests.md) | tests/ | ⬜ |

## Dependencias

- [HU-5.1: Modelo de datos](../HU-5.1-modelo-datos-planificacion/HU-5.1-modelo-datos-planificacion.md) — Tablas
- [HU-5.2: Cronograma](../HU-5.2-cronograma-docente/HU-5.2-cronograma-docente.md) — Saber qué clases planificar
- [HU-3.6: Actividades](../../03-integracion/HU-3.6-actividades-didacticas/HU-3.6-actividades-didacticas.md) — Catálogo de actividades

## Diseño técnico

### POST Request

```json
{
  "course_subject_id": 1,
  "coord_doc_class_id": 42,
  "title": "Introducción al pensamiento algebraico",
  "objective": "Que los estudiantes identifiquen patrones numéricos...",
  "activities": [
    {"moment": "opening", "activity_id": 3, "custom_note": "Usar las tarjetas de colores", "order": 0},
    {"moment": "development", "activity_id": 7, "order": 0},
    {"moment": "development", "activity_id": 9, "custom_note": "Grupos de 4", "order": 1},
    {"moment": "closing", "activity_id": 12, "order": 0}
  ],
  "source_type": "resource",
  "source_reference": "https://example.com/lectura-algebraica.pdf"
}
```

### PATCH Request (parcial)

```json
{
  "title": "Nuevo título",
  "activities": [
    {"moment": "opening", "activity_id": 3, "order": 0},
    {"moment": "development", "activity_id": 10, "order": 0},
    {"moment": "closing", "activity_id": 12, "order": 0}
  ]
}
```

El PATCH de activities **reemplaza** todas las activities del plan (delete + insert). Esto simplifica la lógica frente a agregar/quitar individuales.

### Validaciones

1. **Momentos completos:** Debe haber al menos 1 actividad de apertura, 1+ de desarrollo, 1 de cierre
2. **Máximo desarrollo:** `len(development_activities) <= config.desarrollo_max_activities`
3. **Actividades válidas:** Cada activity_id debe existir y su momento debe coincidir
4. **Fuente:** Si source_type es "resource", source_reference no puede ser vacío

## Test cases

- 5.9: POST plan completo → 201 con activities creadas
- 5.10: POST sin actividad de apertura → 422
- 5.11: POST con más activities de desarrollo que el máximo → 422
- 5.12: POST con activity_id de momento incorrecto → 422
- 5.13: PATCH title y activities → actualizados
- 5.14: PATCH source_type=resource sin reference → 422
- 5.15: Otro docente intenta crear → 403

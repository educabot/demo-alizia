# HU-5.1: Modelo de datos planificacion

> Como equipo de desarrollo, necesito las tablas normalizadas para las planificaciones docentes y sus actividades por momento.

**Fase:** 5 — Planificacion docente
**Prioridad:** Alta (bloqueante para todo lo demas de esta epica)
**Estimacion:** —

---

## Criterios de aceptacion

- [ ] Tabla `teacher_lesson_plans` con: id, organization_id, course_subject_id, coordination_document_id, coord_doc_class_id, class_number, title, objective, status (enum), proposal (text), source_type (enum nullable), source_reference (text), created_at, updated_at
- [ ] Tabla `lesson_plan_activities` (junction: plan + momento + actividad + orden)
- [ ] Enum `lesson_plan_status`: pending, planned
- [ ] Enum `source_type`: resource, custom (nullable — null = sin fuente)
- [ ] FK a course_subjects, coordination_documents, coord_doc_classes
- [ ] Unique constraint: (course_subject_id, coord_doc_class_id) — una planificacion por clase por materia
- [ ] Entities Go con GORM tags y relaciones
- [ ] Provider interfaces para CRUD
- [ ] Repository GORM con preloads de actividades y relaciones

## Tareas

| # | Tarea | Archivo | Estado |
|---|-------|---------|--------|
| 5.1.1 | [Migracion: tablas de planificacion](./tareas/T-5.1.1-migracion.md) | db/migrations/ | ⬜ |
| 5.1.2 | [Entities y providers](./tareas/T-5.1.2-entities-providers.md) | src/core/ | ⬜ |
| 5.1.3 | [Repository GORM](./tareas/T-5.1.3-repository.md) | src/repositories/ | ⬜ |
| 5.1.4 | [Tests](./tareas/T-5.1.4-tests.md) | tests/ | ⬜ |

## Dependencias

- [HU-3.1: Organizaciones](../../03-integracion/HU-3.1-organizaciones-configuracion/HU-3.1-organizaciones-configuracion.md) — FK organization_id
- [HU-3.4: Cursos y asignaciones](../../03-integracion/HU-3.4-cursos-alumnos-asignaciones/HU-3.4-cursos-alumnos-asignaciones.md) — FK course_subject_id
- [HU-3.6: Actividades didacticas](../../03-integracion/HU-3.6-actividades-didacticas/HU-3.6-actividades-didacticas.md) — FK activity_id, enum class_moment
- [HU-4.1: Modelo de datos documento](../../04-documento-coordinacion/HU-4.1-modelo-datos-documento/HU-4.1-modelo-datos-documento.md) — FK coordination_document_id, coord_doc_class_id

## Diseno tecnico

### Modelo normalizado

```
teacher_lesson_plans
  └── lesson_plan_activities (plan ↔ moment ↔ activity + order)
```

### Relaciones

- `teacher_lesson_plans.course_subject_id` → `course_subjects.id` (que materia en que curso)
- `teacher_lesson_plans.coordination_document_id` → `coordination_documents.id` (de que doc hereda)
- `teacher_lesson_plans.coord_doc_class_id` → `coord_doc_classes.id` (que clase del plan)
- `lesson_plan_activities.activity_id` → `activities.id` (que actividad)
- `lesson_plan_activities.moment` usa el enum `class_moment` existente (opening, development, closing)

## Test cases

- 5.1: Crear lesson plan → todas las relaciones correctas
- 5.2: GET detalle → retorna plan con activities preloaded
- 5.3: Unique constraint (course_subject_id, coord_doc_class_id) → no duplicados

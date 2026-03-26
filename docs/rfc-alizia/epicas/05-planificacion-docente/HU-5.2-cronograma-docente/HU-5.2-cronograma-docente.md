# HU-5.2: Cronograma del docente

> Como docente, necesito ver el cronograma de clases de mi materia heredado del documento de coordinacion, incluyendo cuales son compartidas.

**Fase:** 5 -- Planificacion docente
**Prioridad:** Alta
**Estimacion:** --

---

## Criterios de aceptacion

- [ ] Endpoint `GET /api/v1/course-subjects/:id/lesson-plans` retorna la lista de clases del docente
- [ ] Cada clase muestra: class_number, title, objective, status de planificacion (pending/planned o sin plan)
- [ ] Las clases compartidas se marcan con is_shared y shared_with_subject
- [ ] Solo el docente asignado al course_subject puede ver el cronograma (o coordinadores del area)
- [ ] Si no hay documento de coordinacion publicado → 404 con mensaje claro
- [ ] Las clases se ordenan por class_number ASC

## Tareas

| # | Tarea | Archivo | Estado |
|---|-------|---------|--------|
| 5.2.1 | [Usecase: listar clases del docente](./tareas/T-5.2.1-usecase-listar-clases.md) | src/core/usecases/ | ⬜ |
| 5.2.2 | [Endpoint GET cronograma](./tareas/T-5.2.2-endpoint-cronograma.md) | src/entrypoints/ | ⬜ |
| 5.2.3 | [Tests](./tareas/T-5.2.3-tests.md) | tests/ | ⬜ |

## Dependencias

- [HU-5.1: Modelo de datos](../HU-5.1-modelo-datos-planificacion/HU-5.1-modelo-datos-planificacion.md) -- Tabla teacher_lesson_plans
- [HU-4.5: Publicacion](../../04-documento-coordinacion/HU-4.5-publicacion-estados/HU-4.5-publicacion-estados.md) -- Solo documentos published
- [HU-3.5: Grilla horaria](../../03-integracion/HU-3.5-grilla-horaria-clases-compartidas/HU-3.5-grilla-horaria-clases-compartidas.md) -- Shared classes

## Diseno tecnico

### Response

```json
{
  "course_subject": {
    "id": 1,
    "course": "3a",
    "subject": "Matematicas",
    "teacher": "Prof. Garcia"
  },
  "coordination_document": {
    "id": 5,
    "name": "Itinerario Ciencias 1er cuatrimestre",
    "status": "published"
  },
  "classes": [
    {
      "class_number": 1,
      "coord_doc_class_id": 42,
      "title": "Introduccion al pensamiento algebraico",
      "objective": "Que los estudiantes identifiquen patrones...",
      "is_shared": false,
      "shared_with_subject": null,
      "plan_status": "planned",
      "lesson_plan_id": 15
    },
    {
      "class_number": 2,
      "coord_doc_class_id": 43,
      "title": "Ecuaciones de primer grado",
      "objective": "Que los estudiantes resuelvan ecuaciones...",
      "is_shared": true,
      "shared_with_subject": "Fisica",
      "plan_status": "pending",
      "lesson_plan_id": 16
    },
    {
      "class_number": 3,
      "coord_doc_class_id": 44,
      "title": "Funciones lineales",
      "objective": "...",
      "is_shared": false,
      "shared_with_subject": null,
      "plan_status": null,
      "lesson_plan_id": null
    }
  ]
}
```

`plan_status: null` = el docente aun no creo planificacion para esa clase.

### Flujo

```
GET /api/v1/course-subjects/:id/lesson-plans
  → Buscar course_subject
  → Buscar coordination_document published del area del subject
  → Obtener coord_doc_classes de la materia
  → Obtener teacher_lesson_plans existentes (LEFT JOIN)
  → Calcular shared class numbers (desde grilla horaria)
  → Armar respuesta combinada
```

## Test cases

- 5.4: GET cronograma con doc publicado → lista de clases con plan_status
- 5.5: GET cronograma sin doc publicado → 404
- 5.6: Clases compartidas marcadas correctamente
- 5.7: Solo docente asignado o coordinador del area puede acceder → 403 para otros

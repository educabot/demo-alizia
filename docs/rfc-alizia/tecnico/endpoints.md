# Backend — Endpoints API

Todos los endpoints requieren autenticación via Bearer token (JWT via team-ai-toolkit/tokens) salvo `/health`.

---

## Admin (Fase 2)

| Método | Ruta | Descripción | Roles |
|--------|------|-------------|-------|
| POST | `/api/v1/areas` | Crear área | coordinator, admin |
| GET | `/api/v1/areas` | Listar áreas de la org | Todos |
| PUT | `/api/v1/areas/:id` | Actualizar área | coordinator, admin |
| POST | `/api/v1/areas/:id/coordinators` | Asignar coordinador | admin |
| POST | `/api/v1/subjects` | Crear materia | coordinator, admin |
| GET | `/api/v1/subjects` | Listar materias | Todos |
| POST | `/api/v1/courses` | Crear curso | admin |
| GET | `/api/v1/courses` | Listar cursos | Todos |
| GET | `/api/v1/courses/:id` | Detalle con students + schedule | Todos |
| POST | `/api/v1/courses/:id/time-slots` | Crear time slot | admin |
| POST | `/api/v1/topics` | Crear topic | admin |
| GET | `/api/v1/topics` | Listar topics (tree) | Todos |

---

## Coordination Documents (Fase 3)

| Método | Ruta | Descripción | Roles |
|--------|------|-------------|-------|
| POST | `/api/v1/coordination-documents` | Crear documento (wizard) | coordinator |
| GET | `/api/v1/coordination-documents` | Listar docs (filtro por area) | coordinator, teacher |
| GET | `/api/v1/coordination-documents/:id` | Detalle completo | coordinator, teacher |
| PATCH | `/api/v1/coordination-documents/:id` | Actualizar (sections, status) | coordinator |
| DELETE | `/api/v1/coordination-documents/:id` | Eliminar (solo draft) | coordinator |
| POST | `/api/v1/coordination-documents/:id/subjects` | Asignar materias + class_count | coordinator |
| POST | `/api/v1/coordination-documents/:id/generate` | Generar secciones + plan con IA | coordinator |
| POST | `/api/v1/coordination-documents/:id/chat` | Chat con Alizia (function calling) | coordinator |

---

## Teaching (Fase 5)

| Método | Ruta | Descripción | Roles |
|--------|------|-------------|-------|
| GET | `/api/v1/course-subjects/:id/lesson-plans` | Lesson plans del docente | teacher |
| POST | `/api/v1/lesson-plans` | Crear lesson plan | teacher |
| PATCH | `/api/v1/lesson-plans/:id` | Actualizar | teacher |
| POST | `/api/v1/lesson-plans/:id/generate-activity` | Generar contenido IA por actividad | teacher |

---

## Resources (Fase 6)

| Método | Ruta | Descripción | Roles |
|--------|------|-------------|-------|
| GET | `/api/v1/resource-types` | Tipos disponibles para la org | teacher |
| GET | `/api/v1/fonts` | Fuentes educativas del area | Todos |
| POST | `/api/v1/resources` | Crear recurso | teacher |
| PATCH | `/api/v1/resources/:id` | Actualizar | teacher |
| POST | `/api/v1/resources/:id/generate` | Generar con IA | teacher |

---

## AI (Fase 4)

| Método | Ruta | Descripción | Roles |
|--------|------|-------------|-------|
| POST | `/api/v1/chat` | Chat general con Alizia | Todos |

---

## Queries SQL de referencia

### Tipos de recurso disponibles para una org

```sql
SELECT rt.*, ort.custom_prompt, ort.custom_output_schema
FROM resource_types rt
LEFT JOIN organization_resource_types ort
    ON ort.resource_type_id = rt.id AND ort.organization_id = $1
WHERE rt.is_active = true
  AND (
    (rt.organization_id IS NULL AND COALESCE(ort.enabled, true) = true)
    OR rt.organization_id = $1
  );
```

### Detectar clases compartidas

```sql
SELECT ts.day_of_week, ts.start_time, ts.end_time,
       array_agg(cs.id) AS course_subject_ids
FROM time_slots ts
JOIN time_slot_subjects tss ON tss.time_slot_id = ts.id
JOIN course_subjects cs ON cs.id = tss.course_subject_id
WHERE ts.course_id = $1
GROUP BY ts.id
HAVING count(*) > 1;
```

### Clases con topics de un documento

```sql
SELECT cdc.class_number, cdc.title, array_agg(t.name) AS topics
FROM coord_doc_classes cdc
JOIN coordination_document_subjects cds ON cds.id = cdc.coord_doc_subject_id
LEFT JOIN coord_doc_class_topics cdct ON cdct.coord_doc_class_id = cdc.id
LEFT JOIN topics t ON t.id = cdct.topic_id
WHERE cds.coordination_document_id = $1 AND cds.subject_id = $2
GROUP BY cdc.id ORDER BY cdc.class_number;
```

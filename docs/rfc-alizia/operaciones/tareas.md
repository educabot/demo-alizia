# Tareas por fase

## Fase 1 — Setup

| # | Tarea | Estado |
|---|-------|--------|
| 1.1 | Crear repo alizia-api con estructura de directorios | ⬜ |
| 1.2 | Configurar go.mod con team-ai-toolkit | ⬜ |
| 1.3 | Configurar CI (GitHub Actions: test + lint) | ⬜ |
| 1.4 | Provisionar Railway + PostgreSQL | ⬜ |
| 1.5 | Configurar JWT auth (JWKS domain, audience) para staging + prod | ⬜ |
| 1.6 | Deploy inicial (/health responde) | ⬜ |
| 1.7 | Integrar auth middleware | ⬜ |

## Fase 2 — Admin/Integration

| # | Tarea | Estado |
|---|-------|--------|
| 2.1 | Migración init (enums + tablas base + triggers) | ⬜ |
| 2.2 | CRUD areas + area_coordinators | ⬜ |
| 2.3 | CRUD subjects | ⬜ |
| 2.4 | CRUD courses + students + course_subjects | ⬜ |
| 2.5 | CRUD topics (jerarquía con validación de niveles) | ⬜ |
| 2.6 | CRUD time_slots + time_slot_subjects (trigger same-course) | ⬜ |
| 2.7 | CRUD activities (por momento) | ⬜ |
| 2.8 | Tests de integración | ⬜ |

## Fase 3 — Coordination Documents

| # | Tarea | Estado |
|---|-------|--------|
| 3.1 | Migración coordination (6 tablas) | ⬜ |
| 3.2 | Crear documento (wizard 3 pasos) | ⬜ |
| 3.3 | Asignar materias + topics a materias | ⬜ |
| 3.4 | CRUD secciones dinámicas (sections JSONB) | ⬜ |
| 3.5 | Status workflow (draft → published → archived) | ⬜ |
| 3.6 | GET documento completo (con JOINs/Preloads) | ⬜ |
| 3.7 | Tests | ⬜ |

## Fase 4 — AI Generation

| # | Tarea | Estado |
|---|-------|--------|
| 4.1 | Azure OpenAI client wrapper | ⬜ |
| 4.2 | Generar secciones del doc (prompt por sección desde config) | ⬜ |
| 4.3 | Generar plan de clases (distribuir topics) | ⬜ |
| 4.4 | Chat con function calling (update_section, update_class, update_class_topics) | ⬜ |
| 4.5 | Tests con mock de AI client | ⬜ |

## Fase 5 — Teaching

| # | Tarea | Estado |
|---|-------|--------|
| 5.1 | Migración teaching (3 tablas + activities ya en Fase 2) | ⬜ |
| 5.2 | Crear lesson plan (hereda de doc) | ⬜ |
| 5.3 | Seleccionar actividades por momento (validar limits) | ⬜ |
| 5.4 | Seleccionar fonts (global o por momento) | ⬜ |
| 5.5 | Generar contenido por actividad (IA) | ⬜ |
| 5.6 | Tests | ⬜ |

## Fase 6 — Resources

| # | Tarea | Estado |
|---|-------|--------|
| 6.1 | Migración resources (4 tablas) | ⬜ |
| 6.2 | CRUD resource types + org overrides | ⬜ |
| 6.3 | CRUD fonts | ⬜ |
| 6.4 | Crear recurso + generar con IA (prompt resolution) | ⬜ |
| 6.5 | Query tipos disponibles por org | ⬜ |
| 6.6 | Tests | ⬜ |

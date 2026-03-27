# RFC: Alizia — Plataforma de planificación educativa anual

| Campo              | Valor                                      |
|--------------------|--------------------------------------------|
| **Autor(es)**      | Equipo Backend + Equipo de Producto        |
| **Estado**         | Borrador                                   |
| **Tipo**           | Épica / API / Refactor                     |
| **Creado**         | 2026-03-25                                 |
| **Última edición** | 2026-03-26                                 |
| **Revisores**      | Pendiente                                  |
| **Decisión**       | Pendiente                                  |

---

## Historial de versiones

| Versión | Fecha      | Autor   | Cambios |
|---------|------------|---------|---------|
| 0.1     | 2026-03-25 | Equipo Backend | Borrador inicial |
| 0.2     | 2026-03-25 | Equipo Backend | RFC completo — fusión de notion.md (producto) + proposal-der-v2 (datos) + arquitectura Go |
| 0.3     | 2026-03-26 | Equipo Backend | Reorganización local: contenido distribuido en carpetas modulares |

---

## Índice del RFC

- [Este documento](#contexto-y-motivación) — Contexto, objetivo, alcance, flujos, reglas, patrones, glosario
- [Épicas](./epicas/epicas.md) — 11 épicas (0–10) con definición de producto + tareas técnicas
- **Técnico**
  - [Arquitectura Go](./tecnico/arquitectura.md)
  - [Modelo de datos](./tecnico/modelo-de-datos.md)
  - [Endpoints API](./tecnico/endpoints.md)
  - [team-ai-toolkit](./tecnico/team-ai-toolkit.md)
  - [Auth service (futuro)](./tecnico/auth-service-futuro.md)
- **Operaciones**
  - [Testing](./operaciones/testing.md)
  - [Rollout](./operaciones/rollout.md)
  - [Riesgos, dependencias y preguntas abiertas](./operaciones/riesgos.md)
  - [Tareas por fase](./operaciones/tareas.md)
- **Decisiones**
  - [Comparativa arquitectura Go](./decisiones/comparativa-arquitectura.md)
  - [Comparativa deploy](./decisiones/comparativa-deploy.md)

---

## Contexto y motivación

### Problema

Los coordinadores y docentes de instituciones educativas planifican anualmente de forma fragmentada: documentos sueltos, WhatsApp, planillas, sin alineación entre áreas. No existe una herramienta que:

1. Permita al coordinador definir un plan de área que los docentes hereden
2. Genere contenido pedagógico con IA alineado al diseño curricular provincial
3. Recolecte feedback de lo que pasó en clase para mejorar planificaciones futuras
4. Se adapte a la estructura curricular de cada provincia sin cambios de código

### Contexto

- **POC actual**: Backend en FastAPI (Python), frontend vanilla HTML/JS, 10 tablas, sin multi-tenancy
- **POC validó**: El flujo coordinador → documento de coordinación → docente → lesson plan funciona
- **v2 es un rewrite completo**: Backend en Go, frontend en React, 26+ tablas, multi-tenant, IA integrada
- **Dos productos comparten infraestructura**: Alizia + TiCh/Tuni usan JWT (via team-ai-toolkit/tokens) para autenticación y team-ai-toolkit como librería compartida
- **Arquitectura ya definida**: Ver [arquitectura.md](./tecnico/arquitectura.md)

---

## Objetivo

### Objetivos

- Rewrite completo del backend en Go con Clean Architecture
- Multi-tenancy: cada provincia/institución es un tenant con configuración propia
- Documentos de coordinación con generación IA y edición colaborativa
- Planificación docente clase a clase heredada del documento de coordinación
- Sistema de recursos (guías, fichas) con generación IA configurable por org
- Clases compartidas (coordinadas) como diferenciador de producto
- Auth via JWT (team-ai-toolkit/tokens), con posibilidad de migrar a auth-service propio en el futuro

### No-objetivos

- Frontend (este RFC es solo backend)
- WhatsApp integration (Épica 9, pendiente de definición)
- Cosmos (Épica 10, sin definición)
- Social login (Google/Microsoft) — futuro
- Admin panel UI — administración por API
- Migración de datos del POC — se arranca de cero
- Roles de directivos o supervisores — horizonte
- Gestión de múltiples instituciones por usuario — por definir
- Informe de proceso de alumnos — horizonte
- Trayectorias de refuerzo personalizadas — horizonte

### Métricas de éxito

| Métrica | Valor esperado | Cómo se mide |
|---------|---------------|--------------|
| Documentos de coordinación creados | ≥1 por área piloto | Query DB |
| Lesson plans generados | ≥1 por docente piloto | Query DB |
| Tiempo de generación IA | < 30s por sección | Logs |
| Cobertura de tests | ≥ 80% | CI/CD coverage report |
| Uptime | > 99.5% | Railway healthcheck |

---

## Alcance

### Incluye (MVP)

- Épica 1: Roles y accesos (login, roles, multi-org)
- Épica 3: Integración (diseño curricular, topics, horarios)
- Épica 4: Documento de coordinación (wizard, secciones, IA, publicación)
- Épica 5: Planificación docente (lesson plans, momentos, IA) — sin bitácora ni repropuesta
- Épica 6: Asistente IA (generación, chat, function calling)
- Épica 8: Contenido (recursos, tipos, generación IA, library)

### No incluye (futuro)

- Épica 2: Onboarding — NTH post-MVP
- Épica 7: Dashboard — NTH, depende de Épica 4 y 5
- Épica 9: WhatsApp — pendiente definición
- Épica 10: Cosmos — pendiente definición
- Bitácora de cotejo (audio) — parte de Épica 5, post-MVP
- Repropuesta automática — parte de Épica 5, post-MVP
- Export PDF — NTH

### Fases de implementación

| Fase | Qué incluye | Dependencia |
|------|-------------|-------------|
| 1 — Setup | Repo, CI/CD, Railway, DB, auth integration (JWT), /health | team-ai-toolkit |
| 2 — Admin/Integration (Épica 1 + 3) | Orgs, areas, subjects, topics, courses, time slots | Fase 1 |
| 3 — Coordination Documents (Épica 4) | Wizard, secciones dinámicas, CRUD, publicación | Fase 2 |
| 4 — AI Generation (Épica 6) | Generación de secciones, plan de clases, chat | Fase 3 |
| 5 — Teaching (Épica 5) | Lesson plans, momentos, actividades, generación | Fase 3 |
| 6 — Resources (Épica 8) | Tipos de recurso, fonts, generación IA, library | Fase 2 |

---

## Diseño de producto

### Resumen del sistema

Sistema multi-tenant de planificación educativa anual. Cada organización (colegio, provincia) es un tenant con configuración propia via `organizations.config` (JSONB).

**Roles:**
- **Coordinador**: crea documentos de coordinación que definen qué se enseña por materia en un período (topics, plan de clases, secciones configurables por org)
- **Docente**: a partir del documento de coordinación, crea lesson plans clase a clase (momentos con actividades, fuentes) y recursos (guías, fichas, etc.)
- **Admin**: gestión de la organización, usuarios, configuración

**Flujo principal:**
1. Coordinador crea **coordination_document** para un área → selecciona topics, asigna a materias, genera plan de clases con IA
2. Docente ve el plan y crea **teacher_lesson_plans** por clase → selecciona actividades por momento (apertura/desarrollo/cierre), IA genera contenido por actividad
3. Docente crea **resources** (guías de lectura, fichas de curso, etc.) usando tipos configurables con generación IA

### Principios de diseño

1. **Provincial-first** — Cada implementación respeta la estructura y terminología de la provincia
2. **Proponer, no imponer** — La IA propone; el usuario decide
3. **Configurable, no customizable** — JSON config por org, no código custom por cliente
4. **Simple sobre abstracto** — Si un patrón emerge en 3+ clientes, entonces genericizar
5. **Rol define el flujo** — La experiencia del usuario cambia según su rol desde el inicio
6. **Del área al aula** — La planificación individual nace del acuerdo colectivo
7. **Fuentes curadas** — Los recursos se generan desde fuentes oficiales, no desde internet abierto
8. **IA que aprende del aula** — Las propuestas mejoran con el feedback real del docente
9. **Voz del docente** — La bitácora acepta audio libre, sin formato rígido

---

## Flujos de usuario

### Flujo 1: Setup de la organización (Admin)

**Actor:** Admin / Equipo de implementación
**Precondición:** Organización creada en el sistema

1. Crear organización con config JSONB (niveles de topics, secciones, feature flags)
2. Crear usuarios y asignar roles (teacher, coordinator, admin)
3. Crear áreas y asignar coordinadores
4. Crear materias en cada área
5. Crear cursos y alumnos
6. Crear course_subjects (curso + materia + docente + período)
7. Definir time_slots (grilla horaria semanal)
8. Si clases compartidas habilitadas → 2 time_slot_subjects por slot
9. Cargar topics (jerarquía según topic_max_levels de la config)
10. Cargar activities (por momento: apertura/desarrollo/cierre)

**Resultado:** Organización lista para que coordinadores creen documentos.

### Flujo 2: Coordinador crea documento de coordinación

**Actor:** Coordinador
**Precondición:** Área con materias y topics cargados

1. Coordinador selecciona área
2. **Wizard paso 1**: Selecciona topics al nivel configurado por `topic_selection_level`
3. **Wizard paso 2**: Define período (fechas custom) + cantidad de clases por materia
4. **Wizard paso 3**: Asigna topics a cada materia
5. Sistema crea documento en estado `draft`
6. Coordinador completa secciones dinámicas (según `config.coord_doc_sections`)
7. Opcionalmente genera secciones con IA ("Generar con Alizia")
8. IA genera: eje problemático, estrategia metodológica, plan de clases por materia
9. Coordinador revisa, edita directo o via chat con Alizia (function calling: `update_section`, `update_class`, etc.)
10. Coordinador publica → estado `published` → visible para docentes

**Resultado:** Documento publicado con secciones completas y plan de clases por materia.

### Flujo 3: Docente planifica clase a clase

**Actor:** Docente
**Precondición:** Documento de coordinación publicado para su materia

1. Docente ve el plan de clases heredado del documento de coordinación
2. Selecciona una clase (class_number)
3. Crea teacher_lesson_plan: título, objetivo, topics
4. Selecciona actividades por momento:
   - **Apertura**: exactamente 1 actividad
   - **Desarrollo**: 1 a `config.desarrollo_max_activities` (default 3) actividades
   - **Cierre**: exactamente 1 actividad
5. Selecciona fuentes educativas (global o por momento)
6. Opcionalmente genera contenido por actividad con IA (`activityContent`)
7. Edita directo o via chat con Alizia
8. Estado cambia a `planned`

**Resultado:** Lesson plan con momentos, actividades y contenido generado.

### Flujo 4: Docente crea recurso

**Actor:** Docente
**Precondición:** Tipos de recurso habilitados en la org

1. Docente elige tipo de recurso (guía de lectura, ficha de curso, etc.)
2. Si el tipo `requires_font` → selecciona font (fuente educativa)
3. Se resuelve el prompt: `organization_resource_types.custom_prompt` ?? `resource_types.prompt`
4. Se resuelve el output_schema: `custom_output_schema` ?? `output_schema`
5. Se envía al LLM con contexto (font, course_subject, etc.)
6. La respuesta se guarda en `resources.content` (JSONB) según el schema
7. Docente edita directo o via chat con Alizia
8. Recurso queda en library, reutilizable por otros docentes de la org

**Resultado:** Recurso generado, editable, exportable, reutilizable.

---

## Reglas de negocio

| # | Regla | Ejemplo | Aplica a |
|---|-------|---------|----------|
| 1 | Cada org define niveles de topics via config | `topic_max_levels: 3`, nombres: "Núcleos", "Áreas", "Categorías" | Back |
| 2 | Topics se seleccionan al nivel `topic_selection_level` | Si level=3, se eligen categorías, no núcleos | Back + Front |
| 3 | Clases compartidas solo si `shared_classes_enabled` | 2 materias en mismo time_slot, ambas del mismo área | Back |
| 4 | Secciones del doc son dinámicas según `coord_doc_sections` | Cada sección tiene key, label, type, ai_prompt, required | Back + Front |
| 5 | Momentos didácticos son enum fijo: apertura, desarrollo, cierre | desarrollo permite 1 a `desarrollo_max_activities` actividades | Back |
| 6 | Resource types pueden ser públicos (todas las orgs) o privados (1 org) | `organization_id IS NULL` = público | Back |
| 7 | Un usuario puede tener múltiples roles | teacher + coordinator en la misma org | JWT + Back |
| 8 | Mismo email puede existir en orgs distintas | `UNIQUE(email, organization_id)` | JWT + Back |
| 9 | El período del documento es texto libre con fechas custom | No se fuerza semestre/cuatrimestre | Back |
| 10 | Un docente por materia por curso (first-come-first-serve si hay conflicto) | El primero en planificar escribe | Back |
| 11 | Coordinador puede override manual de class_count (± feriados) | Ajuste manual sobre el cálculo automático | Back |
| 12 | Todos los topics del documento deben estar distribuidos entre materias | Validación al publicar | Back |
| 13 | Filter por materia en library es soft (UX), no permisos | Un docente de matemáticas puede ver recursos de ciencias | Front |
| 14 | Permisos sobre el doc de coordinación son configurables por org | Quién edita, quién solo visualiza | Back |

---

## Decisiones por provincia

| Decisión | Quién decide | Default | Impacto en config |
|----------|-------------|---------|-------------------|
| Niveles de topics (profundidad) | Provincia | 3 | `topic_max_levels`, `topic_level_names` |
| Nivel de selección de topics | Provincia | 3 | `topic_selection_level` |
| Clases compartidas habilitadas | Provincia | true | `shared_classes_enabled` |
| Secciones del documento | Provincia | problem_edge + methodological_strategy + eval_criteria | `coord_doc_sections` |
| Max actividades en desarrollo | Provincia | 3 | `desarrollo_max_activities` |
| Tipos de recurso habilitados | Provincia | Todos los públicos | `organization_resource_types` |
| Permisos del docente sobre el doc | Provincia | Solo lectura | Config de permisos |
| Datos requeridos en onboarding | Provincia | Perfil básico | Config de onboarding |
| Estrategias metodológicas disponibles | Provincia | proyecto, taller, ateneo | `coord_doc_sections[].options` |
| Tipos de actividad por momento | Provincia | Definidos con equipo pedagógico | Tabla `activities` |

---

## Estados y ciclo de vida

### Documento de coordinación
```
[draft] ──(publicar / coordinador)──> [published] ──(archivar / coordinador)──> [archived]
```

### Lesson plan
```
[pending] ──(planificar / docente)──> [planned]
```

### Recurso
```
[draft] ──(activar / docente)──> [active]
```

---

## Patrones transversales

| Patrón | Épicas | Descripción |
|---|---|---|
| JSON de configuración por org | 1, 2, 3, 4, 5, 8 | Configuración provincial centralizada (feature flags, nombres de niveles, tipos habilitados) |
| Prompt + JSON Schema por sección | 4, 6, 8 | Cada output generado por IA tiene prompt y schema configurable por provincia |
| Feature flags por organización | 2, 4, 5, 8 | Funcionalidades que se activan/desactivan por cliente |
| Clases coordinadas | 4, 5 | Diferenciador clave: sincronización entre docentes que comparten horario |
| Decisiones por provincia | Todas | Cada cliente customiza comportamiento sin cambios de código |

---

## Arquitectura general

```
┌─────────────────┐                    ┌──────────────────────┐
│  Alizia Frontend │                    │  JWT Auth             │
│  React + TS      │                    │  (team-ai-toolkit/    │
└────────┬────────┘                    │   tokens)             │
         │                              └──────────┬───────────┘
         │ HTTPS                                   │ JWT firmado
         ▼                                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      alizia-api (este RFC)                       │
│                                                                  │
│  Go 1.26 + Gin (via team-ai-toolkit/web)                        │
│  Clean Architecture: entities → providers → usecases → handlers  │
│  GORM + PostgreSQL                                               │
│  Deploy: Railway (Docker container)                              │
│                                                                  │
│  Módulos:                                                        │
│  ├── admin        → orgs, areas, subjects, topics, courses       │
│  ├── coordination → documentos, wizard, secciones, publicación   │
│  ├── teaching     → lesson plans, momentos, actividades          │
│  ├── resources    → fonts, tipos de recurso, recursos generados  │
│  └── ai           → Azure OpenAI, function calling, chat         │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │                     │
             ┌──────┴──────┐    ┌────────┴────────┐
             │  PostgreSQL  │    │  Azure OpenAI    │
             │  (Railway)   │    │  (gpt-5-mini)    │
             └─────────────┘    └─────────────────┘
```

### Stack técnico

| Componente | Tecnología |
|---|---|
| Lenguaje | Go 1.26 |
| Framework | Gin (abstraído via team-ai-toolkit/web) |
| ORM | GORM (estándar empresa) |
| DB | PostgreSQL |
| Auth | JWT + Bearer tokens (team-ai-toolkit/tokens valida via JWKS) |
| AI | Azure OpenAI SDK (gpt-5-mini) |
| Logging | slog (team-ai-toolkit/applog) |
| Error tracking | Bugsnag (team-ai-toolkit/applog/bugsnag) |
| Testing | testify + GORM, target 80% |
| Linting | golangci-lint (15+ linters) |
| Deploy | Railway (Docker, auto-deploy desde GitHub) |

Ver [arquitectura.md](./tecnico/arquitectura.md) para estructura de directorios completa, patrones de código, y decisiones técnicas detalladas.

---

## Configuración por organización

```jsonc
{
  // --- Taxonomía de temas ---
  "topic_max_levels": 3,
  "topic_level_names": [
    "Núcleos problemáticos",
    "Áreas de conocimiento",
    "Categorías"
  ],
  "topic_selection_level": 3,

  // --- Clases compartidas ---
  "shared_classes_enabled": true,

  // --- Secciones del documento de coordinación ---
  "coord_doc_sections": [
    {
      "key": "problem_edge",
      "label": "Eje problemático",
      "type": "text",
      "ai_prompt": "Generá un eje problemático que integre las categorías seleccionadas...",
      "required": true
    },
    {
      "key": "methodological_strategy",
      "label": "Estrategia metodológica",
      "type": "select_text",
      "options": ["proyecto", "taller_laboratorio", "ateneo_debate"],
      "ai_prompt": "Generá una estrategia metodológica de tipo {selected_option}...",
      "required": true
    },
    {
      "key": "eval_criteria",
      "label": "Criterios de evaluación",
      "type": "text",
      "ai_prompt": "Generá criterios de evaluación para las categorías seleccionadas...",
      "required": false
    }
  ],

  // --- Lesson plans ---
  "desarrollo_max_activities": 3
}
```

### Estructura JSONB: sections del coordination document

```json
{
  "problem_edge": {
    "value": "¿Cómo las lógicas de poder y saber configuran..."
  },
  "methodological_strategy": {
    "selected_option": "proyecto",
    "value": "Implementaremos un ateneo-debate interdisciplinario..."
  },
  "eval_criteria": {
    "value": "Los criterios de evaluación serán..."
  }
}
```

### Estructura JSONB: moments del teacher_lesson_plan

```json
{
  "apertura": {
    "activities": [1],
    "activityContent": { "1": "Texto generado por IA para actividad 1..." }
  },
  "desarrollo": {
    "activities": [3, 5],
    "activityContent": { "3": "...", "5": "..." }
  },
  "cierre": {
    "activities": [8],
    "activityContent": { "8": "..." }
  }
}
```

---

## Alternativas evaluadas

### Arquitectura

| Criterio | POC (FastAPI) | Go + GORM + Railway |
|----------|:---:|:---:|
| Performance | Python | Go |
| Multi-tenancy | No | org_id en JWT |
| Equipo conoce | Python | Go (tich-cronos) |
| Escalabilidad | No | Sí |
| Infra compartida | No | team-ai-toolkit |

> **Elegido: Go + GORM + Railway**

### ORM

| Criterio | GORM | sqlx |
|----------|:---:|:---:|
| Equipo lo conoce | Sí | No |
| CRUD rápido | Sí | No |
| Queries complejas | Raw SQL | Sí |
| Performance | Buena | Óptima |

> **Elegido: GORM** — estándar empresa. sqlx documentado como alternativa futura en [arquitectura.md](./tecnico/arquitectura.md).

---

## Glosario

| Término | Definición |
|---------|-----------|
| Coordination Document | Documento de planificación anual de un área, creado por el coordinador |
| Lesson Plan | Plan de clase individual creado por el docente, hereda del coordination document |
| Topic | Tema/saber en la jerarquía curricular (self-referential, niveles configurables) |
| Class Moment | Momento didáctico: apertura, desarrollo, cierre |
| Shared Class / Clase compartida | Dos materias enseñadas simultáneamente por dos docentes en el mismo horario. Diferenciador clave del producto |
| Font | Fuente educativa (PDF, video, documento) — del español "fuente", NO tipografía |
| Resource Type | Tipo de recurso generado por IA (guía de lectura, ficha de curso, etc.) |
| Organization / org | Tenant: una provincia, escuela, o universidad con configuración propia |
| team-ai-toolkit | Librería Go compartida con infra reutilizable (web, boot, tokens, etc.) |
| Railway | Plataforma de hosting para containers Docker |
| Bitácora | Registro post-clase del docente sobre cómo fue la clase (soporta audio). Post-MVP |
| Repropuesta | Sugerencia automática de cambios a clases futuras basada en bitácora. Post-MVP |
| NAP | Núcleos de Aprendizajes Prioritarios — lineamientos curriculares nacionales argentinos |

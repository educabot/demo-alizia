# Épica 1: Roles y accesos

> Autenticación, roles, permisos y asignación organizacional de usuarios.

**Estado:** MVP
**Fases de implementación:** Fase 1 (auth) + Fase 2 (modelo + CRUD)

---

## Problema

La plataforma opera con múltiples roles (coordinador, docente, y potencialmente directivos) que tienen permisos distintos sobre los mismos documentos y cursos. Se necesita un sistema que controle quién puede crear, editar y visualizar cada recurso o informes.

## Objetivos

- Autenticar usuarios de forma segura
- Definir roles con permisos diferenciados (coordinador crea documentos, docente planifica clases)
- Asignar usuarios a instituciones, áreas y cursos

## Alcance MVP

**Incluye:**

- Autenticación de usuarios (email + password via JWT authentication)
- Roles de coordinator, teacher y admin con permisos diferenciados
- Asignación de usuarios a organizaciones y cursos

**No incluye:**

- Roles de directivos o supervisores → horizonte
- Gestión de múltiples instituciones por usuario → por definir

## Principios de diseño

- **Rol define el flujo:** La experiencia del usuario cambia según su rol desde el inicio.
- **Asignación clara:** Cada usuario sabe a qué cursos e instituciones tiene acceso.

---

## Historias de usuario

| # | Historia | Descripción | Fase | Tareas |
|---|---------|-------------|------|--------|
| HU-1.1 | [Autenticación JWT](./HU-1.1-autenticacion-jwt/HU-1.1-autenticacion-jwt.md) | JWT middleware, JWKS validation, tenant middleware, refresh, CORS | Fase 1 | 6 |
| HU-1.2 | [Modelo de usuarios y roles](./HU-1.2-modelo-usuarios-roles/HU-1.2-modelo-usuarios-roles.md) | Migración, entities, repository GORM, seed | Fase 2 | 6 |
| HU-1.3 | [Middleware de autorización](./HU-1.3-middleware-autorizacion/HU-1.3-middleware-autorizacion.md) | RequireRole, interceptor chain, error handling | Fase 2 | 4 |
| HU-1.4 | [Asignación organizacional](./HU-1.4-asignacion-organizacional/HU-1.4-asignacion-organizacional.md) | Area coordinators, admin endpoints, multi-tenancy | Fase 2 | 5 |

> **Nota:** El setup del proyecto (repo, CI/CD, Railway, Docker) se movió a [Épica 0](../00-setup-infraestructura/00-setup-infraestructura.md).

---

## Decisiones técnicas

- Un usuario puede tener **múltiples roles dentro de una misma organización**. Un docente puede ser profesor de dos materias y coordinador de un área — no hay restricción. Idealmente la experiencia no necesita "Escoger un rol" para el usuario.
- En el MVP, si un usuario trabaja en **dos instituciones distintas**, tiene dos cuentas separadas (un usuario por organización).
- El mecanismo de autenticación puede variar por provincia: mail + contraseña, cuentas institucionales (ej: Google Workspace del ministerio), u otros proveedores. Para el MVP, limitamos a mail + password via JWT authentication (team-ai-toolkit/tokens).
- Los permisos sobre el documento de coordinación (quién edita, quién solo visualiza) son **configurables por organización**. No se hardcodea que "el coordinador edita y el docente solo ve" porque hay provincias donde el docente también interviene.

## Decisiones de cada cliente

- Los roles adicionales a coordinador y docente dependen de cada provincia
- El modelo de permisos sobre el documento de coordinación (quién edita, quién solo visualiza) es decisión de cada cliente

## Épicas relacionadas

- **Onboarding** — Flujo post-autenticación para nuevos usuarios
- **Documento de coordinación** — Permisos de edición y visualización del documento
- **Planificación docente** — Acceso del docente a sus cursos y clases

## Test cases asociados

- Fase 1: Tests 1.2–1.5 (auth, JWT)
- Permisos: Tests P1–P8 (roles por endpoint)
- Multi-tenancy: Tests T1–T4 (isolation entre orgs)

Ver [testing.md](../../operaciones/testing.md) para la matriz completa.

# HU-3.1: Organizaciones y configuración

> Como admin, necesito gestionar organizaciones con su configuración provincial para que cada tenant tenga comportamiento personalizado.

**Fase:** 2 — Admin/Integration
**Prioridad:** Alta (bloqueante para todo lo demás)
**Estimación:** —

---

## Criterios de aceptación

- [ ] Tabla `organizations` existe con campos: id, name, slug (unique), config (JSONB), created_at
- [ ] Entity `Organization` en Go con struct tags GORM
- [ ] Provider interface `OrganizationProvider` con métodos CRUD
- [ ] Repository GORM implementa el provider
- [ ] Endpoint `GET /api/v1/organizations/:id` retorna org con config
- [ ] Endpoint `PATCH /api/v1/organizations/:id` actualiza config (merge parcial del JSONB)
- [ ] Config JSONB tiene defaults sensatos al crear una org
- [ ] Seed con al menos 1 organización de ejemplo con config completa
- [ ] Multi-tenancy: org_id se extrae del JWT y filtra todos los queries

## Tareas

| # | Tarea | Archivo | Estado |
|---|-------|---------|--------|
| 3.1.1 | [Migración: organizations](./tareas/T-3.1.1-migracion-organizations.md) | db/migrations/ | ⬜ |
| 3.1.2 | [Entity y provider](./tareas/T-3.1.2-entity-provider.md) | src/core/ | ⬜ |
| 3.1.3 | [Repository GORM](./tareas/T-3.1.3-repository.md) | src/repositories/ | ⬜ |
| 3.1.4 | [Endpoints y handler](./tareas/T-3.1.4-endpoints-handler.md) | src/entrypoints/ | ⬜ |
| 3.1.5 | [Seed de organización](./tareas/T-3.1.5-seed.md) | db/seeds/ | ⬜ |

## Dependencias

- [Épica 0: Setup](../../00-setup-infraestructura/00-setup-infraestructura.md) completada (repo, CI, DB)
- [HU-1.1: Autenticación JWT](../../01-roles-accesos/HU-1.1-autenticacion-jwt/HU-1.1-autenticacion-jwt.md) — JWT con org_id en claims

## Test cases

- 3.1: GET org → retorna config JSONB completa
- 3.2: PATCH org con config parcial → merge sin perder keys existentes
- 3.3: Request con JWT de org A → no puede ver org B

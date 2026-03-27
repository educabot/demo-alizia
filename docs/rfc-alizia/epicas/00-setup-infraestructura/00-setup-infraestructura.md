# Épica 0: Setup e infraestructura

> Repositorio, arquitectura base, CI/CD, infraestructura de deploy y entorno de desarrollo local.

**Estado:** MVP
**Fase de implementación:** Fase 1

---

## Problema

Antes de construir cualquier feature, el equipo necesita un proyecto base funcional con estructura Clean Architecture definida, patrones de código establecidos, CI/CD corriendo, base de datos provisionada y deploy automático a staging.

## Objetivos

- Crear el repositorio con estructura Clean Architecture (`src/core/`, `src/entrypoints/`, `src/repositories/`)
- Establecer los patrones base de código (DI manual, error handling, config, route mapping)
- Configurar CI/CD con tests y linting automáticos (80% coverage target)
- Provisionar infraestructura de staging (Railway + PostgreSQL)
- Tener un endpoint `/health` respondiendo en producción
- Entorno de desarrollo local reproducible (Docker + Air hot reload)
- Documentación del proyecto (README.md, TESTING.md)

## Alcance MVP

**Incluye:**

- Repo con estructura de directorios `src/` por capas (no por módulos)
- `go.mod` con team-ai-toolkit + GORM + golang-migrate + testify + Azure OpenAI SDK
- Clean Architecture: entities, providers (interfaces), usecases, entrypoints (handlers), repositories
- DI manual separado en archivos: `cmd/main.go`, `app.go`, `repositories.go`, `usecases.go`, `handlers.go`
- Config embebiendo `team-ai-toolkit/config.BaseConfig`
- Error handling extendiendo `team-ai-toolkit/errors`
- Route mapping centralizado en `src/app/web/mapping.go`
- GitHub Actions (test + lint en cada PR, coverage target 80%)
- Railway con PostgreSQL managed
- Dockerfile multi-stage + docker-compose local
- Makefile, Air hot reload, pre-commit hooks
- Endpoint /health (incluido en team-ai-toolkit/boot)
- Deploy automático desde main
- README.md y TESTING.md del proyecto

**No incluye:**

- Monitoring avanzado (Grafana, Prometheus) → horizonte
- Environments múltiples (preview per-PR) → por definir

---

## Stack tecnológico

| Componente | Tecnología | Justificación |
|-----------|-----------|---------------|
| Lenguaje | Go 1.26 | Performance, tipado, concurrencia |
| HTTP Framework | Gin (intercambiable via `team-ai-toolkit/web/`) | Ecosistema maduro, abstraído |
| ORM | GORM | Estándar de la empresa (tich-cronos) |
| Base de datos | PostgreSQL | Multi-tenant, JSONB, enums |
| Migraciones | golang-migrate | Up/down, embebidas en binario |
| Auth | JWT + Bearer tokens (via team-ai-toolkit/tokens) | Validación via JWKS |
| AI | Azure OpenAI SDK | Requerimiento de negocio |
| Logging | slog via team-ai-toolkit/applog | Structured logging nativo |
| Error tracking | Bugsnag via team-ai-toolkit/applog/bugsnag | Stack actual empresa |
| Testing | testify + GORM | Mocks para unit, PostgreSQL real para integration |
| Linting | golangci-lint | 15+ linters configurados |
| Hot reload | Air | Desarrollo rápido |
| CI/CD | GitHub Actions | Test + lint + coverage + deploy |
| Deploy | Railway | Container Docker, auto-deploy, sin vendor lock-in |
| Infra compartida | team-ai-toolkit | Librería Go con web/, boot/, tokens/, errors/, etc. |

## Relación con team-ai-toolkit

```
┌─────────────────────────────────────────────────────────┐
│  team-ai-toolkit (librería compartida, no se deploya)    │
│                                                         │
│  web/          → Abstracción HTTP (Request, Response)   │
│  web/gin/      → Adaptador Gin (Adapt, AdaptMiddleware) │
│  boot/         → Server bootstrap (NewEngine, NewServer) │
│  tokens/       → JWT JWKS validation, Claims, middleware │
│  dbconn/       → PostgreSQL connection (GORM)            │
│  errors/       → Sentinel errors + HandleError()        │
│  pagination/   → ParseFromQuery + PaginatedResponse     │
│  transactions/ → RunInTx(), DBTX interface              │
│  applog/       → Setup slog + ErrorTracker interface    │
│  applog/bugsnag/ → Bugsnag adapter                     │
│  config/       → EnvOr(), MustEnv(), BaseConfig        │
└──────────────────────────┬──────────────────────────────┘
                           │
                           │  go.mod: require github.com/educabot/team-ai-toolkit
                           │
┌──────────────────────────▼──────────────────────────────┐
│  alizia-api (este proyecto, se deploya)                  │
│                                                         │
│  cmd/          → Entry point + DI manual                │
│  src/core/     → entities, providers, usecases          │
│  src/entrypoints/ → HTTP handlers                       │
│  src/repositories/ → GORM + raw SQL cuando necesario    │
│  src/mocks/    → Mocks de todas las capas               │
│  src/app/      → Route mapping                          │
│  config/       → Config propio (embebe BaseConfig)      │
│  db/migrations/→ Schema propio                          │
└─────────────────────────────────────────────────────────┘
```

**Alizia NO tiene** `web/`, `boot/`, `packages/`. Todo eso viene de `team-ai-toolkit`.

## Arquitectura Clean Architecture

```
cmd/
├── main.go ──→ config.Load() + NewApp()
└── app.go  ──→ repositories.go → usecases.go → handlers.go

         ┌──────────────────────────────────────────────────────────┐
         │                                                          │
         ▼                                                          ▼
   src/repositories/                                    src/entrypoints/rest/
   (implementa providers)                               (consume usecases)
         │                                                          │
         ▼                                                          ▼
   src/core/providers/ ◄──────── src/core/usecases/ ──→ src/core/providers/
   (interfaces)                  (lógica de negocio)    (interfaces)
         │                              │
         ▼                              ▼
   src/core/entities/            src/core/entities/
   (modelos puros)               (modelos puros)

   team-ai-toolkit/ ◄── usado por cmd/, entrypoints/, repositories/
   (web, boot, tokens, dbconn, errors, pagination, transactions, applog)
```

**Reglas de dependencia:**
- `core/` NO importa `repositories/`, `entrypoints/`, ni `team-ai-toolkit`
- `usecases/` solo importa `providers/` (interfaces) y `entities/`
- `entrypoints/` importa `usecases/` (interfaces), `entities/`, y `team-ai-toolkit/web`
- `repositories/` importa `providers/`, `entities/`, y `team-ai-toolkit/dbconn` + `transactions`
- `cmd/` importa todo para hacer el wiring

---

## Historias de usuario

| # | Historia | Descripción | Fase | Tareas |
|---|---------|-------------|------|--------|
| HU-0.1 | [Setup del proyecto e infraestructura](./HU-0.1-setup-proyecto/HU-0.1-setup-proyecto.md) | Repo, scaffolding, CI/CD, Railway, Docker, dev tools, documentación | Fase 1 | 9 |

---

## Decisiones técnicas

- **DI manual** (no Wire) separado en archivos: `repositories.go` → `usecases.go` → `handlers.go`
- **GORM como ORM** (estándar empresa, equipo ya lo conoce). Para queries complejas: `db.Raw()`
- **1 archivo = 1 operación** en usecases (granularidad fina)
- **Containers** para agrupar handlers por feature
- **Abstracción HTTP** via team-ai-toolkit/web — framework intercambiable
- **Config como struct inmutable** (no singleton, testeable)
- **Sentinel errors + fmt.Errorf %w** — Go estándar
- **Railway** container Docker, auto-deploy, zero vendor lock-in
- **Alternativa futura: sqlx** si queries complejas dominan (>50% de repos usan Raw). La arquitectura Clean permite migrar tocando solo `src/repositories/`

## Principios de diseño

- **Zero vendor lock-in:** Dockerfile portable a cualquier plataforma (Render, Fly.io, VPS)
- **Dev-prod parity:** Mismo PostgreSQL version local y en staging
- **CI rápido:** Pipeline < 3 min para no bloquear PRs
- **Filosofía:** Tomar lo mejor de ai-assistant (simplicidad, DI manual, abstracción HTTP) y tich-cronos (Clean Architecture, testing robusto, CI completo)

## Épicas relacionadas

- **Roles y accesos** — Necesita repo y DB funcionando para empezar con auth
- **Integración** — Necesita la estructura de módulos para crear entities

## Test cases asociados

- Fase 1: Test 1.1 (GET /health → 200)

Ver [testing.md](../../operaciones/testing.md) para la matriz completa.

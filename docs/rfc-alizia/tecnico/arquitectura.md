# Arquitectura Go — Alizia

Documento de referencia para el equipo. Define estructura, patrones, convenciones y decisiones técnicas del backend.

**Contexto**: Plataforma educativa multi-tenant. Monolito modular con JWT authentication (via team-ai-toolkit/tokens). PostgreSQL. Railway como deploy target. Equipo de 4+ devs.

**Filosofía**: Tomar lo mejor de ai-assistant (simplicidad, graceful degradation, SQL explícito, abstracción HTTP) y tich-cronos (Clean Architecture, testing robusto, CI completo) sin caer en over-engineering.

**Librería compartida**: Este proyecto importa `github.com/educabot/team-ai-toolkit` que contiene toda la infraestructura reutilizable (web/, boot/, tokens/, dbconn/, errors/, pagination/, transactions/, applog/, config/). Ver documento BACK-CONFIG-LIBRERIA.md para detalles.

---

## Stack Tecnológico

| Componente | Tecnología | Justificación |
|-----------|-----------|---------------|
| Lenguaje | Go 1.26 | Performance, tipado, concurrencia |
| HTTP Framework | Gin (intercambiable via `team-ai-toolkit/web/`) | Ecosistema maduro, abstraído para poder cambiar |
| ORM | GORM | Estándar de la empresa, ya usado en tich-cronos |
| Base de datos | PostgreSQL | Multi-tenant, JSONB, triggers, enums |
| Migraciones | golang-migrate | Up/down, embebidas en binario |
| Auth | JWT + Bearer tokens (via team-ai-toolkit/tokens) | Validación via JWKS |
| AI | Azure OpenAI SDK | Requerimiento de negocio |
| Logging | slog via team-ai-toolkit/applog | Structured logging nativo, sin dependencias |
| Error tracking | Bugsnag via team-ai-toolkit/applog/bugsnag | Stack actual de la empresa, ya integrado en tich-cronos |
| Testing | testify + GORM | Mocks para unit, PostgreSQL real para integration |
| Linting | golangci-lint | 15+ linters configurados |
| Hot reload | Air | Desarrollo rápido |
| CI/CD | GitHub Actions | Test + lint + coverage + deploy |
| Deploy | Railway | Container Docker, auto-deploy desde GitHub, sin vendor lock-in |
| Infra compartida | team-ai-toolkit | Librería Go con web/, boot/, tokens/, errors/, etc. |

### GORM como ORM

GORM es el estándar de la empresa (tich-cronos lo usa). Beneficios para el equipo:

- El equipo ya lo conoce, sin curva de aprendizaje
- CRUD rápido (menos código para operaciones simples)
- Soft deletes, hooks, preloading de relaciones
- Connection pooling integrado
- Migraciones automáticas desde structs (para desarrollo, SQL explícito para producción)

Para queries complejas (JOINs de 8+ tablas, CTEs recursivos para topics), se usa `db.Raw()`. Ver sección "Alternativa futura: sqlx" al final del documento para los beneficios de migrar a sqlx si las queries complejas dominan.

### Deploy e infraestructura: Railway

Railway es la plataforma de deploy para Alizia. Corre un Docker container estándar — el mismo Dockerfile que usamos en desarrollo local.

#### ¿Qué es Railway?

Railway es una plataforma de hosting que toma un Dockerfile (o detecta el lenguaje automáticamente), lo builda, lo deploya, y le rutea tráfico. Es como un Heroku moderno pero con soporte nativo de Docker.

#### ¿Cómo funciona el deploy?

```
1. Dev pushea a main (o merge PR)
2. GitHub Actions corre tests + lint
3. Si pasan → Railway detecta el push automáticamente
4. Railway hace docker build con el Dockerfile del repo
5. Railway levanta el container y rutea tráfico al puerto 8080
6. El container queda corriendo (sin cold starts)
```

No hay pasos manuales. Push a main = deploy automático.

#### ¿Qué configura Railway?

| Aspecto | Cómo se configura |
|---|---|
| **Environment variables** | Dashboard de Railway (DATABASE_URL, JWKS_DOMAIN, JWKS_AUDIENCE, API_KEY_BUGSNAG, etc.) |
| **Puerto** | Railway detecta `PORT` automáticamente o se configura en dashboard |
| **Dominio** | Railway asigna un dominio `.up.railway.app` + custom domain si se necesita |
| **PostgreSQL** | Railway ofrece PostgreSQL managed en el mismo proyecto, o se conecta a una DB externa |
| **Healthcheck** | Railway monitorea `GET /health` (ya existe en `boot/gin.go` de team-ai-toolkit) |
| **Logs** | Railway captura stdout. slog en JSON (producción) se muestra en el dashboard |
| **Scaling** | Vertical (más CPU/RAM) desde dashboard. Horizontal (réplicas) en plan Pro |
| **Rollback** | Railway permite revertir a cualquier deploy anterior con un click |

#### ¿Qué impacto tiene en el código?

**Ninguno.** Railway corre un Docker container. Si el container arranca y escucha en un puerto, Railway funciona. No necesita:

- ~~SDKs de la plataforma~~ (no hay `railway.Init()` ni similar)
- ~~Adapters de Cloud Functions~~ (eliminado `src/app/functions/`)
- ~~API Gateway~~ (Railway rutea directo al container)
- ~~Configuración especial en el código~~ (usa env vars estándar)

Todo lo que está en `team-ai-toolkit` funciona sin cambios:

| team-ai-toolkit | Impacto de Railway |
|---|---|
| `boot/server.go` | Railway le pasa `PORT` como env var, el server escucha ahí. Sin cambios |
| `boot/gin.go` | `/health` ya existe, Railway lo usa para healthcheck. Sin cambios |
| `applog/` | slog a stdout, Railway lo captura. Sin cambios |
| `dbconn/` | Se conecta por `DATABASE_URL` (env var). Sin cambios |
| `tokens/` | Validación JWT via JWKS. Sin cambios |
| `web/` | Abstracción HTTP no sabe dónde corre. Sin cambios |

#### ¿Y si mañana migran de Railway?

El Dockerfile es estándar. Se puede deployar en:
- Otro PaaS: Render, Fly.io, Heroku
- Cloud: GCP Cloud Run, AWS ECS, Azure Container Apps
- VPS: cualquier servidor con Docker
- Kubernetes: con un manifest básico

**Zero vendor lock-in.** Railway no requiere código ni configuración específica de la plataforma.

#### Estructura de Railway (proyecto)

```
Railway Project: alizia
├── Service: alizia-api          ← Este repo (Docker container)
│   ├── Dockerfile               ← Build automático
│   ├── Environment variables    ← DATABASE_URL, JWKS_DOMAIN, JWKS_AUDIENCE, etc.
│   └── Custom domain            ← api.alizia.com (opcional)
│
└── Service: postgres            ← PostgreSQL managed (o externo)
    ├── DATABASE_URL             ← Inyectado automáticamente al api
    └── Backups                  ← Automáticos
```

### ¿Por qué slog y no una librería?

Go 1.21+ incluye `log/slog` con structured logging. Es estándar, no agrega dependencias, y soporta JSON output para producción + text output para desarrollo. Bugsnag captura los errores críticos por separado.

---

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

---

## Estructura de Directorios

```
alizia-api/
├── cmd/                                         # Entry point + DI manual (1 archivo por responsabilidad)
│   ├── main.go                                  # config → NewApp() → Run()
│   ├── app.go                                   # App struct, NewApp(), Run(), Close(), graceful shutdown
│   ├── repositories.go                          # Crea todos los repos (retorna RepositoriesContainer)
│   ├── usecases.go                              # Crea todos los usecases (recibe repos)
│   ├── handlers.go                              # Crea todos los handlers + containers (recibe usecases)
│   └── routes.go                                # Rutas condicionales de dev (si se necesitan)
│
├── src/
│   ├── app/                                     # Configuración de rutas
│   │   └── web/
│   │       └── mapping.go                       # TODAS las rutas del web server registradas acá
│   │
│   ├── core/                                    # DOMINIO PURO — no importa nada de infraestructura
│   │   │
│   │   ├── entities/                            # Modelos de datos puros (structs + constantes + enums)
│   │   │   ├── organization.go
│   │   │   ├── user.go
│   │   │   ├── area.go
│   │   │   ├── subject.go
│   │   │   ├── topic.go
│   │   │   ├── course.go
│   │   │   ├── timeslot.go
│   │   │   ├── coordination.go
│   │   │   ├── lesson_plan.go
│   │   │   ├── activity.go
│   │   │   ├── font.go
│   │   │   └── resource.go
│   │   │
│   │   ├── providers/                           # INTERFACES — contratos que el dominio necesita
│   │   │   ├── admin.go
│   │   │   ├── coordination.go
│   │   │   ├── teaching.go
│   │   │   ├── resources.go
│   │   │   ├── ai.go
│   │   │   └── errors.go                        # Errores ESPECÍFICOS de Alizia (extiende team-ai-toolkit/errors)
│   │   │
│   │   └── usecases/                            # LÓGICA DE NEGOCIO — 1 archivo = 1 operación
│   │       ├── admin/
│   │       │   ├── create_area.go
│   │       │   ├── create_area_test.go
│   │       │   ├── list_areas.go
│   │       │   ├── create_topic.go
│   │       │   ├── create_course.go
│   │       │   └── assign_coordinator.go
│   │       ├── coordination/
│   │       │   ├── create_document.go
│   │       │   ├── create_document_test.go
│   │       │   ├── get_document.go
│   │       │   ├── update_sections.go
│   │       │   ├── set_doc_subjects.go
│   │       │   ├── generate_content.go
│   │       │   ├── generate_content_test.go
│   │       │   ├── publish_document.go
│   │       │   └── chat.go
│   │       ├── teaching/
│   │       │   ├── create_lesson_plan.go
│   │       │   ├── create_lesson_plan_test.go
│   │       │   ├── select_activities.go
│   │       │   ├── generate_activity.go
│   │       │   └── list_lesson_plans.go
│   │       └── resources/
│   │           ├── create_resource.go
│   │           ├── generate_resource.go
│   │           └── list_resource_types.go
│   │
│   ├── entrypoints/                             # HTTP handlers — traducen HTTP ↔ usecases
│   │   ├── admin.go                             # AdminContainer
│   │   ├── coordination.go                      # CoordinationContainer
│   │   ├── teaching.go                          # TeachingContainer
│   │   ├── resources.go                         # ResourcesContainer
│   │   ├── containers.go                        # WebHandlerContainer (agrupa todos)
│   │   └── rest/
│   │       ├── rest.go                          # HandleError() que extiende team-ai-toolkit/errors
│   │       ├── admin/
│   │       │   ├── create_area.go
│   │       │   ├── create_area_test.go
│   │       │   ├── list_areas.go
│   │       │   ├── create_topic.go
│   │       │   └── create_course.go
│   │       ├── coordination/
│   │       │   ├── create.go
│   │       │   ├── get.go
│   │       │   ├── update.go
│   │       │   ├── generate.go
│   │       │   ├── chat.go
│   │       │   └── publish.go
│   │       ├── teaching/
│   │       │   ├── create_plan.go
│   │       │   ├── generate_activity.go
│   │       │   └── list_plans.go
│   │       └── resources/
│   │           ├── create.go
│   │           ├── generate.go
│   │           └── list_types.go
│   │
│   ├── repositories/                            # IMPLEMENTACIONES de providers con GORM
│   │   ├── admin/
│   │   │   ├── repository.go                    # struct + New(db *gorm.DB)
│   │   │   ├── create_area.go
│   │   │   ├── create_area_test.go
│   │   │   ├── list_areas.go
│   │   │   └── create_topic.go
│   │   ├── coordination/
│   │   │   ├── repository.go
│   │   │   ├── get_document.go                  # Preload + Raw SQL para JOINs complejos
│   │   │   ├── get_document_test.go
│   │   │   ├── create_document.go
│   │   │   ├── set_topics.go
│   │   │   └── set_subjects.go
│   │   ├── teaching/
│   │   │   ├── repository.go
│   │   │   └── create_lesson_plan.go
│   │   ├── resources/
│   │   │   ├── repository.go
│   │   │   └── list_resource_types.go
│   │   └── ai/
│   │       ├── client.go                        # Azure OpenAI SDK wrapper
│   │       ├── prompts/
│   │       │   ├── generate_strategy.txt
│   │       │   ├── generate_class_plan.txt
│   │       │   └── chat_system.txt
│   │       └── schemas/
│   │           └── tools.go
│   │
│   ├── mocks/                                   # Mocks de TODAS las capas
│   │   ├── providers/
│   │   │   ├── admin.go
│   │   │   ├── coordination.go
│   │   │   ├── teaching.go
│   │   │   ├── resources.go
│   │   │   └── ai.go
│   │   └── usecases/
│   │       ├── admin.go
│   │       ├── coordination.go
│   │       ├── teaching.go
│   │       └── resources.go
│   │
│   └── utils/
│       ├── json.go
│       ├── pointers.go
│       └── slices.go
│
├── config/
│   └── config.go                                # Embebe team-ai-toolkit/config.BaseConfig + campos propios
│
├── db/
│   └── migrations/
│       ├── 000001_init.up.sql
│       ├── 000001_init.down.sql
│       ├── 000002_coordination.up.sql
│       ├── 000002_coordination.down.sql
│       ├── 000003_teaching.up.sql
│       ├── 000003_teaching.down.sql
│       ├── 000004_resources.up.sql
│       └── 000004_resources.down.sql
│
├── docs/
│   └── swagger.yml
│
├── scripts/
│   ├── migrate.sh
│   └── seed.sh
│
├── .github/
│   └── workflows/
│       ├── test.yml
│       ├── lint.yml
│       └── deploy.yml                           # Railway auto-deploy
│
├── Dockerfile
├── docker-compose.yml
├── .golangci.yml
├── .air.toml
├── .pre-commit-config.yaml
├── Makefile
├── go.mod                                       # require github.com/educabot/team-ai-toolkit
└── go.sum
```

**Lo que NO tiene este proyecto (viene de team-ai-toolkit):**
- ~~web/~~ → `team-ai-toolkit/web`
- ~~boot/~~ → `team-ai-toolkit/boot`
- ~~packages/~~ → `team-ai-toolkit/tokens`, `dbconn`, `pagination`, `transactions`, `applog`, `errors`

---

## Flujo de Dependencias

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

## Configuración (embebe BaseConfig de team-ai-toolkit)

```go
// config/config.go
package config

import (
    "os"
    bcfg "github.com/educabot/team-ai-toolkit/config"
)

type Config struct {
    bcfg.BaseConfig                     // Port, Env, DatabaseURL, JWKSDomain, JWKSAudience, AllowedOrigins, BugsnagAPIKey
    AzureOpenAIKey      string
    AzureOpenAIEndpoint string
    AzureOpenAIModel    string
}

func Load() *Config {
    base := bcfg.LoadBase()
    return &Config{
        BaseConfig:          base,
        AzureOpenAIKey:      bcfg.MustEnv("AZURE_OPENAI_API_KEY"),
        AzureOpenAIEndpoint: bcfg.MustEnv("AZURE_OPENAI_ENDPOINT"),
        AzureOpenAIModel:    bcfg.EnvOr("AZURE_OPENAI_MODEL", "gpt-5-mini"),
    }
}
```

`BaseConfig` ya trae Port, Env, DatabaseURL, JWKSDomain, JWKSAudience, AllowedOrigins, BugsnagAPIKey. Alizia solo agrega los campos específicos del proyecto (Azure OpenAI).

---

## cmd/ — Entry Point + DI Manual

### cmd/main.go — Entry point (mínimo)
```go
package main

import (
    "alizia-api/config"
    "github.com/educabot/team-ai-toolkit/applog"
    "github.com/educabot/team-ai-toolkit/dbconn"
)

func main() {
    cfg := config.Load()
    applog.Setup(cfg.Env)

    db := dbconn.MustConnectGORM(cfg.DatabaseURL)
    sqlDB, _ := db.DB()
    defer sqlDB.Close()

    app := NewApp(cfg, db)
    defer app.Close()
    app.Run()
}
```

### cmd/app.go — App struct, lifecycle, graceful shutdown
```go
package main

import (
    "log/slog"
    "os"
    "os/signal"
    "syscall"
    "alizia-api/config"
    "alizia-api/src/entrypoints"
    appweb "alizia-api/src/app/web"
    "github.com/educabot/team-ai-toolkit/boot"
    "github.com/educabot/team-ai-toolkit/applog/bugsnag"
    "gorm.io/gorm"
)

type App struct {
    cfg    *config.Config
    db     *gorm.DB
    server *boot.Server
}

func NewApp(cfg *config.Config, db *gorm.DB) *App {
    // Error tracker (Bugsnag o NoOp si no hay API key)
    tracker := bugsnag.NewTracker(cfg.BugsnagAPIKey, cfg.Env)

    repos := NewRepositories(cfg, db)
    usecases := NewUseCases(repos, cfg)
    container := NewHandlers(usecases, cfg)

    // Boot: crea Gin engine con middleware global (viene de team-ai-toolkit)
    engine := boot.NewEngine(cfg.Env, cfg.AllowedOrigins)

    // Bugsnag middleware (si está configurado)
    if cfg.BugsnagAPIKey != "" {
        engine.Use(bugsnag.GinMiddleware())
    }

    // Registra rutas
    appweb.ConfigureMappings(engine, container, cfg)

    // Server HTTP con timeouts y graceful shutdown (viene de team-ai-toolkit)
    server := boot.NewServer(cfg.Port, engine)

    return &App{cfg: cfg, db: db, server: server}
}

func (a *App) Run() {
    go func() {
        sigCh := make(chan os.Signal, 1)
        signal.Notify(sigCh, syscall.SIGINT, syscall.SIGTERM)
        sig := <-sigCh
        slog.Info("shutting down", "signal", sig)
        a.server.Shutdown()
    }()

    a.server.Run()
}

func (a *App) Close() {
    a.db.Close()
}
```

### cmd/repositories.go — Crea todos los repos
```go
package main

import (
    "alizia-api/config"
    "alizia-api/src/core/providers"
    adminr "alizia-api/src/repositories/admin"
    coordr "alizia-api/src/repositories/coordination"
    teachr "alizia-api/src/repositories/teaching"
    resr   "alizia-api/src/repositories/resources"
    air    "alizia-api/src/repositories/ai"
    "gorm.io/gorm"
)

type Repositories struct {
    Admin        providers.Admin
    Coordination providers.Coordination
    Teaching     providers.Teaching
    Resources    providers.Resources
    AI           providers.AIClient
}

func NewRepositories(cfg *config.Config, db *gorm.DB) *Repositories {
    return &Repositories{
        Admin:        adminr.New(db),
        Coordination: coordr.New(db),
        Teaching:     teachr.New(db),
        Resources:    resr.New(db),
        AI:           air.NewClient(cfg.AzureOpenAIKey, cfg.AzureOpenAIEndpoint),
    }
}
```

### cmd/usecases.go — Crea todos los usecases
```go
package main

import (
    "alizia-api/config"
    adminuc "alizia-api/src/core/usecases/admin"
    coorduc "alizia-api/src/core/usecases/coordination"
    teachuc "alizia-api/src/core/usecases/teaching"
    resuc   "alizia-api/src/core/usecases/resources"
)

type UseCases struct {
    CreateArea      adminuc.CreateArea
    ListAreas       adminuc.ListAreas
    CreateTopic     adminuc.CreateTopic
    CreateDocument  coorduc.CreateDocument
    GetDocument     coorduc.GetDocument
    GenerateContent coorduc.GenerateContent
    Chat            coorduc.Chat
    PublishDocument  coorduc.PublishDocument
    CreateLessonPlan teachuc.CreateLessonPlan
    ListLessonPlans  teachuc.ListLessonPlans
    GenerateActivity teachuc.GenerateActivity
    ListResourceTypes resuc.ListResourceTypes
    CreateResource    resuc.CreateResource
    GenerateResource  resuc.GenerateResource
}

func NewUseCases(repos *Repositories, cfg *config.Config) *UseCases {
    return &UseCases{
        CreateArea:       adminuc.NewCreateArea(repos.Admin),
        ListAreas:        adminuc.NewListAreas(repos.Admin),
        CreateTopic:      adminuc.NewCreateTopic(repos.Admin),
        CreateDocument:   coorduc.NewCreateDocument(repos.Coordination),
        GetDocument:      coorduc.NewGetDocument(repos.Coordination),
        GenerateContent:  coorduc.NewGenerateContent(repos.Coordination, repos.AI),
        Chat:             coorduc.NewChat(repos.Coordination, repos.AI),
        PublishDocument:   coorduc.NewPublishDocument(repos.Coordination),
        CreateLessonPlan: teachuc.NewCreateLessonPlan(repos.Teaching),
        ListLessonPlans:  teachuc.NewListLessonPlans(repos.Teaching),
        GenerateActivity: teachuc.NewGenerateActivity(repos.Teaching, repos.AI),
        ListResourceTypes: resuc.NewListResourceTypes(repos.Resources),
        CreateResource:    resuc.NewCreateResource(repos.Resources),
        GenerateResource:  resuc.NewGenerateResource(repos.Resources, repos.AI),
    }
}
```

### cmd/handlers.go — Crea handlers + containers
```go
package main

import (
    "alizia-api/config"
    "alizia-api/src/entrypoints"
    "github.com/educabot/team-ai-toolkit/tokens"
    adminh "alizia-api/src/entrypoints/rest/admin"
    coordh "alizia-api/src/entrypoints/rest/coordination"
    teachh "alizia-api/src/entrypoints/rest/teaching"
    resh   "alizia-api/src/entrypoints/rest/resources"
)

func NewHandlers(uc *UseCases, cfg *config.Config) *entrypoints.WebHandlerContainer {
    jwksValidator, err := tokens.NewJWKSValidator(cfg.JWKSDomain, cfg.JWKSAudience)
    if err != nil {
        panic("invalid JWT config: " + err.Error())
    }

    return &entrypoints.WebHandlerContainer{
        Admin: entrypoints.NewAdminContainer(
            adminh.NewCreateArea(uc.CreateArea),
            adminh.NewListAreas(uc.ListAreas),
            adminh.NewCreateTopic(uc.CreateTopic),
        ),
        Coordination: entrypoints.NewCoordinationContainer(
            coordh.NewCreate(uc.CreateDocument),
            coordh.NewGet(uc.GetDocument),
            coordh.NewGenerate(uc.GenerateContent),
            coordh.NewChat(uc.Chat),
            coordh.NewPublish(uc.PublishDocument),
        ),
        Teaching: entrypoints.NewTeachingContainer(
            teachh.NewCreatePlan(uc.CreateLessonPlan),
            teachh.NewListPlans(uc.ListLessonPlans),
            teachh.NewGenerateActivity(uc.GenerateActivity),
        ),
        Resources: entrypoints.NewResourcesContainer(
            resh.NewListTypes(uc.ListResourceTypes),
            resh.NewCreate(uc.CreateResource),
            resh.NewGenerate(uc.GenerateResource),
        ),
        AuthMiddleware:   tokens.NewAuthInterceptor(jwksValidator),
        TenantMiddleware: tokens.NewTenantInterceptor(),
    }
}
```

### Cómo se registran las rutas

```go
// src/app/web/mapping.go
package web

import (
    webgin "github.com/educabot/team-ai-toolkit/web/gin"
    "alizia-api/src/entrypoints"
)

func ConfigureMappings(engine *gin.Engine, h *entrypoints.WebHandlerContainer, conf *config.Config) {
    api := engine.Group("/api/v1")

    // Middleware (de team-ai-toolkit, adaptados via webgin)
    api.Use(webgin.AdaptMiddleware(h.AuthMiddleware))
    api.Use(webgin.AdaptMiddleware(h.TenantMiddleware))

    // Admin routes
    api.POST("/areas", webgin.Adapt(h.Admin.CreateArea.Handle()))
    api.GET("/areas", webgin.Adapt(h.Admin.ListAreas.Handle()))
    api.POST("/topics", webgin.Adapt(h.Admin.CreateTopic.Handle()))

    // Coordination routes
    docs := api.Group("/coordination-documents")
    docs.POST("", webgin.Adapt(h.Coordination.Create.Handle()))
    docs.GET("/:id", webgin.Adapt(h.Coordination.Get.Handle()))
    docs.PATCH("/:id", webgin.Adapt(h.Coordination.Update.Handle()))
    docs.POST("/:id/generate", webgin.Adapt(h.Coordination.Generate.Handle()))
    docs.POST("/:id/chat", webgin.Adapt(h.Coordination.Chat.Handle()))

    // Teaching routes
    api.POST("/lesson-plans", webgin.Adapt(h.Teaching.CreatePlan.Handle()))
    api.GET("/course-subjects/:id/lesson-plans", webgin.Adapt(h.Teaching.ListPlans.Handle()))

    // Resources routes
    api.GET("/resource-types", webgin.Adapt(h.Resources.ListTypes.Handle()))
    api.POST("/resources", webgin.Adapt(h.Resources.Create.Handle()))
    api.POST("/resources/:id/generate", webgin.Adapt(h.Resources.Generate.Handle()))
}
```

---

## Capas — Qué es cada una y qué hace

### core/entities/ — Modelos puros

Structs de datos + constantes + enums. **Zero lógica, zero imports de infra**.

```go
// src/core/entities/coordination.go
package entities

import "time"

type CoordDocStatus string

const (
    DocStatusDraft     CoordDocStatus = "draft"
    DocStatusPublished CoordDocStatus = "published"
    DocStatusArchived  CoordDocStatus = "archived"
)

type CoordinationDocument struct {
    ID             int64          `db:"id"`
    OrganizationID int64          `db:"organization_id"`
    Name           string         `db:"name"`
    AreaID         int64          `db:"area_id"`
    StartDate      time.Time      `db:"start_date"`
    EndDate        time.Time      `db:"end_date"`
    Status         CoordDocStatus `db:"status"`
    Sections       JSONMap        `db:"sections"`
    CreatedAt      time.Time      `db:"created_at"`
    UpdatedAt      time.Time      `db:"updated_at"`
}
```

### core/providers/ — Interfaces (contratos)

Define QUÉ necesita el dominio. No sabe CÓMO se implementa.

```go
// src/core/providers/coordination.go
package providers

import (
    "context"
    "alizia-api/src/core/entities"
)

type Coordination interface {
    GetDocument(ctx context.Context, orgID, docID int64) (*entities.CoordinationDocument, error)
    CreateDocument(ctx context.Context, doc *entities.CoordinationDocument) (int64, error)
    UpdateSections(ctx context.Context, docID int64, sections entities.JSONMap) error
    ListByArea(ctx context.Context, orgID, areaID int64) ([]entities.CoordinationDocument, error)
    SetTopics(ctx context.Context, docID int64, topicIDs []int64) error
    SetSubjects(ctx context.Context, docID int64, subjects []entities.CoordDocSubject) error
    CreateClasses(ctx context.Context, classes []entities.CoordDocClass) error
}
```

### core/providers/errors.go — Errores de dominio (extiende team-ai-toolkit)

```go
// src/core/providers/errors.go
package providers

import (
    bcerrors "github.com/educabot/team-ai-toolkit/errors"
)

// Re-export errores compartidos de team-ai-toolkit
var (
    ErrNotFound     = bcerrors.ErrNotFound
    ErrValidation   = bcerrors.ErrValidation
    ErrUnauthorized = bcerrors.ErrUnauthorized
    ErrForbidden    = bcerrors.ErrForbidden
    ErrDuplicate    = bcerrors.ErrDuplicate
)

// Errores ESPECÍFICOS de Alizia (no están en team-ai-toolkit)
var (
    ErrDocNotFound      = bcerrors.New("coordination document not found")
    ErrTopicMaxLevel    = bcerrors.New("topic exceeds max level")
    ErrSharedClassLimit = bcerrors.New("shared classes limit exceeded")
)
```

### core/usecases/ — Lógica de negocio

1 archivo = 1 operación. Solo depende de providers. **CERO HTTP, CERO DB**.

```go
// src/core/usecases/coordination/create_document.go
package coordination

import (
    "context"
    "fmt"
    "alizia-api/src/core/entities"
    "alizia-api/src/core/providers"
)

type CreateDocumentRequest struct {
    OrgID    int64
    Name     string
    AreaID   int64
    TopicIDs []int64
}

func (r CreateDocumentRequest) Validate() error {
    if r.Name == "" {
        return fmt.Errorf("%w: name is required", providers.ErrValidation)
    }
    return nil
}

type CreateDocument interface {
    Execute(ctx context.Context, req CreateDocumentRequest) (int64, error)
}

type createDocumentImpl struct {
    repo providers.Coordination
}

func NewCreateDocument(repo providers.Coordination) CreateDocument {
    return &createDocumentImpl{repo: repo}
}

func (uc *createDocumentImpl) Execute(ctx context.Context, req CreateDocumentRequest) (int64, error) {
    if err := req.Validate(); err != nil {
        return 0, err
    }

    doc := &entities.CoordinationDocument{
        OrganizationID: req.OrgID,
        Name:           req.Name,
        AreaID:         req.AreaID,
        Status:         entities.DocStatusDraft,
    }

    id, err := uc.repo.CreateDocument(ctx, doc)
    if err != nil {
        return 0, fmt.Errorf("create document: %w", err)
    }

    if len(req.TopicIDs) > 0 {
        if err := uc.repo.SetTopics(ctx, id, req.TopicIDs); err != nil {
            return 0, fmt.Errorf("set topics: %w", err)
        }
    }

    return id, nil
}
```

### entrypoints/rest/ — HTTP handlers (usan web.Request de team-ai-toolkit)

```go
// src/entrypoints/rest/coordination/create.go
package coordination

import (
    "net/http"
    "github.com/educabot/team-ai-toolkit/web"
    "github.com/educabot/team-ai-toolkit/tokens"
    "alizia-api/src/entrypoints/rest"
    coorduc "alizia-api/src/core/usecases/coordination"
)

type CreateHandler struct {
    useCase coorduc.CreateDocument
}

func NewCreate(uc coorduc.CreateDocument) *CreateHandler {
    return &CreateHandler{useCase: uc}
}

func (h *CreateHandler) Handle() web.Handler {
    return func(req web.Request) web.Response {
        claims := tokens.MustClaims(req)

        var body CreateDocumentRequest
        if err := req.Bind(&body); err != nil {
            return web.Err(http.StatusBadRequest, "invalid_request", err.Error())
        }

        id, err := h.useCase.Execute(req.Context(), coorduc.CreateDocumentRequest{
            OrgID:    claims.OrgID,
            Name:     body.Name,
            AreaID:   body.AreaID,
            TopicIDs: body.TopicIDs,
        })
        if err != nil {
            return rest.HandleError(err)
        }

        return web.Created(map[string]any{"id": id})
    }
}
```

### entrypoints/rest/rest.go — HandleError que extiende team-ai-toolkit

```go
// src/entrypoints/rest/rest.go
package rest

import (
    "github.com/educabot/team-ai-toolkit/errors"
    "github.com/educabot/team-ai-toolkit/web"
    "alizia-api/src/core/providers"
    "net/http"
)

// HandleError extiende team-ai-toolkit/errors.HandleError con errores específicos de Alizia.
func HandleError(err error) web.Response {
    switch {
    case errors.Is(err, providers.ErrDocNotFound):
        return web.Err(http.StatusNotFound, "doc_not_found", err.Error())
    case errors.Is(err, providers.ErrTopicMaxLevel):
        return web.Err(http.StatusBadRequest, "topic_max_level", err.Error())
    case errors.Is(err, providers.ErrSharedClassLimit):
        return web.Err(http.StatusBadRequest, "shared_class_limit", err.Error())
    default:
        // Delega al handler compartido de team-ai-toolkit
        return errors.HandleError(err)
    }
}
```

### repositories/ — Implementación con GORM

```go
// src/repositories/coordination/repository.go
package coordination

import "gorm.io/gorm"

type Repository struct {
    db *gorm.DB
}

func New(db *gorm.DB) *Repository {
    return &Repository{db: db}
}
```

```go
// src/repositories/coordination/get_document.go — CRUD simple con GORM
package coordination

import (
    "context"
    "fmt"
    "alizia-api/src/core/entities"
    "alizia-api/src/core/providers"
)

func (r *Repository) GetDocument(ctx context.Context, orgID, docID int64) (*entities.CoordinationDocument, error) {
    var doc entities.CoordinationDocument
    err := r.db.WithContext(ctx).
        Where("organization_id = ? AND id = ?", orgID, docID).
        First(&doc).Error
    if err != nil {
        return nil, fmt.Errorf("%w: id=%d", providers.ErrDocNotFound, docID)
    }
    return &doc, nil
}

// Para queries complejas (JOINs de 8+ tablas), se usa Raw SQL:
func (r *Repository) GetDocumentFull(ctx context.Context, orgID, docID int64) (*entities.CoordinationDocumentFull, error) {
    var doc entities.CoordinationDocumentFull
    err := r.db.WithContext(ctx).Raw(`
        SELECT cd.id, cd.name, cd.status, cd.sections,
               cd.start_date, cd.end_date, cd.created_at, cd.updated_at,
               a.id AS area_id, a.name AS area_name
        FROM coordination_documents cd
        JOIN areas a ON a.id = cd.area_id
        WHERE cd.organization_id = ? AND cd.id = ?
    `, orgID, docID).Scan(&doc).Error
    if err != nil {
        return nil, fmt.Errorf("%w: id=%d", providers.ErrDocNotFound, docID)
    }
    return &doc, nil
}
```

---

## Dependencias (go.mod)

```
module alizia-api

go 1.26

require (
    github.com/educabot/team-ai-toolkit  v1.x.x    // Infra compartida
    gorm.io/gorm                         v1.25.x   // ORM (estándar de la empresa)
    gorm.io/driver/postgres              v1.5.x    // PostgreSQL driver para GORM
    github.com/golang-migrate/migrate    v4.x.x    // DB migrations
    github.com/stretchr/testify          v1.9.x    // Testing
    github.com/Azure/azure-sdk-for-go/sdk/ai/azopenai  // Azure OpenAI
)
```

**6 dependencias directas.** web/, boot/, tokens/, errors/, pagination/ vienen transitivamente de team-ai-toolkit.

---

## Testing

### Coverage target: 80%

### Estructura por capa

```
core/usecases/coordination/
├── create_document.go
├── create_document_test.go      # Unit test: mock providers

repositories/coordination/
├── get_document.go
├── get_document_test.go         # Integration test: PostgreSQL real

entrypoints/rest/coordination/
├── create.go
├── create_test.go               # Test: mock usecase
```

---

## Linting, CI/CD, Makefile, Dockerfile, Docker Compose

(Sin cambios respecto a la versión anterior — ver secciones de .golangci.yml, GitHub Actions, Makefile, Dockerfile y docker-compose.yml en el documento original)

---

## Resumen de decisiones

### De ai-assistant tomamos:
1. **DI manual** (no Wire) → transparente, sin herramienta deprecated
2. **DI separado por archivos** → repositories.go, usecases.go, handlers.go (no 1 archivo gigante)
3. **Config como struct inmutable** (no singleton) → testeable
4. **Abstracción HTTP** (`web/` + `web/gin/`) → framework intercambiable (ahora en team-ai-toolkit)
5. **Sentinel errors + fmt.Errorf %w** → Go estándar sin librería custom
6. **Graceful degradation** → Bugsnag opcional, AI failable

### De tich-cronos tomamos:
7. **Clean Architecture** → entities, providers, usecases, entrypoints, repositories
8. **1 archivo = 1 operación** en usecases → granularidad fina
9. **Containers** para agrupar handlers por feature
10. **Provider interfaces** → desacopla dominio de infraestructura
11. **Testing robusto** → 80% coverage, PostgreSQL real en integration, mocks
12. **GolangCI Lint** → 15+ linters, pre-commit hooks
13. **Migraciones up/down** → rollback posible
14. **Hot reload con Air** → desarrollo rápido
15. **CI completo** → test + lint + coverage + deploy
16. **Error codes en respuesta** → frontend puede actuar programáticamente
17. **Swagger/OpenAPI** → documentación de API validada en CI
18. **Multi-tenancy via middleware** → org_id desde JWT
19. **GORM** → estándar de la empresa, equipo ya lo conoce
20. **`src/app/`** → separación de rutas

### Nuevo en esta arquitectura:
21. **team-ai-toolkit** → librería compartida con toda la infra reutilizable
22. **GORM** → estándar de la empresa, equipo ya lo conoce
23. **`cmd/` separado** → 1 archivo por responsabilidad del wiring
24. **`src/mocks/`** → fuera de cualquier capa, mockea todo
25. **ErrorTracker abstracto** → Bugsnag hoy, reemplazable mañana
26. **Config embebe BaseConfig** → campos comunes vienen de team-ai-toolkit
27. **errors.go extiende** → errores compartidos + errores específicos del proyecto
28. **Railway** → container Docker, auto-deploy, sin vendor lock-in, sin cold starts

---

## Alternativa futura: sqlx

Esta sección documenta los beneficios de migrar de GORM a sqlx si en el futuro las queries complejas dominan el proyecto. **No es una acción inmediata**, es un análisis para tener documentado si el equipo lo necesita.

### ¿Qué es sqlx?

sqlx es un wrapper sobre `database/sql` que agrega mapeo automático de rows a structs (sin `row.Scan` manual) pero sin generar SQL. Vos escribís el SQL, sqlx lo ejecuta y mapea.

### ¿Cuándo tendría sentido migrar?

- Si más del 50% de los repositories usan `db.Raw()` (señal de que GORM no alcanza)
- Si se detectan queries N+1 causando problemas de performance en producción
- Si el debugging de queries GORM se vuelve un cuello de botella del equipo

### Beneficios de sqlx vs GORM

| Aspecto | GORM (actual) | sqlx (alternativa) |
|---|---|---|
| **SQL explícito** | GORM genera SQL, no siempre ves qué ejecuta | Vos escribís el SQL, siempre sabés qué corre |
| **Performance** | Reflexión en runtime (~15-20% overhead) | Zero reflexión, performance igual a database/sql |
| **Debugging** | Difícil saber qué query generó GORM | Ves el SQL exacto en archivos .sql |
| **JOINs complejos** | Caés a `db.Raw()` | Naturales (es SQL directo) |
| **N+1** | Posible si olvidás Preload | Imposible (vos escribís la query) |
| **Code review** | `.Where().Preload().Find()` es difícil de revisar | SQL en archivos .sql, reviewable línea por línea |
| **Curva de aprendizaje** | Aprender API de GORM | Si sabés SQL, sabés sqlx |

### Beneficios de GORM vs sqlx (por qué lo usamos hoy)

| Aspecto | GORM (actual) | sqlx (alternativa) |
|---|---|---|
| **CRUD simple** | 1 línea: `db.Create(&user)` | Escribir INSERT completo |
| **Equipo** | Ya lo conocen | Curva de aprendizaje |
| **Soft deletes** | Automático con `gorm.DeletedAt` | Manual: `WHERE deleted_at IS NULL` |
| **Hooks** | BeforeCreate, AfterUpdate, etc. | No existen, lógica en usecase |
| **Relaciones** | Preload automático | JOINs manuales |
| **Migraciones dev** | AutoMigrate desde structs | Solo SQL |

### Cómo sería la migración

La arquitectura Clean ya separa repositories del resto. Migrar de GORM a sqlx solo tocaría `src/repositories/`. Ningún usecase, handler, o entity cambia.

```
Hoy (GORM):
  repository.go → db.Where().First(&doc)

Mañana (sqlx):
  repository.go → db.GetContext(ctx, &doc, getDocumentSQL, orgID, docID)
  queries/get_document.sql → SELECT ... FROM ... WHERE ...
```

Los repositories implementan las mismas interfaces de `providers/`. El resto del sistema no se entera del cambio.

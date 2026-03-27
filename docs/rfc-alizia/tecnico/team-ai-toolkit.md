# team-ai-toolkit — Librería compartida de infraestructura Go

## Qué es

Módulo Go reutilizable (`github.com/educabot/team-ai-toolkit`) que contiene toda la infraestructura común entre los proyectos backend de Educabot. Cualquier proyecto nuevo importa `team-ai-toolkit` y arranca con: servidor HTTP, auth JWT (via team-ai-toolkit/tokens JWKS), conexión a DB, logging, paginación, errores estandarizados y abstracción de framework.

> **NOTA:** Alizia y tich-cronos usan **JWT authentication via team-ai-toolkit/tokens**. El auth-service propio descrito en este documento es un **plan futuro**. El diagrama de ecosistema a continuación muestra la arquitectura futura; la arquitectura actual usa JWT via team-ai-toolkit/tokens en lugar del auth-service.

**No contiene lógica de dominio.** Solo infraestructura que no depende de ningún proyecto específico.

---

## Contexto: Ecosistema Educabot

```
                    ┌──────────────────────┐
                    │  JWT Auth Service     │  ← Autenticación via JWT
                    │  (team-ai-toolkit/   │
                    │   tokens)             │
                    │  - JWT (JWKS)         │
                    │  - Bearer tokens      │
                    │                      │
                    │  (Futuro: auth-service│
                    │   propio centraliza   │
                    │   emisión de tokens)  │
                    └──────────┬───────────┘
                               │
                               │ JWT firmado
                               │
          ┌────────────────────┼─────────────────────┐
          │                    │                      │
          ▼                    ▼                      ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│    Alizia       │  │  tich-cronos    │  │  Futuro proyecto │
│   (monolito)    │  │  (refactorizado)│  │                 │
│                 │  │                 │  │                 │
│  DB: alizia_db  │  │  DB: cronos_db  │  │  DB: propia     │
└────────┬────────┘  └────────┬────────┘  └────────┬────────┘
         │                    │                     │
         └────────────────────┼─────────────────────┘
                              │
                              ▼
                    ┌──────────────────────┐
                    │    team-ai-toolkit        │  ← Esta librería
                    │                      │
                    │  Importada por todos  │
                    │  los proyectos como   │
                    │  dependencia Go       │
                    └──────────────────────┘
```

**3 repos separados:**

| Repo | Tipo | Propósito |
|------|------|-----------|
| `educabot/auth-service` | Microservicio (futuro, no en uso) | Planificado para centralizar emisión de JWT en el futuro. Emitirá y gestionará JWT con base de datos propia |
| `educabot/team-ai-toolkit` | Librería Go (no se deploya) | Infraestructura compartida. Se importa en `go.mod` |
| `educabot/alizia-api` | Monolito (deploy propio) | Plataforma Alizia. Importa team-ai-toolkit |
| `educabot/tich-cronos` | Monolito (deploy propio) | Plataforma TiCh. Importa team-ai-toolkit |

---

## Autenticación actual — JWT via team-ai-toolkit/tokens

### Qué se usa hoy

Alizia y tich-cronos usan **JWT authentication via team-ai-toolkit/tokens**. El sistema de autenticación emite tokens JWT, y expone un endpoint JWKS para validación.

Los backends validan los JWT usando **JWKS** (JSON Web Key Set) via `team-ai-toolkit/tokens`. No se necesita una RSA key pair propia.

```
Login (1 vez)
  → Sistema de auth devuelve JWT
    → Frontend guarda JWT
      → Cada request envía JWT en Authorization header
        → Backend valida JWT via JWKS (cached, sin HTTP en cada request)
          → Extrae user_id, org_id, roles del token
```

### Auth Service propio (FUTURO)

> El auth-service propio está planificado para centralizar la emisión de tokens a futuro. No es necesario para el lanzamiento de Alizia. Ver ARQUITECTURA-AUTH-SERVICE.md para los detalles del diseño futuro.

---

## team-ai-toolkit — Estructura de la librería

```
team-ai-toolkit/
│
├── web/                                 # Abstracción HTTP framework-agnostic
│   ├── request.go                       # Request interface
│   │                                    #   Param(), Query(), Header(), Body()
│   │                                    #   Bind(), Set(), Get(), Next()
│   ├── response.go                      # Response struct
│   │                                    #   JSON(status, body), Err(status, code, msg)
│   ├── handler.go                       # Handler func(Request) Response
│   ├── interceptor.go                   # Interceptor func(Request) Response (middleware)
│   ├── error.go                         # Error response helpers
│   │
│   └── gin/                             # Adaptador Gin (reemplazable por chi/, echo/, etc.)
│       ├── handler.go                   # Adapt(web.Handler) → gin.HandlerFunc
│       ├── request.go                   # GinRequest implementa web.Request
│       ├── middleware.go                # AdaptMiddleware(web.Interceptor) → gin.HandlerFunc
│       └── engine.go                    # Helpers
│
├── boot/                                # Bootstrap de servidor HTTP
│   ├── server.go                        # Server struct
│   │                                    #   NewServer(port, engine) → *Server
│   │                                    #   Run() — ListenAndServe con timeouts
│   │                                    #   Shutdown() — graceful con context timeout
│   └── gin.go                           # NewEngine(env, allowedOrigins) → *gin.Engine
│                                        #   Recovery, CORS, slog middleware, /health
│
├── dbconn/                              # Conexión a PostgreSQL
│   └── postgres.go                      # MustConnect(dsn) → *sqlx.DB
│                                        #   MaxOpenConns: 25, MaxIdleConns: 10
│                                        #   ConnMaxLifetime: 5min
│
├── tokens/                              # Validación JWT (JWKS o RSA public key)
│   ├── jwt.go                           # ValidateJWT(token, validator) → (*Claims, error)
│   │                                    #   Valida JWT via JWKS (o RSA public key futuro)
│   │                                    #   Verifica exp, iat
│   ├── jwks.go                          # NewJWKSValidator(domain, audience) → Validator
│   │                                    #   Descarga JWKS y cachea las keys
│   ├── claims.go                        # Claims struct
│   │                                    #   UserID int64, OrgID int64
│   │                                    #   Roles []string, Email string, Name string
│   ├── middleware.go                    # NewAuthInterceptor(validator) → web.Interceptor
│   │                                    #   Extrae Bearer token de Authorization header
│   │                                    #   Valida JWT via JWKS, inyecta Claims en context
│   │                                    #   Retorna 401 si falta o es inválido
│   ├── tenant.go                        # NewTenantInterceptor() → web.Interceptor
│   │                                    #   Lee OrgID del Claims ya validado
│   │                                    #   Lo inyecta en context para multi-tenancy
│   ├── roles.go                         # RequireRole(roles...) → web.Interceptor
│   │                                    #   Chequea que Claims.Roles contenga al menos 1
│   │                                    #   Retorna 403 si no tiene permisos
│   └── context.go                       # MustClaimsFromContext(req) → Claims
│                                        #   UserIDFromContext(req) → int64
│                                        #   OrgIDFromContext(req) → int64
│
├── applog/                              # Logging con slog
│   ├── logger.go                        # Setup(env string)
│   │                                    #   prod/staging → JSON a stdout
│   │                                    #   local/develop → text con colores
│   └── test_logger.go                   # SetupTest() — logger silencioso para tests
│
├── pagination/                          # Paginación
│   ├── pagination.go                    # Pagination struct {Page, PerPage, Offset()}
│   │                                    #   ParseFromQuery(req web.Request) → Pagination
│   │                                    #   Defaults: page=1, per_page=20, max=100
│   └── response.go                      # PaginatedResponse[T] {Data, Total, Page, PerPage}
│
├── transactions/                        # Transacciones con sqlx
│   ├── transactor.go                    # RunInTx(ctx, db, func(tx) error) error
│   │                                    #   Begin → fn(tx) → Commit o Rollback
│   ├── dbtx.go                          # DBTX interface
│   │                                    #   GetContext, SelectContext, ExecContext
│   │                                    #   Implementado por *sqlx.DB y *sqlx.Tx
│   └── mock.go                          # MockDBTX para tests
│
├── errors/                              # Errores compartidos + mapeo HTTP
│   ├── errors.go                        # Sentinel errors comunes
│   │                                    #   ErrNotFound, ErrValidation, ErrUnauthorized
│   │                                    #   ErrForbidden, ErrDuplicate, ErrConflict
│   └── handler.go                       # HandleError(err) → web.Response
│                                        #   errors.Is() → mapea a HTTP status + code
│                                        #   not_found → 404
│                                        #   validation_error → 400
│                                        #   unauthorized → 401
│                                        #   forbidden → 403
│                                        #   duplicate → 409
│                                        #   default → 500 + log
│
├── config/                              # Helpers de configuración
│   ├── env.go                           # EnvOr(key, fallback) string
│   │                                    #   MustEnv(key) string — panic si falta
│   └── base.go                          # BaseConfig struct
│                                        #   Port, Env, DatabaseURL, JWKSDomain, JWKSAudience
│                                        #   AllowedOrigins []string
│                                        #   LoadBase() → BaseConfig
│
├── go.mod                               # module github.com/educabot/team-ai-toolkit
└── go.sum
```

---

## Dependencias de team-ai-toolkit

```
require (
    github.com/gin-gonic/gin        v1.10.x
    github.com/jmoiron/sqlx          v1.4.x
    github.com/lib/pq                v1.10.x
    github.com/golang-jwt/jwt/v5     v5.x.x
)
```

4 dependencias. Minimalista.

---

## Cómo lo importa cada proyecto

### Alizia

```go
// go.mod
module github.com/educabot/alizia-api

require github.com/educabot/team-ai-toolkit v1.x.x
```

```go
// config/config.go
package config

import bcfg "github.com/educabot/team-ai-toolkit/config"

type Config struct {
    bcfg.BaseConfig                     // Port, Env, DatabaseURL, JWKSDomain, JWKSAudience, AllowedOrigins
    AzureOpenAIKey      string
    AzureOpenAIEndpoint string
    AzureOpenAIModel    string
    BugsnagAPIKey       string
}

func Load() *Config {
    base := bcfg.LoadBase()
    return &Config{
        BaseConfig:          base,
        AzureOpenAIKey:      bcfg.MustEnv("AZURE_OPENAI_API_KEY"),
        AzureOpenAIEndpoint: bcfg.MustEnv("AZURE_OPENAI_ENDPOINT"),
        AzureOpenAIModel:    bcfg.EnvOr("AZURE_OPENAI_MODEL", "gpt-5-mini"),
        BugsnagAPIKey:       os.Getenv("API_KEY_BUGSNAG"),
    }
}
```

```go
// cmd/app.go
import (
    "github.com/educabot/team-ai-toolkit/boot"
    "github.com/educabot/team-ai-toolkit/dbconn"
    "github.com/educabot/team-ai-toolkit/tokens"
    "github.com/educabot/team-ai-toolkit/applog"
)

func NewApp(cfg *config.Config) *App {
    applog.Setup(cfg.Env)
    db := dbconn.MustConnect(cfg.DatabaseURL)
    engine := boot.NewEngine(cfg.Env, cfg.AllowedOrigins)

    // Auth middleware — valida JWT via JWKS (team-ai-toolkit/tokens)
    validator, _ := tokens.NewJWKSValidator(cfg.JWKSDomain, cfg.JWKSAudience)
    authMw := tokens.NewAuthInterceptor(validator)
    tenantMw := tokens.NewTenantInterceptor()

    // ... wiring de repos, usecases, handlers
    server := boot.NewServer(cfg.Port, engine)
    return &App{db: db, server: server}
}
```

### tich-cronos (refactorizado)

```go
// go.mod
module tichacademy.com/tich-cronos

require github.com/educabot/team-ai-toolkit v1.x.x
```

```go
// config/config.go
package config

import bcfg "github.com/educabot/team-ai-toolkit/config"

type Config struct {
    bcfg.BaseConfig
    CanvasSigloClientID     string
    CanvasSigloClientSecret string
    CanvasSigloRedirectURI  string
    LLMOpenAIKey            string
    LLMOpenAIURL            string
    ContentGeneratorURL     string
    BugsnagAPIKey           string
}

func Load() *Config {
    base := bcfg.LoadBase()
    return &Config{
        BaseConfig:              base,
        CanvasSigloClientID:     bcfg.MustEnv("CANVAS_SIGLO_CLIENT_ID"),
        LLMOpenAIKey:            bcfg.MustEnv("LLM_OPENAI_API_KEY"),
        ContentGeneratorURL:     bcfg.MustEnv("CONTENT_GENERATOR_URL"),
        BugsnagAPIKey:           os.Getenv("API_KEY_BUGSNAG"),
        // ...
    }
}
```

```go
// cmd/app.go — mismo patrón que Alizia
import (
    "github.com/educabot/team-ai-toolkit/boot"
    "github.com/educabot/team-ai-toolkit/dbconn"
    "github.com/educabot/team-ai-toolkit/tokens"     // MISMA validación JWT JWKS
    "github.com/educabot/team-ai-toolkit/applog"
)
```

### Auth Service (FUTURO — no en uso actualmente)

> El auth-service es un plan futuro para centralizar la emisión de tokens. Actualmente se usa JWT via team-ai-toolkit/tokens.

```go
// auth-service/go.mod (FUTURO)
module github.com/educabot/auth-service

require github.com/educabot/team-ai-toolkit v1.x.x
```

```go
// Usará de team-ai-toolkit:
import (
    "github.com/educabot/team-ai-toolkit/boot"       // Server bootstrap
    "github.com/educabot/team-ai-toolkit/web"         // Handler abstraction
    "github.com/educabot/team-ai-toolkit/dbconn"      // PostgreSQL connection
    "github.com/educabot/team-ai-toolkit/applog"      // Logging
    "github.com/educabot/team-ai-toolkit/config"      // EnvOr(), MustEnv()
    "github.com/educabot/team-ai-toolkit/errors"      // ErrNotFound, HandleError()
    "github.com/educabot/team-ai-toolkit/pagination"  // Si tiene listados
)

// NO usará tokens/ (él CREARÁ los tokens, no los valida)
// En su lugar tendrá su propio paquete interno:
//   internal/jwt/issuer.go → SignJWT(claims, privateKey) → token string
```

---

## Qué va y qué NO va en team-ai-toolkit

### Va (infraestructura genérica)

| Paquete | Qué resuelve | Quién lo usa |
|---------|-------------|-------------|
| `web/` | Abstracción HTTP framework-agnostic | Todos |
| `web/gin/` | Adaptador Gin | Todos (hoy) |
| `boot/` | Server lifecycle, timeouts, shutdown | Todos |
| `dbconn/` | Conexión PostgreSQL con sqlx | Todos |
| `tokens/` | Validación JWT via JWKS (o RSA key futuro) | Alizia, tich-cronos, futuros |
| `applog/` | Setup de slog | Todos |
| `pagination/` | Parse page/per_page + response wrapper | Todos |
| `transactions/` | RunInTx(), DBTX interface | Todos |
| `errors/` | Sentinel errors + HandleError() | Todos |
| `config/` | EnvOr(), MustEnv(), BaseConfig | Todos |

### NO va (dominio específico)

| Cosa | Por qué NO | Dónde vive |
|------|-----------|------------|
| Entities/modelos | Cada proyecto tiene su dominio | `proyecto/src/core/entities/` |
| Providers/interfaces | Específicas del dominio | `proyecto/src/core/providers/` |
| Usecases | Lógica de negocio propia | `proyecto/src/core/usecases/` |
| Handlers | Endpoints propios | `proyecto/src/entrypoints/` |
| Repositories | Queries propias | `proyecto/src/repositories/` |
| Migraciones | Schema propio | `proyecto/db/migrations/` |
| Config struct completo | Cada proyecto tiene campos distintos | `proyecto/config/` |
| AI client | Alizia usa Azure OpenAI, cronos puede usar otro | `proyecto/src/repositories/ai/` |
| Mocks | Mockean interfaces propias del proyecto | `proyecto/src/mocks/` |
| JWT issuer (private key) | Solo el auth service (futuro) firmará tokens | `auth-service/internal/jwt/` (futuro) |
| Prompts/schemas AI | Contenido específico del producto | `proyecto/src/repositories/ai/prompts/` |

---

## Versionamiento

team-ai-toolkit usa **Go modules + semver**:

```
v1.0.0 → primera versión estable
v1.1.0 → se agrega pagination/response.go (backward compatible)
v1.2.0 → se agrega web/gin/engine.go (backward compatible)
v2.0.0 → se cambia firma de tokens.ValidateJWT (breaking change)
```

Los proyectos fijan la versión en `go.mod`:
```
require github.com/educabot/team-ai-toolkit v1.2.0
```

Actualizar es un `go get github.com/educabot/team-ai-toolkit@latest` + correr tests.

---

## Estructura final de los 4 repos

```
educabot/
├── team-ai-toolkit/                 # Librería compartida (no se deploya)
│   ├── web/                     #   Abstracción HTTP
│   ├── boot/                    #   Server bootstrap
│   ├── dbconn/                  #   PostgreSQL connection
│   ├── tokens/                  #   JWT validation (JWKS)
│   ├── applog/                  #   Logging
│   ├── pagination/              #   Paginación
│   ├── transactions/            #   Transacciones DB
│   ├── errors/                  #   Errores compartidos
│   └── config/                  #   Config helpers + BaseConfig
│
├── auth-service/                # Microservicio de autenticación (FUTURO — no en uso)
│   ├── cmd/                     #   Entry point
│   ├── internal/                #   JWT issuer (private key), bcrypt, sessions
│   ├── db/migrations/           #   organizations, users, user_roles, refresh_tokens
│   └── go.mod                   #   importa team-ai-toolkit
│
├── alizia-api/                  # Monolito Alizia (deploy propio)
│   ├── cmd/                     #   Entry point + DI manual
│   ├── src/                     #   core/, entrypoints/, repositories/, mocks/
│   ├── config/                  #   Config propio (extiende BaseConfig)
│   ├── db/migrations/           #   24 tablas de dominio educativo
│   └── go.mod                   #   importa team-ai-toolkit
│
└── tich-cronos/                 # Monolito TiCh refactorizado (deploy propio)
    ├── cmd/                     #   Entry point + DI manual (sin Wire)
    ├── src/                     #   core/, entrypoints/, repositories/, mocks/
    ├── config/                  #   Config propio (extiende BaseConfig)
    ├── db/migrations/           #   26 tablas de dominio educativo
    └── go.mod                   #   importa team-ai-toolkit
```

---

## Resumen

| Pregunta | Respuesta |
|----------|-----------|
| **¿Qué es team-ai-toolkit?** | Librería Go con infraestructura compartida |
| **¿Se deploya?** | No. Se importa como dependencia en `go.mod` |
| **¿Qué contiene?** | web/, boot/, dbconn/, tokens/, applog/, pagination/, transactions/, errors/, config/ |
| **¿Quién lo usa?** | Alizia, tich-cronos, auth-service, futuros proyectos |
| **¿Qué es auth-service?** | Microservicio propio planificado para el futuro. Actualmente se usa JWT via team-ai-toolkit/tokens |
| **¿Cómo se relacionan?** | El sistema de auth firma tokens. team-ai-toolkit/tokens/ los valida via JWKS. Los proyectos importan team-ai-toolkit |
| **¿Qué NO va?** | Lógica de dominio, entities, usecases, handlers, migraciones |
| **¿Cómo se versiona?** | Semver via Go modules (v1.0.0, v1.1.0, v2.0.0) |

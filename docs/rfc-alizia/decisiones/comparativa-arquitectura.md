# Comparativa Arquitectonica: ai-assistant vs tich-cronos vs Alizia

## Resumen Ejecutivo

| Aspecto | ai-assistant | tich-cronos | Alizia                                             |
|---------|-------------|-------------|----------------------------------------------------|
| **Go Version** | 1.25.0 | 1.23.7 | 1.25.8                                             |
| **LOC** | ~15,000 (estimado) | ~41,008 | Nuevo proyecto                                     |
| **Framework** | Gin (abstraido via `web/`) | Gin (directo) | Gin (abstraido via `web/` + `boot/`)               |
| **ORM/DB** | Raw SQL (`database/sql`) | GORM v1.25.11 | GORM v1.25.11                                 |
| **Base de datos** | SQLite WAL / PostgreSQL | PostgreSQL | PostgreSQL                                         |
| **DI** | Manual (1 archivo) | Google Wire (compile-time) | Manual (1 archivo por responsabilidad)             |
| **Deploy** | Docker Compose → VPS | Cloud Functions + local | Cloud Functions agrupadas (5 por módulo)           |
| **Auth** | Webhook secret simple | JWT + Bearer | JWT + Bearer (via team-ai-toolkit/tokens) |
| **Logging** | stdlib `log` | Interfaz custom + Bugsnag | slog (stdlib Go 1.21+) + Bugsnag                   |
| **Testing** | 56 archivos, 190+ tests | 80+ archivos, target 80% | Target 80%, PostgreSQL real, sin E2E               |
| **Linting** | `go vet` basico | GolangCI Lint (20 linters) | GolangCI Lint (15+ linters)                        |
| **Deps directas** | 5-6 | 25+ | 5 (+ team-ai-toolkit transitivas)                  |
| **Libreria compartida** | No | No | team-ai-toolkit (web, boot, tokens, errors, etc.)  |
| **AI Provider** | Claude/OpenAI (failover) | Azure OpenAI | Azure OpenAI                                       |
| **Arquitectura** | Layered pragmatico | Clean Architecture estricto | Clean Architecture pragmatico                      |

---

## 1. Estructura de Directorios

### ai-assistant
```
ai-assistant/
├── cmd/           # Entry point + wiring (main, server, clients, routes)
├── clients/       # Todos los clientes externos en 1 paquete flat
├── config/        # 1 archivo, env vars
├── pkg/
│   ├── domain/    # Modelos + errores + validacion (35 archivos, 1 paquete)
│   ├── controller/# HTTP handlers (20 controladores)
│   ├── usecase/   # Logica de negocio (15 archivos)
│   └── service/   # Acceso a datos
├── web/           # Abstraccion HTTP framework-agnostic
├── boot/          # Bootstrap del servidor
├── internal/      # hooks, skills, middleware
├── db/            # Migraciones embebidas
├── skills/        # Archivos .md con YAML frontmatter
└── test/          # Mocks centralizados
```

### tich-cronos
```
tich-cronos/
├── cmd/                    # Entry point local
├── src/
│   ├── app/               # Orquestacion (web, functions, router, e2e)
│   ├── core/              # Dominio puro
│   │   ├── entities/      # Modelos (26+ archivos)
│   │   ├── providers/     # Interfaces/contratos (23 interfaces)
│   │   │   └── mocks/     # Mocks auto-generados
│   │   ├── usecases/      # Logica (subdirectorios por feature)
│   │   └── scripts/       # Scripts de datos
│   ├── entrypoints/       # Containers + REST handlers
│   │   └── rest/          # Implementaciones REST por feature
│   ├── infrastructure/    # DI con Wire
│   ├── repositories/      # Implementaciones de providers
│   └── utils/             # Utilidades compartidas
├── packages/              # Paquetes de infraestructura reutilizables
├── config/                # Config singleton
├── db/migrations/         # 46 migraciones SQL (up/down)
├── docs/                  # Swagger/OpenAPI
└── test/                  # Setup E2E
```

### Alizia (usa team-ai-toolkit)
```
alizia-api/
├── cmd/                   # Entry point + DI manual (1 archivo por responsabilidad)
│   ├── main.go            # config → NewApp() → Run()
│   ├── app.go             # App struct, lifecycle, graceful shutdown
│   ├── repositories.go    # Crea repos
│   ├── usecases.go        # Crea usecases
│   ├── handlers.go        # Crea handlers + containers
│   └── routes.go          # Rutas condicionales dev
├── src/
│   ├── app/               # Rutas por modo de deploy (web/mapping.go, functions/)
│   ├── core/              # Dominio puro
│   │   ├── entities/      # Modelos puros (structs + enums)
│   │   ├── providers/     # Interfaces + errors (extiende team-ai-toolkit/errors)
│   │   └── usecases/      # 1 archivo = 1 operacion
│   ├── entrypoints/       # Containers + REST handlers (usa team-ai-toolkit/web)
│   ├── repositories/      # sqlx + queries/ embebidas
│   ├── mocks/             # Mocks de TODAS las capas (providers + usecases)
│   └── utils/
├── config/                # Embebe team-ai-toolkit/config.BaseConfig + campos propios
├── db/migrations/         # SQL up + down
└── docs/                  # Swagger/OpenAPI

NO tiene (viene de team-ai-toolkit):
  web/, boot/, packages/ (tokens, dbconn, applog, pagination, transactions, errors)
```

### team-ai-toolkit (librería compartida)
```
team-ai-toolkit/
├── web/                   # Abstraccion HTTP (Request, Response, Handler)
│   └── gin/               # Adaptador Gin (Adapt, AdaptMiddleware)
├── boot/                  # Server bootstrap (NewEngine, NewServer, Shutdown)
├── tokens/                # JWT validation (JWKS) + middleware + claims
├── dbconn/                # PostgreSQL connection con sqlx
├── errors/                # Sentinel errors + HandleError()
├── pagination/            # ParseFromQuery + PaginatedResponse
├── transactions/          # RunInTx(), DBTX interface
├── applog/                # slog setup + ErrorTracker interface
│   └── bugsnag/           # Bugsnag adapter (reemplazable)
└── config/                # EnvOr(), MustEnv(), BaseConfig
```

### Analisis comparativo

| Criterio | ai-assistant | tich-cronos | Alizia |
|----------|-------------|-------------|--------|
| **Profundidad** | Plana (2-3 niveles) | Profunda (4-5 niveles) | Media (3-4 niveles) |
| **Granularidad** | 1 paquete por capa | 1 paquete por feature por capa | 1 paquete por feature por capa |
| **Navegabilidad** | Facil, todo junto | Requiere conocer la convencion | Estructura reconocible, menos archivos |
| **Escalabilidad** | Limitada | Alta | Alta |
| **Separacion de capas** | Suave (mismo paquete) | Estricta (compilador enforce) | Estricta (compilador enforce) |

**Alizia toma:**
- De ai-assistant: `boot/`, `web/`, DI manual separado por archivos → ahora en team-ai-toolkit
- De tich-cronos: `core/`, `entrypoints/`, `repositories/`
- Nuevo: `mocks/` fuera de cualquier capa, `cmd/` con 1 archivo por responsabilidad, team-ai-toolkit como librería compartida

---

## 2. Entry Points y Bootstrap

### ai-assistant
- **1 modo**: servidor HTTP
- Bootstrap en `NewApp()`: config → clients → services → controllers → routes
- `boot/` separa la creacion del engine

### tich-cronos
- **Dual**: servidor local + Cloud Functions (55+ funciones)
- Cada funcion tiene su propio router Gin aislado
- Wire genera containers para ambos modos

### Alizia
- **Dual potencial**: web server (primario) + Cloud Functions (a futuro)
- `team-ai-toolkit/boot` crea engine + server con timeouts y graceful shutdown
- `src/app/web/mapping.go` registra rutas separado de boot
- `cmd/app.go` orquesta todo

| Criterio | ai-assistant | tich-cronos | Alizia |
|----------|-------------|-------------|----------|
| **Complejidad boot** | Baja | Media (dual path) | Baja-media (boot/ separado) |
| **Flexibilidad deploy** | Solo Docker | Cloud Functions + local | Cloud Functions agrupadas (5 funciones) |
| **Cold start** | N/A | Relevante (55+ funciones) | Relevante pero solo 5 funciones |
| **Graceful shutdown** | Signal handler | Gin default | Explicito en boot/server.go |

**Alizia toma:**
- De ai-assistant: `boot/` como paquete separado → ahora en team-ai-toolkit
- De tich-cronos: dual deploy (web + functions), estructura `src/app/`
- Nuevo: Cloud Functions agrupadas por módulo (5 funciones, no 55+), boot/ compartido via librería

---

## 3. Dependency Injection

### ai-assistant: Manual, 1 archivo
```go
func NewApp(cfg config.Config) *App {
    cl := NewClients(cfg)
    memorySvc := NewMemoryService(cfg)
    ctrls := NewControllers(cl, cfg, memorySvc, ...)
    return &App{...}
}
```

### tich-cronos: Google Wire
```go
var repositorySet = wire.NewSet(
    usersr.New,
    wire.Bind(new(providers.User), new(*usersr.Repository)),
)
// wire_gen.go generado automaticamente
```

### Alizia: Manual, 1 archivo por responsabilidad
```go
// cmd/repositories.go → cmd/usecases.go → cmd/handlers.go
repos := NewRepositories(cfg, db)
usecases := NewUseCases(repos, cfg)
container := NewHandlers(usecases, cfg)
```

| Criterio | ai-assistant | tich-cronos | Alizia |
|----------|-------------|-------------|----------|
| **Transparencia** | Total | Parcial (generado) | Total |
| **Mantenimiento** | 1 archivo crece | Wire gen + conflicts | Distribuido en 3 archivos |
| **Type safety** | Compile-time | Compile-time | Compile-time |
| **Escalabilidad** | Se complica | Escala con Wire sets | Escala (1 archivo por paso) |
| **Herramienta externa** | No | Wire (deprecated) | No |

**Alizia toma:**
- De ai-assistant: DI manual sin framework externo
- De tich-cronos: containers que agrupan features
- Nuevo: separar en repositories.go → usecases.go → handlers.go (no un solo archivo gigante)

---

## 4. Acceso a Datos

### ai-assistant: Raw SQL + database/sql
- `go:embed` para archivos .sql
- `database/sql` directo, `row.Scan` manual
- Dual backend: SQLite WAL + PostgreSQL

### tich-cronos: GORM
- ORM completo con reflection
- PostgreSQL exclusivo
- Transactor pattern custom

### Alizia: sqlw (punto medio)
- `go:embed` para archivos .sql (de ai-assistant)
- Mapeo automatico a structs sin reflection (sin `row.Scan`)
- PostgreSQL exclusivo
- Transactor con `RunInTx()` (de tich-cronos simplificado)

| Criterio | ai-assistant | tich-cronos | Alizia |
|----------|-------------|-------------|--------|
| **Control SQL** | Total | Parcial | Total |
| **Boilerplate** | Alto (row.Scan) | Bajo (GORM) | Bajo (sqlx mapea auto) |
| **Performance** | Optima | Buena (reflection) | Optima (zero reflection) |
| **Debugging** | Ves SQL exacto | Dificil | Ves SQL exacto |
| **Queries complejas** | Naturales | Caes a Raw SQL | Naturales |
| **Migraciones** | Solo up | up + down | up + down |
| **Transacciones** | Manual | Transactor pattern | RunInTx() simplificado |

**Alizia toma:**
- De ai-assistant: SQL embebido con `go:embed`, control total
- De tich-cronos: migraciones up/down, connection pooling, transactor
- Nuevo: sqlx elimina `row.Scan` sin agregar reflection de GORM

---

## 5. Error Handling

### ai-assistant: Custom Wrap/Wrapf
- 50+ sentinel errors, wrapping propio

### tich-cronos: Switch por handler
- errors.Is() + switch repetitivo en cada handler

### Alizia: HandleError() centralizado
- Sentinel errors en `providers/errors.go`
- `fmt.Errorf("%w")` estandar (no custom wrapper)
- `HandleError()` centralizado que mapea error → HTTP status + code

| Criterio | ai-assistant | tich-cronos | Alizia |
|----------|-------------|-------------|----------|
| **Wrapping** | Custom Wrap/Wrapf | Go estandar | Go estandar (fmt.Errorf %w) |
| **Mapeo HTTP** | En cada controller | Switch en cada handler | HandleError() centralizado |
| **Error codes** | No | Si (alfanumericos) | Si (estandarizados) |
| **Repeticion** | Baja | Alta (switch repetido) | Minima (1 funcion) |

**Alizia toma:**
- De ai-assistant: sentinel errors granulares
- De tich-cronos: error codes en response para frontend
- Nuevo: `HandleError()` centralizado, `fmt.Errorf("%w")` estandar

---

## 6. HTTP Layer y API Design

### ai-assistant: Abstraccion `web/` + `web/gin/`
- Handlers retornan `web.Response`, reciben `web.Request`
- Gin adapter en `web/gin/`
- Portable pero nadie lo usa en la practica

### tich-cronos: Gin directo
- `gin.Context` en todos los handlers
- Lock-in a Gin
- Rapido de escribir

### Alizia: Abstraccion via team-ai-toolkit
- `team-ai-toolkit/web` para handler/request/response generico
- `team-ai-toolkit/boot` para server lifecycle
- `team-ai-toolkit/web/gin` para el adaptador Gin
- Handlers usan `web.Request`/`web.Response`, nunca `gin.Context`
- `webgin.Adapt()` en mapping.go convierte a Gin

| Criterio | ai-assistant | tich-cronos | Alizia |
|----------|-------------|-------------|----------|
| **Acoplamiento framework** | Bajo | Alto | Bajo |
| **Cambiar de Gin** | Cambiar `web/gin/` | Tocar todos los handlers | Cambiar `web/gin/` + `boot/gin.go` |
| **Productividad** | Media | Alta | Media-alta |
| **Testing handlers** | Mock Request | httptest + gin context | Mock Request |
| **Server lifecycle** | En `boot/` | En `src/app/web/` | En `boot/` (separado de rutas) |

**Alizia toma:**
- De ai-assistant: `web/` + `boot/` → extraidos a team-ai-toolkit (reutilizable entre proyectos)
- De tich-cronos: mapping.go centralizado para rutas
- Nuevo: infra HTTP compartida via librería, `boot/` maneja el COMO, `mapping.go` maneja el QUE

---

## 7. Configuracion

| Criterio | ai-assistant | tich-cronos | Alizia |
|----------|-------------|-------------|----------|
| **Pattern** | Struct inmutable | Singleton global | Struct embebe team-ai-toolkit/BaseConfig |
| **Loader** | `os.Getenv()` puro | godotenv + singleton | team-ai-toolkit: `MustEnv()` + `EnvOr()` |
| **Validacion** | Ninguna | Minima | `mustEnv()` panic si falta |
| **Testabilidad** | Pasas Config | Singleton dificulta | Pasas *Config |
| **Dev experience** | Exportar vars manual | `.env.local` auto | docker-compose env / direnv |

**Alizia toma:**
- De ai-assistant: struct inmutable, sin singleton, sin godotenv
- De tich-cronos: carpeta `config/` separada, soporte multi-ambiente
- Nuevo: `BaseConfig` en team-ai-toolkit con campos comunes (Port, Env, DatabaseURL, JWKSDomain, JWKSAudience, BugsnagAPIKey), cada proyecto embebe y agrega los suyos

---

## 8. Testing

| Criterio | ai-assistant | tich-cronos | Alizia |
|----------|-------------|-------------|----------|
| **Coverage target** | No definido | 80% | 80% |
| **Mocks ubicacion** | `test/mocks.go` (centralizado) | `providers/mocks/` (dentro de capa) | `src/mocks/` (fuera de capas) |
| **Mocks alcance** | Solo repos | Solo providers | Providers + usecases + lo que sea |
| **DB tests** | SQLite in-memory | PostgreSQL Docker | PostgreSQL Docker |
| **E2E** | No | Si (httpexpect) | No (de momento) |
| **CI** | test + build | test + lint + coverage | test + lint + coverage |
| **Linting** | `go vet` | 20 linters | 15+ linters |
| **Pre-commit** | No | Si | Si |

**Alizia toma:**
- De ai-assistant: sin E2E (de momento), race detection
- De tich-cronos: 80% coverage, PostgreSQL real, golangci-lint, pre-commit hooks
- Nuevo: `src/mocks/` fuera de cualquier capa (mockea providers, usecases, lo que sea)

---

## 9. Build, Deploy y CI/CD

| Criterio | ai-assistant | tich-cronos | Alizia |
|----------|-------------|-------------|----------|
| **Dev server** | `make run` | `make run` (Air) | `make run` (Air) |
| **CI pipelines** | 1 workflow | 5 workflows | 3 workflows (test, lint, deploy) |
| **Deploy target** | Docker → VPS | Cloud Functions (55+ por endpoint) | Cloud Functions agrupadas (5 por módulo) |
| **Scaling** | Manual | Auto (per-function) | Auto (per-container) |
| **Cold starts** | N/A | Si | Minimo (min instances) |
| **Hot reload** | No | Si (Air) | Si (Air) |
| **API docs validation** | No | Si (Swagger CI) | Si (Swagger CI) |
| **Pre-commit** | No | Si | Si |
| **Vendor lock-in** | Ninguno | Alto (Cloud Functions) | Bajo (container estandar) |

**Alizia toma:**
- De ai-assistant: deploy portable (Docker container)
- De tich-cronos: Air, pre-commit hooks, Swagger validation
- Nuevo: Cloud Functions agrupadas por módulo (5 funciones, mejora sobre las 55+ de tich-cronos)

---

## 10. Integraciones Externas

| Criterio | ai-assistant | tich-cronos | Alizia |
|----------|-------------|-------------|----------|
| **Cantidad** | 14 (paquete flat) | 5 (paquetes separados) | 1 principal (Azure OpenAI) |
| **Patron** | clients/ flat | repositories/ por feature | repositories/ai/ con prompts/ y schemas/ |
| **Interfaces** | No (directo) | Si (providers) | Si (providers.AIClient) |
| **Failover** | Si (primary → fallback) | No | No (de momento) |
| **Prompts** | Inline en codigo | Archivos separados | Archivos embebidos (.txt) |

**Alizia toma:**
- De ai-assistant: posibilidad de agregar failover a futuro
- De tich-cronos: integraciones implementan interfaces, prompts/schemas separados
- Nuevo: prompts como archivos .txt embebidos (reviewables en PRs)

---

## 11. Concurrencia

| Criterio | ai-assistant | tich-cronos | Alizia |
|----------|-------------|-------------|----------|
| **Goroutines custom** | Si (cron, hooks, reminders) | No | Minimo (graceful shutdown) |
| **Connection pooling** | No (SQLite) | GORM (25/15) | sqlx (25/10) |
| **Transacciones** | Manual | Transactor pattern | RunInTx() |
| **Shutdown** | Signal handler + defer | Gin default | boot/server.go Shutdown() explicito |

---

## 12. Domain Modeling

| Criterio | ai-assistant | tich-cronos | Alizia |
|----------|-------------|-------------|----------|
| **Ubicacion modelos** | `pkg/domain/` (1 paquete, 35 archivos) | `core/entities/` (separado) | `core/entities/` (separado) |
| **Ubicacion interfaces** | `pkg/domain/` (mezclado) | `core/providers/` (separado) | `core/providers/` (separado) |
| **Ubicacion errores** | `pkg/domain/errors.go` (mezclado) | `core/providers/errors.go` | `core/providers/errors.go` |
| **Entities importan infra** | Tags GORM mezclados | Tags GORM | Solo tags `db:` (sqlx) |
| **Enums** | Constantes string | Custom types | Custom types |
| **Validacion** | En domain (`Validate()`) | En usecases | En usecases (request DTOs) |

**Alizia toma:**
- De ai-assistant: nada (dominio flat no escala)
- De tich-cronos: entities/ + providers/ separados, entities sin logica
- Nuevo: tags `db:` de sqlx son mas livianos que tags GORM

---

## 13. Tabla Comparativa Final

### ai-assistant - Top 5 Fortalezas
1. Simplicidad radical (5 deps, codigo directo)
2. Framework-agnostic (`web/` + `boot/`)
3. Graceful degradation (todo opcional)
4. SQL embebido (zero ORM overhead)
5. Deploy simple (Docker compose)

### tich-cronos - Top 5 Fortalezas
1. Clean Architecture estricto (compilador enforce)
2. Testing robusto (80%, E2E, PostgreSQL real)
3. CI completo (5 pipelines + pre-commit)
4. Containers agrupan features (Wire DI)
5. Multi-tenancy + Auth profesional (JWT via team-ai-toolkit/tokens)

### Alizia - Top 5 Fortalezas
1. Lo mejor de ambos (clean arch + simplicidad)
2. team-ai-toolkit: infra compartida entre proyectos (web, boot, tokens, errors, etc.)
3. sqlx: control de SQL sin boilerplate de `row.Scan`
4. DI manual legible (sin Wire deprecated)
5. Framework intercambiable via team-ai-toolkit (`web/` + `boot/`)

### Alizia - Posibles Riesgos
1. Mas archivos que ai-assistant (costo de Clean Architecture)
2. Abstraccion `web/` es overhead si nunca cambian de Gin
3. DI manual puede crecer mucho si suman 10+ modulos
4. Sin E2E tests (posible gap de confianza)
5. sqlx requiere escribir SQL a mano (mas lento que GORM para CRUDs simples)

---

## 14. Que tomo Alizia de cada proyecto

### De ai-assistant (6 decisiones):
1. **DI manual** — sin Wire deprecated
2. **SQL embebido** — `go:embed` + archivos `.sql`
3. **Config struct inmutable** — no singleton
4. **Abstraccion HTTP** — `web/` + `web/gin/`
5. **`boot/`** — server lifecycle separado
6. **Sentinel errors + fmt.Errorf %w** — Go estandar

### De tich-cronos (14 decisiones):
7. **Clean Architecture** — entities, providers, usecases, entrypoints, repositories
8. **1 archivo = 1 operacion** en usecases
9. **Containers** para agrupar handlers
10. **Provider interfaces** para desacoplar dominio
11. **Testing 80%** — PostgreSQL real, mocks, coverage en PRs
12. **GolangCI Lint 15+** — pre-commit hooks
13. **Migraciones up/down** — rollback posible
14. **Hot reload Air** — desarrollo rapido
15. **CI completo** — test + lint + coverage + deploy
16. **Error codes** — frontend puede actuar
17. **Swagger/OpenAPI** — validado en CI
18. **Multi-tenancy** — org_id desde JWT middleware
19. **Dual deploy** — web server + functions ready
20. **`src/app/`** — rutas separadas por modo de deploy

### Nuevo (5 decisiones):
21. **team-ai-toolkit** — librería compartida con toda la infra reutilizable (web, boot, tokens, errors, dbconn, pagination, transactions, applog, config)
22. **sqlx** — punto medio entre raw SQL y GORM
23. **`cmd/` separado** — 1 archivo por responsabilidad del wiring
24. **`src/mocks/`** — fuera de cualquier capa, mockea todo
25. **Cloud Functions agrupadas** — 5 funciones por módulo (admin, coordination, teaching, resources, ai)

### Descartado de ambos:
- ~~GORM~~ → sqlx
- ~~Wire~~ → DI manual
- ~~Singleton config~~ → struct inmutable
- Cloud Functions agrupadas por módulo (5 funciones, no 55+ ni Cloud Run)
- JWT auth via team-ai-toolkit/tokens se mantiene. Auth service propio es plan futuro
- ~~stdlib log~~ → slog
- Bugsnag se mantiene (stack de la empresa)
- ~~Custom error wrapping~~ → fmt.Errorf estandar
- ~~Handlers acoplados a Gin~~ → abstraccion web/

---

## 15. Conclusion

**ai-assistant** = **pragmatico minimalista**. Optimizado para 1 dev. Rapido de entender, dificil de escalar.

**tich-cronos** = **enterprise estricto**. Optimizado para equipos. Robusto pero con boilerplate y herramientas deprecated (Wire, GORM overhead).

**Alizia** = **clean pragmatico**. Toma la estructura y disciplina de tich-cronos, la simplicidad y portabilidad de ai-assistant, y agrega decisiones nuevas (team-ai-toolkit como librería compartida, sqlx, mocks centralizados, cmd separado) para un equipo de 4+ devs que necesita escalar sin ahogarse en boilerplate. La infra común (web, boot, tokens, errors, DB, logging) vive en team-ai-toolkit y se comparte entre Alizia, tich-cronos y futuros proyectos.

| Filosofia | ai-assistant | tich-cronos | Alizia |
|-----------|-------------|-------------|----------|
| **Principio** | KISS | Clean Architecture | Clean Architecture + KISS |
| **Optimizado para** | 1 dev | Equipo grande | Equipo mediano (4-8 devs) |
| **Trade-off** | Velocidad > estructura | Estructura > velocidad | Balance |

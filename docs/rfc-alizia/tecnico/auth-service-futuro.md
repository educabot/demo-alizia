# Auth Service — Microservicio de autenticación Educabot

> **NOTA: Este documento describe el auth-service propio planificado para el futuro. Alizia arranca con JWT authentication (via team-ai-toolkit/tokens). El auth-service NO es una dependencia bloqueante para el lanzamiento de Alizia.**

## Qué es

Microservicio Go planificado para centralizar la emisión de tokens en el futuro. Será el **único servicio que maneje credenciales y emita tokens**. Todos los demás proyectos (Alizia, tich-cronos, futuros) validarán tokens con la public key via team-ai-toolkit/tokens.

**Estado actual:** Alizia y tich-cronos usan JWT authentication (via team-ai-toolkit/tokens). Este auth-service es un plan futuro.

---

## Contexto: Qué reemplazará (FUTURO)

| Hoy (JWT via team-ai-toolkit/tokens — sistema actual) | Futuro (auth-service — planificado) |
|---|---|
| Login: JWT emitido por el sistema de autenticación actual | Login: `POST auth-service/auth/login` con bcrypt propio |
| Signup: gestionado externamente | Signup: `POST auth-service/auth/register` |
| JWT: firmado externamente, backends validan con JWKS via team-ai-toolkit/tokens | JWT: auth-service firma con private key RSA, backends validan con public key |
| Canvas OAuth: cronos intercambia code → crea usuario | Canvas OAuth: cronos intercambia code → crea usuario directo en auth-service |
| Refresh tokens: NO EXISTEN | Refresh tokens: rotación automática |
| Password reset: NO EXISTE | Password reset: email con token temporal |
| Rate limiting login: NO EXISTE | Rate limiting: 5 intentos en 15 min por email |
| Roles: hardcoded en DB de cronos | Roles: centralizados en auth-service, dinámicos por producto |

---

## Quién lo consume

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  tuni-ai-webapp  │     │  Alizia frontend │     │  Futuro frontend │
│  (React)         │     │  (React)         │     │                 │
└────────┬────────┘     └────────┬────────┘     └────────┬────────┘
         │                       │                        │
         │ Login, Register       │ Login, Register        │
         │ Canvas OAuth          │                        │
         ▼                       ▼                        ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Auth Service                              │
│                                                                  │
│  POST /auth/login         → JWT access + refresh token           │
│  POST /auth/register      → Crea usuario                        │
│  POST /auth/refresh       → Rota refresh token                   │
│  POST /auth/password-reset → Envía email                         │
│  POST /auth/password-reset/confirm → Cambia password             │
│  GET  /auth/me            → Info del usuario autenticado         │
│                                                                  │
│  POST /auth/canvas/oauth/callback → Canvas OAuth (solo TiCh)    │
│  POST /auth/canvas/login          → Canvas LTI init (solo TiCh) │
│  POST /auth/canvas/launch         → Canvas LTI launch (solo TiCh)│
│                                                                  │
│  POST /admin/organizations → Crear org (super admin)             │
│  POST /admin/users         → Crear usuario (admin de org)        │
│  PUT  /admin/users/:id/roles → Asignar roles                    │
│                                                                  │
│  DB: auth_db (organizations, users, user_roles, refresh_tokens,  │
│      login_attempts, password_reset_tokens)                      │
└──────────────────────────────┬──────────────────────────────────┘
                               │
         JWT firmado con       │ private key
         ──────────────────────┘
         │
         ▼ Validación con public key (team-ai-toolkit/tokens, ZERO HTTP calls)
┌────────────────┐  ┌────────────────┐  ┌────────────────┐
│  tich-cronos    │  │  alizia-api    │  │  Futuro backend │
│  (backend Go)   │  │  (backend Go)  │  │                │
└────────────────┘  └────────────────┘  └────────────────┘
```

---

## Stack

| Componente | Tecnología |
|---|---|
| Lenguaje | Go 1.26 |
| Infra compartida | team-ai-toolkit (web, boot, dbconn, errors, applog, config) |
| Base de datos | PostgreSQL (auth_db, separada de los productos) |
| DB driver | sqlx |
| Password hashing | bcrypt (golang.org/x/crypto/bcrypt) |
| JWT signing | RS256 con private key (golang-jwt/jwt/v5) |
| Email | SendGrid (para password reset) |
| Rate limiting | In-database (tabla login_attempts) |
| Deploy | Cloud Function individual (es 1 solo servicio, no necesita agrupar) |
| Canvas OAuth | Solo habilitado si env vars de Canvas están presentes |

---

## Base de datos (auth_db)

```sql
-- Enums
CREATE TYPE member_role AS ENUM ('student', 'supervisor', 'teacher', 'coordinator', 'admin');

-- Tenants
CREATE TABLE organizations (
    id          BIGSERIAL PRIMARY KEY,
    name        VARCHAR(255) NOT NULL,
    slug        VARCHAR(100) UNIQUE NOT NULL,
    config      JSONB DEFAULT '{}',
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Users
CREATE TABLE users (
    id              BIGSERIAL PRIMARY KEY,
    organization_id BIGINT NOT NULL REFERENCES organizations(id),
    email           VARCHAR(255) NOT NULL,
    password_hash   TEXT NOT NULL,
    name            VARCHAR(255) NOT NULL,
    avatar_url      TEXT,
    external_id     VARCHAR(255),          -- Canvas user ID (nullable, solo TiCh)
    salt            VARCHAR(255),          -- Para Canvas synthetic password (nullable)
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(email, organization_id)         -- Mismo email puede existir en orgs distintas
);

-- Roles (M2M, un usuario puede tener varios roles)
CREATE TABLE user_roles (
    id      BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role    member_role NOT NULL,
    UNIQUE(user_id, role)
);

-- Refresh tokens (rotación: cada uso invalida el anterior)
CREATE TABLE refresh_tokens (
    id         BIGSERIAL PRIMARY KEY,
    user_id    BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,       -- SHA256 del token (no guardamos el token plano)
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Rate limiting login
CREATE TABLE login_attempts (
    id         BIGSERIAL PRIMARY KEY,
    email      VARCHAR(255) NOT NULL,
    ip_address VARCHAR(45),
    success    BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Password reset
CREATE TABLE password_reset_tokens (
    id         BIGSERIAL PRIMARY KEY,
    user_id    BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash TEXT NOT NULL UNIQUE,       -- SHA256 del token
    expires_at TIMESTAMP NOT NULL,         -- 1 hora de vida
    used       BOOLEAN NOT NULL DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_org ON users(organization_id);
CREATE INDEX idx_users_external_id ON users(external_id) WHERE external_id IS NOT NULL;
CREATE INDEX idx_refresh_tokens_user ON refresh_tokens(user_id);
CREATE INDEX idx_refresh_tokens_expires ON refresh_tokens(expires_at);
CREATE INDEX idx_login_attempts_email ON login_attempts(email, created_at);
CREATE INDEX idx_password_reset_expires ON password_reset_tokens(expires_at) WHERE used = false;
```

### Roles unificados

Todos los roles de todos los productos viven en el mismo enum:

| Rol | Producto | Descripción |
|---|---|---|
| `student` | TiCh/Tuni | Estudiante |
| `supervisor` | TiCh/Tuni | Supervisor de cursos |
| `teacher` | Alizia | Docente |
| `coordinator` | Alizia | Coordinador de área |
| `admin` | Ambos | Administrador de la organización |

Un usuario puede tener varios roles. El JWT incluye todos los roles del usuario. Cada producto filtra los que le interesan con `tokens.RequireRole()` de team-ai-toolkit.

---

## JWT

### Firmado (auth service)

```go
claims := &jwt.MapClaims{
    "sub":    user.ID,
    "org_id": user.OrganizationID,
    "roles":  []string{"teacher", "coordinator"},
    "email":  user.Email,
    "name":   user.Name,
    "iat":    time.Now().Unix(),
    "exp":    time.Now().Add(1 * time.Hour).Unix(),
}

token := jwt.NewWithClaims(jwt.SigningMethodRS256, claims)
signed, _ := token.SignedString(privateKey)
```

- **Access token**: 1 hora de vida
- **Refresh token**: 30 días de vida, rotación en cada uso
- **Algoritmo**: RS256 (asymmetric — private key firma, public key valida)

### Validado (en los backends, via team-ai-toolkit)

```go
// Ya existe en team-ai-toolkit/tokens
claims, err := tokens.ValidateJWT(tokenStr, publicKey)
// claims.UserID, claims.OrgID, claims.Roles, claims.Email
```

Zero HTTP calls al auth service en runtime.

---

## Endpoints

### Autenticación pública

```
POST /auth/login
  Body: { "email": "carlos@school.edu", "password": "..." }
  Response: { "access_token": "eyJ...", "refresh_token": "...", "user": {...} }
  Errors: 401 invalid_credentials, 429 too_many_attempts

POST /auth/register
  Body: { "email": "...", "password": "...", "name": "...", "organization_slug": "siglo21" }
  Response: { "access_token": "eyJ...", "refresh_token": "...", "user": {...} }
  Errors: 400 validation_error, 409 email_already_exists

POST /auth/refresh
  Body: { "refresh_token": "..." }
  Response: { "access_token": "eyJ...", "refresh_token": "..." }  (token rotado)
  Errors: 401 invalid_refresh_token

POST /auth/password-reset
  Body: { "email": "...", "organization_slug": "..." }
  Response: 204 (siempre, no revela si el email existe)

POST /auth/password-reset/confirm
  Body: { "token": "...", "new_password": "..." }
  Response: 204
  Errors: 400 token_expired, 400 token_already_used
```

### Autenticado (requiere access token)

```
GET /auth/me
  Response: { "user": { "id", "email", "name", "org_id", "roles", "avatar_url" } }
```

### Canvas (solo si env vars de Canvas presentes)

```
POST /auth/canvas/login
  Body: form-data (iss, login_hint, target_link_uri, client_id, lti_message_hint)
  Response: redirect a Canvas SSO

GET  /auth/canvas/oauth/callback?code=...&popup=true|false
  Response: HTML con postMessage (popup) o redirect al frontend (no popup)

POST /auth/canvas/launch
  Body: form-data (state, id_token)
  Response: redirect al frontend con token
```

### Admin (requiere role admin)

```
POST /admin/organizations
  Body: { "name": "Siglo 21", "slug": "siglo21", "config": {...} }
  Response: { "id": 1 }

GET  /admin/organizations
  Response: [{ "id", "name", "slug" }]

POST /admin/users
  Body: { "email": "...", "name": "...", "password": "...", "organization_id": 1, "roles": ["teacher"] }
  Response: { "id": 1 }

PUT  /admin/users/:id/roles
  Body: { "roles": ["teacher", "coordinator"] }
  Response: 204
```

---

## Estructura del proyecto

```
auth-service/
├── cmd/
│   ├── main.go                          # config → NewApp() → Run()
│   ├── app.go                           # App struct, lifecycle
│   ├── repositories.go                  # Crea repos
│   ├── usecases.go                      # Crea usecases
│   └── handlers.go                      # Crea handlers + container
│
├── src/
│   ├── app/
│   │   ├── web/
│   │   │   └── mapping.go              # Rutas del web server
│   │   └── functions/
│   │       └── functions.go            # Cloud Function entry point
│   │
│   ├── core/
│   │   ├── entities/
│   │   │   ├── user.go                 # User, UserRole
│   │   │   ├── organization.go         # Organization
│   │   │   ├── token.go               # RefreshToken, PasswordResetToken
│   │   │   └── canvas.go              # CanvasUser (si Canvas habilitado)
│   │   │
│   │   ├── providers/
│   │   │   ├── users.go               # UserRepository interface
│   │   │   ├── organizations.go       # OrgRepository interface
│   │   │   ├── tokens.go             # TokenRepository interface (refresh + reset)
│   │   │   ├── email.go              # EmailSender interface
│   │   │   ├── canvas.go             # CanvasClient interface (opcional)
│   │   │   └── errors.go             # Errores específicos del auth service
│   │   │
│   │   └── usecases/
│   │       ├── login.go               # Email + password → JWT + refresh
│   │       ├── login_test.go
│   │       ├── register.go            # Crear usuario + JWT
│   │       ├── register_test.go
│   │       ├── refresh.go             # Rotar refresh token → nuevo JWT
│   │       ├── refresh_test.go
│   │       ├── password_reset.go      # Enviar email con token
│   │       ├── password_reset_confirm.go  # Validar token + cambiar password
│   │       ├── me.go                  # Info del usuario autenticado
│   │       ├── canvas_oauth.go        # Canvas OAuth callback (opcional)
│   │       ├── canvas_lti.go          # Canvas LTI launch (opcional)
│   │       ├── admin_create_org.go    # Crear organización
│   │       ├── admin_create_user.go   # Crear usuario (admin)
│   │       └── admin_set_roles.go     # Asignar roles
│   │
│   ├── entrypoints/
│   │   ├── containers.go              # AuthContainer, AdminContainer
│   │   └── rest/
│   │       ├── rest.go                # HandleError (extiende team-ai-toolkit)
│   │       ├── auth/
│   │       │   ├── login.go
│   │       │   ├── register.go
│   │       │   ├── refresh.go
│   │       │   ├── password_reset.go
│   │       │   ├── password_reset_confirm.go
│   │       │   └── me.go
│   │       ├── canvas/               # Solo si Canvas habilitado
│   │       │   ├── login.go
│   │       │   ├── oauth_callback.go
│   │       │   └── launch.go
│   │       └── admin/
│   │           ├── create_org.go
│   │           ├── create_user.go
│   │           └── set_roles.go
│   │
│   ├── repositories/
│   │   ├── users/
│   │   │   ├── repository.go
│   │   │   ├── get_by_email.go
│   │   │   ├── create.go
│   │   │   ├── update_password.go
│   │   │   └── queries/
│   │   │       ├── get_by_email.sql
│   │   │       ├── create.sql
│   │   │       └── update_password.sql
│   │   ├── organizations/
│   │   │   ├── repository.go
│   │   │   ├── get_by_slug.go
│   │   │   ├── create.go
│   │   │   └── queries/
│   │   ├── tokens/
│   │   │   ├── repository.go
│   │   │   ├── create_refresh.go
│   │   │   ├── validate_refresh.go
│   │   │   ├── revoke_refresh.go
│   │   │   ├── create_reset.go
│   │   │   ├── validate_reset.go
│   │   │   ├── cleanup_expired.go    # Cron: borra tokens expirados
│   │   │   └── queries/
│   │   ├── login_attempts/
│   │   │   ├── repository.go
│   │   │   ├── record.go
│   │   │   ├── check_rate_limit.go   # 5 intentos en 15 min
│   │   │   └── queries/
│   │   ├── email/
│   │   │   └── sendgrid.go           # Implementa providers.EmailSender
│   │   └── canvas/                    # Solo si Canvas habilitado
│   │       ├── client.go
│   │       ├── get_access_token.go
│   │       ├── get_user_profile.go
│   │       └── validate_lti_token.go
│   │
│   ├── jwt/                           # Signing (solo el auth service firma)
│   │   ├── issuer.go                  # SignAccessToken(), SignRefreshToken()
│   │   └── keys.go                    # LoadPrivateKey(), LoadPublicKey()
│   │
│   ├── mocks/
│   │   ├── providers/
│   │   └── usecases/
│   │
│   └── utils/
│       └── hash.go                    # HashPassword(), ComparePassword() (bcrypt)
│
├── config/
│   └── config.go                      # Embebe BaseConfig + JWT keys + SendGrid + Canvas (opcional)
│
├── db/
│   └── migrations/
│       ├── 000001_init.up.sql         # Enums + todas las tablas
│       └── 000001_init.down.sql
│
├── Dockerfile
├── docker-compose.yml                 # PostgreSQL auth_db
├── .golangci.yml
├── .air.toml
├── Makefile
├── go.mod                             # require team-ai-toolkit
└── go.sum
```

---

## Configuración

```go
// config/config.go
package config

import (
    bcfg "github.com/educabot/team-ai-toolkit/config"
)

type Config struct {
    bcfg.BaseConfig

    // JWT signing
    JWTPrivateKey       string  // RSA private key PEM (para firmar tokens)
    AccessTokenExpiry   string  // "1h" default
    RefreshTokenExpiry  string  // "720h" default (30 días)

    // Email (password reset)
    SendGridAPIKey      string
    SendGridFromEmail   string
    PasswordResetURL    string  // URL del frontend: "https://app.alizia.com/reset-password"

    // Canvas (opcional, solo para TiCh/Tuni)
    CanvasURL             string
    CanvasClientID        string
    CanvasClientSecret    string
    CanvasRedirectURI     string
    CanvasLTIPrivateKey   string
    CanvasLTILoginSecret  string

    // Rate limiting
    MaxLoginAttempts    int     // 5
    LoginWindowMinutes  int     // 15

    // Frontend URLs (para redirects)
    FrontendURL         string
}

func Load() *Config {
    base := bcfg.LoadBase()
    return &Config{
        BaseConfig:          base,
        JWTPrivateKey:       bcfg.MustEnv("JWT_PRIVATE_KEY"),
        AccessTokenExpiry:   bcfg.EnvOr("ACCESS_TOKEN_EXPIRY", "1h"),
        RefreshTokenExpiry:  bcfg.EnvOr("REFRESH_TOKEN_EXPIRY", "720h"),
        SendGridAPIKey:      bcfg.EnvOr("SENDGRID_API_KEY", ""),
        SendGridFromEmail:   bcfg.EnvOr("SENDGRID_FROM_EMAIL", "noreply@educabot.com"),
        PasswordResetURL:    bcfg.EnvOr("PASSWORD_RESET_URL", "http://localhost:3000/reset-password"),
        CanvasURL:           bcfg.EnvOr("CANVAS_URL", ""),
        CanvasClientID:      bcfg.EnvOr("CANVAS_CLIENT_ID", ""),
        CanvasClientSecret:  bcfg.EnvOr("CANVAS_CLIENT_SECRET", ""),
        CanvasRedirectURI:   bcfg.EnvOr("CANVAS_REDIRECT_URI", ""),
        CanvasLTIPrivateKey: bcfg.EnvOr("CANVAS_LTI_PRIVATE_KEY", ""),
        CanvasLTILoginSecret: bcfg.EnvOr("CANVAS_LTI_LOGIN_SECRET", ""),
        MaxLoginAttempts:    5,
        LoginWindowMinutes:  15,
        FrontendURL:         bcfg.EnvOr("FRONTEND_URL", "http://localhost:3000"),
    }
}

// CanvasEnabled returns true if Canvas integration is configured.
func (c *Config) CanvasEnabled() bool {
    return c.CanvasURL != "" && c.CanvasClientID != ""
}

// EmailEnabled returns true if email sending is configured.
func (c *Config) EmailEnabled() bool {
    return c.SendGridAPIKey != ""
}
```

---

## Flujos principales

### Login (email + password)

```
1. Frontend: POST /auth/login { email, password }
2. Handler: parsea request
3. Usecase:
   a. CheckRateLimit(email) → si > 5 intentos en 15min → 429
   b. GetUserByEmail(email) → si no existe → 401
   c. bcrypt.CompareHashAndPassword(user.PasswordHash, password)
      → si no matchea → RecordAttempt(email, false) → 401
   d. RecordAttempt(email, true)
   e. SignAccessToken(user) → JWT 1h
   f. CreateRefreshToken(user) → token 30d, guarda hash en DB
   g. Return { access_token, refresh_token, user }
```

### Register

```
1. Frontend: POST /auth/register { email, password, name, organization_slug }
2. Handler: parsea request
3. Usecase:
   a. GetOrgBySlug(slug) → si no existe → 400
   b. CheckEmailExists(email, org_id) → si existe → 409
   c. bcrypt.GenerateFromPassword(password, 12)
   d. CreateUser(email, hash, name, org_id) con role default
   e. SignAccessToken(user) → JWT
   f. CreateRefreshToken(user)
   g. Return { access_token, refresh_token, user }
```

### Refresh token

```
1. Frontend: POST /auth/refresh { refresh_token }
2. Usecase:
   a. Hash(refresh_token) → busca en DB
   b. Si no existe o expirado → 401
   c. Revoca el token usado (delete)
   d. Crea nuevo refresh token (rotación)
   e. SignAccessToken(user)
   f. Return { access_token, refresh_token }
```

### Password reset

```
1. Frontend: POST /auth/password-reset { email, organization_slug }
2. Usecase:
   a. GetUserByEmail(email) → si no existe → 204 (no revela)
   b. Genera token random (32 bytes hex)
   c. Guarda hash del token en DB (expira en 1h)
   d. Envía email con link: {PASSWORD_RESET_URL}?token={token}
   e. Return 204 (siempre)

3. Frontend: POST /auth/password-reset/confirm { token, new_password }
4. Usecase:
   a. Hash(token) → busca en DB
   b. Si no existe, expirado, o usado → 400
   c. bcrypt.GenerateFromPassword(new_password, 12)
   d. UpdatePassword(user_id, new_hash)
   e. Marca token como usado
   f. Revoca todos los refresh tokens del usuario
   g. Return 204
```

### Canvas OAuth (solo TiCh/Tuni)

```
1. Widget: abre popup Canvas OAuth
2. Canvas: redirect a GET /auth/canvas/oauth/callback?code=XXX
3. Usecase:
   a. Exchange code → Canvas access token
   b. Fetch Canvas user profile (name, email, avatar)
   c. GetUserByExternalID(canvas_user_id)
   d. Si no existe:
      - Genera salt
      - Crea usuario con password sintético: bcrypt(base64(email + salt))
      - Asigna role "student" por default
   e. SignAccessToken(user)
   f. CreateRefreshToken(user)
4. Handler:
   - Si popup=true → HTML con postMessage({ token })
   - Si popup=false → redirect a {FRONTEND_URL}/login?token={token}
```

---

## Rate limiting

```sql
-- Verificar rate limit antes de cada login
SELECT COUNT(*) as attempts
FROM login_attempts
WHERE email = $1
  AND success = false
  AND created_at > NOW() - INTERVAL '15 minutes';

-- Si attempts >= 5 → retornar 429 Too Many Requests
-- Response: { "error": { "code": "too_many_attempts", "message": "Try again in X minutes" } }
```

Limpieza automática: cron job o query condicional que borra intentos de más de 24h.

---

## Seguridad

| Aspecto | Implementación |
|---|---|
| **Passwords** | bcrypt cost 12 (nunca se guardan en texto plano) |
| **Refresh tokens** | Solo el hash (SHA256) se guarda en DB |
| **Reset tokens** | Solo el hash se guarda, expiran en 1h, single-use |
| **Rate limiting** | 5 intentos fallidos en 15 min por email |
| **JWT** | RS256 asymmetric (private key solo en auth service) |
| **Token rotation** | Refresh token se invalida al usarse, se emite uno nuevo |
| **Password reset** | Siempre retorna 204 (no revela si el email existe) |
| **Password strength** | Mínimo 8 caracteres (validación en usecase) |
| **Logout** | Revocar refresh tokens del usuario. Access token expira solo (stateless) |

---

## Dependencias (go.mod)

```
require (
    github.com/educabot/team-ai-toolkit   v1.x.x   // Infra compartida
    github.com/jmoiron/sqlx               v1.4.x   // SQL
    github.com/golang-jwt/jwt/v5          v5.x.x   // JWT signing (team-ai-toolkit lo usa para validar, acá para firmar)
    golang.org/x/crypto                            // bcrypt
    github.com/sendgrid/sendgrid-go       v3.x.x   // Email (password reset)
    github.com/stretchr/testify           v1.9.x   // Testing
    github.com/golang-migrate/migrate     v4.x.x   // Migraciones
)
```

7 dependencias directas.

---

## Migración al auth-service (PLAN FUTURO)

> Esta migración se realizará después del lanzamiento de Alizia. Alizia arranca con JWT authentication via team-ai-toolkit/tokens.

### Fase 0: Alizia lanza con JWT auth (ACTUAL)
- Alizia usa JWT authentication via team-ai-toolkit/tokens
- team-ai-toolkit/tokens valida JWT via JWKS
- No se necesita RSA key pair propia ni auth-service

### Fase 1: Build auth service (FUTURO)
- Implementar login, register, refresh, password reset
- Migrar datos: exportar usuarios del sistema actual → importar en auth_db
- Los passwords del sistema actual no se pueden exportar → forzar password reset para todos

### Fase 2: Migrar Alizia (FUTURO)
- Cambiar Alizia del sistema actual a auth-service
- team-ai-toolkit/tokens pasa de validar via JWKS a validar via RSA public key

### Fase 3: Migrar TiCh/Tuni (FUTURO)
- Canvas OAuth callback apunta al auth-service en vez de cronos
- cronos valida JWT del auth-service
- Mantener Canvas LTI launch

### Fase 4: Deprecar sistema de auth actual (FUTURO)
- Verificar que todos los proyectos usen auth-service
- Desactivar sistema de autenticación anterior

---

## Diferencias con la arquitectura de Alizia

| Aspecto | Alizia | Auth Service |
|---|---|---|
| **Tamaño** | Grande (26+ tablas, 5 módulos) | Chico (6 tablas, 1 módulo con sub-features) |
| **Deploy** | Cloud Functions agrupadas (5) | Cloud Function individual (1) |
| **DB** | alizia_db | auth_db (separada) |
| **Usa team-ai-toolkit** | Si (web, boot, tokens, errors, etc.) | Si (web, boot, dbconn, errors, applog, config). NO usa tokens/ (él firma, no valida) |
| **JWT** | Solo valida (public key) | Firma (private key) + valida (para /auth/me) |
| **Arquitectura** | Clean Architecture completa | Clean Architecture (misma estructura, menos capas) |
| **Canvas** | No | Si (opcional, habilitado por config) |

---

## Resumen

El auth service es un microservicio Go planificado para el futuro que:
1. **Centralizará** login, register, y gestión de tokens
2. **Firma JWT RS256** con private key propia
3. **Agrega lo que hoy no existe**: refresh tokens, password reset, rate limiting
4. **Mantiene Canvas** OAuth y LTI para TiCh/Tuni (deshabilitado por config si no se necesita)
5. **Centraliza usuarios y roles** de todos los productos
6. **Usa team-ai-toolkit** para la infra compartida
7. **Es simple**: 6 tablas, 1 Cloud Function, ~15 endpoints

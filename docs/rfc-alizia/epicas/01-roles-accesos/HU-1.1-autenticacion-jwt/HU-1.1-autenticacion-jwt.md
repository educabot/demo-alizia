# HU-1.1: Autenticación JWT

> Como usuario, necesito autenticarme con email y contraseña para acceder a la plataforma con mis permisos correspondientes.

**Fase:** 1 — Setup
**Prioridad:** Alta (bloqueante para rutas protegidas)
**Estimación:** —

---

## Criterios de aceptación

- [ ] JWT auth configurado con JWKS domain + audience para staging
- [ ] JWT middleware valida tokens via JWKS (team-ai-toolkit/tokens)
- [ ] Claims extraídos del JWT: user_id, org_id, roles, email, name
- [ ] Tenant middleware inyecta org_id en el contexto
- [ ] Request sin token → 401 `missing_token`
- [ ] Request con token inválido → 401 `invalid_token`
- [ ] Request con token de otra org → datos filtrados por org_id
- [ ] Refresh token rotation configurada (30 días abs, 7 días inactividad)
- [ ] Endpoint POST /auth/logout invalida sesión
- [ ] CORS configurado para orígenes permitidos via env var
- [ ] Rate limiting en endpoints de IA (generate, chat)

## Tareas

| # | Tarea | Archivo | Estado |
|---|-------|---------|--------|
| 1.1.1 | [Configurar JWT auth](./tareas/T-1.1.1-configurar-jwt.md) | — | ⬜ |
| 1.1.2 | [Integrar JWT middleware (JWKS)](./tareas/T-1.1.2-jwt-middleware.md) | cmd/main.go | ⬜ |
| 1.1.3 | [Integrar tenant middleware](./tareas/T-1.1.3-tenant-middleware.md) | cmd/main.go | ⬜ |
| 1.1.4 | [Config: JWT auth env vars](./tareas/T-1.1.4-config-jwt.md) | config/config.go | ⬜ |
| 1.1.5 | [Tests de autenticación](./tareas/T-1.1.5-tests-auth.md) | — | ⬜ |
| 1.1.6 | [Refresh, logout y CORS](./tareas/T-1.1.6-refresh-logout-cors.md) | cmd/main.go | ⬜ |

## Dependencias

- Épica 0 completada (/health respondiendo)
- JWT auth configurado (JWKS domain + audience)
- team-ai-toolkit/tokens funcional

## Test cases

- 1.1: Request sin Authorization header → 401 `missing_token`
- 1.3: Request con JWT inválido → 401 `invalid_token`
- 1.4: Request con JWT válido → 200 + claims en context
- 1.5: Request con JWT de otra org → datos filtrados por org_id
- 1.6: POST /auth/logout → 200 con logout_url válida
- 1.7: Request desde origen no permitido → CORS bloqueado
- 1.8: Exceder rate limit → 429 rate_limit_exceeded

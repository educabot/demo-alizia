# HU-2.1: Detección de primer ingreso

> Como usuario que ingresa por primera vez, necesito ser redirigido automáticamente al flujo de onboarding para completar mi perfil y conocer la plataforma.

**Prioridad:** Alta
**Estimación:** —

---

## Contexto

Cuando un admin crea un usuario en el sistema (Épica 1), el usuario queda registrado con sus roles pero sin datos de perfil adicionales y sin haber interactuado con la plataforma. La primera vez que ese usuario se autentica, el sistema debe detectar que no completó el onboarding y redirigirlo al flujo correspondiente.

El mecanismo debe ser simple: un flag que indica si el onboarding fue completado. Si no lo completó, el frontend lo redirige.

## Criterios de aceptación

- [ ] Existe un mecanismo para saber si el usuario completó el onboarding (flag o timestamp en el modelo de usuario)
- [ ] Si no completó onboarding, se lo redirige al flujo
- [ ] Si ya lo completó, accede normalmente al home
- [ ] El onboarding se puede marcar como completado
- [ ] Marcar como completado es idempotente (llamar dos veces no genera error)
- [ ] El redirect es responsabilidad del frontend — el backend solo provee el estado

## Flujo esperado

```
Login exitoso → ¿Completó onboarding?
                    │
          ┌─────────┴─────────┐
          │                   │
         No                  Sí
          │                   │
    Ir a onboarding      Ir a home
          │
    (formulario + tour)
          │
    Marcar como completado
          │
    Ir a home
```

## Tareas

| # | Tarea | Archivo principal | Estado |
|---|-------|-------------------|--------|
| T-2.1.1 | [Migración — columna onboarding](./tareas/T-2.1.1-migracion.md) | `migrations/XXX_add_onboarding_to_users.sql` | ⬜ |
| T-2.1.2 | [Entity y endpoint de onboarding](./tareas/T-2.1.2-entity-endpoint.md) | `src/core/usecases/onboarding/complete.go` | ⬜ |

## Dependencias

- [HU-1.1: Autenticación JWT](../../01-roles-accesos/HU-1.1-autenticacion-jwt/HU-1.1-autenticacion-jwt.md) — JWT y middleware de auth deben estar funcionando
- [HU-1.2: Modelo de usuarios y roles](../../01-roles-accesos/HU-1.2-modelo-usuarios-roles/HU-1.2-modelo-usuarios-roles.md) — Tabla `users` debe existir

## Notas

- No se guarda "en qué paso" del onboarding está el usuario — si abandona a mitad, la próxima vez arranca de cero. Esto simplifica el modelo y es aceptable para un flujo corto.
- Para usuarios existentes al momento del deploy, se puede correr un script que los marque como "onboarding completado" para que no pasen por el flujo.

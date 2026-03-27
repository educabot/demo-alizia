# HU-2.4: Configuración de onboarding por organización

> Como admin de una organización, necesito definir qué datos pedir y qué pasos mostrar en el onboarding para que se adapte a las necesidades de mi provincia.

**Prioridad:** Alta
**Estimación:** —

---

## Contexto

El onboarding no es igual para todas las organizaciones. Una provincia puede necesitar saber las disciplinas del docente y su experiencia; otra puede no necesitar nada extra. Lo mismo con el product tour: si una org no tiene habilitadas las clases compartidas, no tiene sentido mostrar ese paso.

La configuración del onboarding sigue el mismo patrón que el resto de la configuración por org (`organizations.config` JSONB) — un JSON centralizado que define el comportamiento por tenant.

## Criterios de aceptación

- [ ] La config de onboarding vive dentro de la configuración general de la organización
- [ ] Se pueden definir los campos del formulario de perfil (key, label, tipo, opciones, obligatorio)
- [ ] Se pueden definir los pasos del product tour (key, título, descripción, orden, roles, feature flag requerido)
- [ ] Se puede definir si el usuario puede saltear el onboarding
- [ ] Si no hay config de onboarding, los defaults son: sin formulario de perfil + tour mínimo
- [ ] Los cambios en la config solo afectan a usuarios que aún no completaron el onboarding

## Qué se configura

### Campos del formulario de perfil

Cada campo tiene:

| Propiedad | Descripción |
|-----------|-------------|
| `key` | Identificador único del campo |
| `label` | Texto visible al usuario |
| `type` | Tipo de input: `text`, `number`, `select`, `multiselect` |
| `options` | Lista de opciones (solo para select/multiselect) |
| `required` | Si el campo es obligatorio |

### Pasos del product tour

Cada paso tiene:

| Propiedad | Descripción |
|-----------|-------------|
| `key` | Identificador único del paso |
| `title` | Título visible al usuario |
| `description` | Texto explicativo del paso |
| `order` | Orden de aparición |
| `roles` | Roles a los que aplica (coordinator, teacher) |
| `requires_feature` | Feature flag que debe estar activo para mostrar el paso (opcional) |

### Opciones generales

| Propiedad | Default | Descripción |
|-----------|---------|-------------|
| Permitir saltear onboarding | Sí | Si el usuario puede omitir el flujo completo |

## Ejemplo de configuración

**Provincia que pide datos y tiene tour personalizado:**
- Campos: disciplinas (multiselect, obligatorio), años de experiencia (number, opcional), niveles (multiselect, obligatorio)
- Tour: 8 pasos diferenciados por rol, paso de clases compartidas condicionado a feature flag
- Saltear: no permitido

**Provincia minimalista:**
- Campos: ninguno (se salta directo al tour)
- Tour: usa el default
- Saltear: permitido

## Tareas

| # | Tarea | Archivo principal | Estado |
|---|-------|-------------------|--------|
| T-2.4.1 | [Schema config onboarding](./tareas/T-2.4.1-schema-config-onboarding.md) | `src/core/entities/onboarding_config.go` | ⬜ |

## Dependencias

- [HU-1.2: Modelo de usuarios y roles](../../01-roles-accesos/HU-1.2-modelo-usuarios-roles/HU-1.2-modelo-usuarios-roles.md) — La config vive en la tabla de organizaciones
- [HU-1.3: Middleware de autorización](../../01-roles-accesos/HU-1.3-middleware-autorizacion/HU-1.3-middleware-autorizacion.md) — Solo admins pueden modificar la config

## Notas

- En la práctica, la config inicial la arma el equipo de implementación al hacer el setup de la org. El admin de la org rara vez la modifica directamente.
- No se necesita versionado ni historial de cambios — si cambian algo, afecta a los próximos usuarios que hagan onboarding.
- Los usuarios que ya completaron el onboarding no se ven afectados por cambios en la config.

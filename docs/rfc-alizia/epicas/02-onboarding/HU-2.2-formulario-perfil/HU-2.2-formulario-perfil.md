# HU-2.2: Formulario de perfil

> Como usuario nuevo, necesito completar mis datos de perfil (disciplinas, experiencia, etc.) para que la plataforma personalice mi experiencia.

**Prioridad:** Alta
**Estimación:** —

---

## Contexto

Cada organización puede necesitar datos distintos de sus usuarios. Una provincia puede pedir disciplinas y años de experiencia docente; otra puede no pedir nada adicional al nombre y email que ya vienen del JWT.

Los campos del formulario se definen en la configuración de la organización. Si la org no tiene campos configurados, este paso se salta y se va directo al product tour.

## Criterios de aceptación

- [ ] El usuario ve un formulario con los campos configurados para su organización
- [ ] Si la org no tiene campos configurados, se salta directo al tour
- [ ] Los campos soportan al menos estos tipos: texto libre, número, selección simple, selección múltiple
- [ ] Los campos marcados como obligatorios se validan antes de avanzar
- [ ] Para campos de selección, las opciones válidas se definen en la config
- [ ] Los datos se guardan asociados al usuario
- [ ] Si el usuario vuelve a este paso (por haber abandonado), puede ver y editar lo que ya cargó

## Ejemplo de campos por organización

Una provincia podría configurar:

| Campo | Tipo | Obligatorio | Opciones |
|-------|------|-------------|----------|
| Disciplinas que enseñás | Selección múltiple | Sí | Matemáticas, Física, Química, Biología, Historia, Geografía... |
| Años de experiencia docente | Número | No | — |
| Especialización o posgrado | Texto libre | No | — |
| Niveles en los que trabajás | Selección múltiple | Sí | Inicial, Primario, Secundario, Superior |

Otra provincia podría no configurar ningún campo → el paso se salta.

## Tareas

| # | Tarea | Archivo principal | Estado |
|---|-------|-------------------|--------|
| T-2.2.1 | [Migración — columna profile_data](./tareas/T-2.2.1-migracion.md) | `migrations/XXX_add_profile_data_to_users.sql` | ⬜ |
| T-2.2.2 | [Endpoint de perfil](./tareas/T-2.2.2-endpoint-perfil.md) | `src/core/usecases/onboarding/save_profile.go` | ⬜ |

## Dependencias

- [HU-2.1: Detección de primer ingreso](../HU-2.1-deteccion-primer-ingreso/HU-2.1-deteccion-primer-ingreso.md) — El flujo de onboarding debe estar activo
- [HU-2.4: Configuración de onboarding por org](../HU-2.4-configuracion-onboarding-por-org/HU-2.4-configuracion-onboarding-por-org.md) — Los campos vienen de la config de la org

## Notas

- Los datos del perfil son informativos y pueden ser consultados por cualquier feature futura. Por ejemplo, la IA podría tener en cuenta la experiencia del docente al generar contenido.
- El formulario también podría exponerse en un "settings" del usuario para editar después del onboarding.
- Las opciones de selección son strings estáticos en la config. En una evolución futura podrían venir de datos reales de la DB (ej: materias de la org en vez de strings sueltos).

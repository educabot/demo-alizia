# Épica 2: Onboarding

> Carga de datos iniciales y product tour para nuevos usuarios.

**Estado:** Post-MVP
**Fase de implementación:** Por definir

> **Nota MVP:** En el MVP no hay flujo de onboarding. Los usuarios y sus datos se cargan manualmente (seeds/scripts) para la demo. Esta épica define el flujo futuro para cuando la plataforma tenga usuarios reales registrándose.

---

## Problema

Un usuario nuevo (coordinador o docente) ingresa a la plataforma por primera vez después de autenticarse, pero no tiene su perfil completo ni sabe cómo usar el sistema. Sin un flujo guiado:

- El tiempo hasta el primer uso productivo es alto
- Faltan datos del usuario necesarios para personalizar la experiencia (disciplinas, experiencia, preferencias)
- El usuario no entiende qué puede hacer según su rol
- La tasa de abandono temprano es mayor

## Objetivos

- Capturar los datos necesarios del usuario al primer ingreso (perfil, disciplinas, experiencia)
- Guiar al usuario por las funcionalidades clave según su rol
- Reducir el tiempo entre el primer login y la primera acción productiva
- Que la experiencia de onboarding sea configurable por provincia/organización

## Alcance

**Incluye:**

- Detección de primer ingreso y redirección al flujo de onboarding
- Formulario de datos de perfil configurable por organización
- Product tour contextual adaptado al rol del usuario y feature flags activos
- Marcado de onboarding completado para no repetir el flujo

**No incluye:**

- Alta de usuarios → ver [Épica 1: Roles y accesos](../01-roles-accesos/01-roles-accesos.md)
- Carga de datos institucionales (áreas, materias, cursos) → ver [Épica 3: Integración](../03-integracion.md)
- Configuración de la organización → admin setup
- Tutorial interactivo avanzado (video, gamificación) → horizonte
- Onboarding de administradores → el admin no necesita tour, usa APIs/panel

## Principios de diseño

- **Mínima fricción:** El onboarding pide solo lo necesario — si la org no requiere datos extra, el usuario pasa directo al tour.
- **Rol define el recorrido:** Un coordinador ve pasos sobre documentos de coordinación; un docente ve pasos sobre planificación de clases.
- **Configurable, no hardcoded:** Los campos del formulario y los pasos del tour se definen en la config de la organización.
- **Una sola vez:** El onboarding se completa una vez y no se repite. El usuario puede acceder a ayuda contextual después, pero no al flujo completo.

---

## Historias de usuario

| # | Historia | Descripción | Prioridad | Tareas |
|---|---------|-------------|-----------|--------|
| HU-2.1 | [Detección de primer ingreso](./HU-2.1-deteccion-primer-ingreso/HU-2.1-deteccion-primer-ingreso.md) | Detectar si el usuario ya completó onboarding y redirigir si no | Alta | 2 |
| HU-2.2 | [Formulario de perfil](./HU-2.2-formulario-perfil/HU-2.2-formulario-perfil.md) | Captura de datos del usuario configurables por organización | Alta | 2 |
| HU-2.3 | [Product tour](./HU-2.3-product-tour/HU-2.3-product-tour.md) | Recorrido guiado por la plataforma adaptado al rol | Media | 1 |
| HU-2.4 | [Configuración de onboarding por org](./HU-2.4-configuracion-onboarding-por-org/HU-2.4-configuracion-onboarding-por-org.md) | Definición de campos y pasos del tour por organización | Alta | 1 |

---

## Decisiones técnicas

- El onboarding se dispara **post-autenticación al primer ingreso**. No al registrarse (el alta la hace un admin), sino la primera vez que el usuario loguea con éxito.
- Los datos de la institución y la estructura curricular **ya están cargados vía Integración** (Épica 3) — el onboarding solo captura datos del usuario, no de la organización.
- Los datos requeridos se definen como **configuración por organización** (mismo patrón JSON de config). Una provincia puede pedir disciplinas y experiencia docente; otra puede no pedir nada adicional al perfil básico.
- El product tour se adapta al **rol y a los feature flags activos** de la organización. Si una org no tiene habilitado contenido, el tour no muestra esa sección.

## Decisiones de cada cliente

- Qué datos pedir en el formulario de perfil (disciplinas, años de experiencia, especialización, etc.)
- Si el formulario de perfil es obligatorio o se puede saltar
- Qué pasos incluir en el product tour
- Si el tour es obligatorio o se puede saltar
- Contenido y orden de los pasos del tour

## Épicas relacionadas

- **[Épica 1: Roles y accesos](../01-roles-accesos/01-roles-accesos.md)** — Define el rol que determina el flujo de onboarding. El usuario ya está autenticado y con roles asignados cuando llega al onboarding.
- **[Épica 3: Integración](../03-integracion.md)** — Los datos institucionales (áreas, materias, cursos, topics) ya están cargados cuando el usuario hace onboarding. El formulario puede referenciar estos datos (ej: "seleccioná tus disciplinas").
- **[Épica 4: Documento de coordinación](../04-documento-coordinacion/04-documento-coordinacion.md)** — El tour del coordinador muestra cómo crear un documento.
- **[Épica 5: Planificación docente](../05-planificacion-docente/05-planificacion-docente.md)** — El tour del docente muestra cómo acceder a sus clases y planificar.

## Test cases asociados

- Primer ingreso: usuario sin onboarding → redirect al flujo
- Segundo ingreso: usuario con onboarding completado → acceso directo al home
- Formulario: campos requeridos no completados → error de validación
- Formulario: org sin campos configurados → se salta directo al tour
- Tour: coordinador ve pasos de coordinación, docente ve pasos de planificación
- Tour: feature flag desactivado → paso del tour se oculta
- Tour: usuario con múltiples roles → ve pasos de ambos roles

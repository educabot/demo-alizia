# HU-2.3: Product tour

> Como usuario nuevo, necesito un recorrido guiado por la plataforma adaptado a mi rol para entender qué puedo hacer y cómo hacerlo.

**Prioridad:** Media
**Estimación:** —

---

## Contexto

Después de completar el formulario de perfil (o directamente si no hay formulario), el usuario ve un product tour que le muestra las funcionalidades clave de la plataforma. El tour es diferente según el rol:

- **Coordinador:** Aprende a crear documentos de coordinación, asignar topics, generar contenido con IA
- **Docente:** Aprende a ver el plan de su materia, crear lesson plans, usar recursos
- **Usuario con múltiples roles:** Ve los pasos de ambos roles

## Criterios de aceptación

- [ ] El usuario ve un recorrido guiado con pasos secuenciales
- [ ] Los pasos se filtran según los roles del usuario (coordinador, docente, ambos)
- [ ] Los pasos se filtran según los feature flags activos de la organización (ej: si clases compartidas no está habilitado, no se muestra ese paso)
- [ ] Si la org tiene pasos configurados, se usan esos; si no, se usa un tour default mínimo
- [ ] El usuario puede saltear el tour si la org lo permite
- [ ] El tour se muestra después del formulario de perfil (o directamente si no hay formulario)
- [ ] Un usuario con múltiples roles ve la unión de los pasos de ambos roles, sin duplicados

## Ejemplo de pasos del tour

### Para coordinador

1. **Bienvenido a Alizia** — Alizia te ayuda a planificar el año escolar de manera colaborativa.
2. **Tus áreas** — Acá vas a ver las áreas que coordinás con sus materias.
3. **Crear documento de coordinación** — El wizard te guía en 3 pasos: elegir temas, definir período y asignar temas a cada materia.
4. **Generá con Alizia** — Una vez creado el documento, podés generar contenido automáticamente con IA.

### Para docente

1. **Bienvenido a Alizia** — Alizia te ayuda a planificar el año escolar de manera colaborativa.
2. **Tus cursos y materias** — Acá vas a ver los cursos donde enseñás.
3. **Planificá tus clases** — Para cada clase podés crear un plan con actividades. La IA te ayuda a generar contenido.
4. **Clases compartidas** — Algunas clases las compartís con otro docente. *(solo si `shared_classes_enabled`)*
5. **Recursos educativos** — Podés crear guías, fichas y otros recursos con ayuda de IA.

### Tour default (sin config)

1. **Bienvenido a Alizia** — Introducción general.
2. **Explorá la plataforma** — Invitación a navegar.

## Flujo completo de onboarding

```
¿Completó onboarding? → No
  │
  ├── ¿Hay campos de perfil configurados?
  │     │
  │     ├── Sí → Mostrar formulario → Guardar datos
  │     │
  │     └── No → Saltar
  │
  ├── Mostrar product tour (pasos filtrados por rol + features)
  │
  └── Marcar onboarding como completado → Ir a home
```

## Tareas

| # | Tarea | Archivo principal | Estado |
|---|-------|-------------------|--------|
| T-2.3.1 | [Endpoint tour steps](./tareas/T-2.3.1-endpoint-tour-steps.md) | `src/core/usecases/onboarding/get_tour_steps.go` | ⬜ |

## Dependencias

- [HU-2.1: Detección de primer ingreso](../HU-2.1-deteccion-primer-ingreso/HU-2.1-deteccion-primer-ingreso.md) — El flujo de onboarding debe estar activo
- [HU-2.2: Formulario de perfil](../HU-2.2-formulario-perfil/HU-2.2-formulario-perfil.md) — El tour se muestra después del formulario
- [HU-2.4: Configuración de onboarding por org](../HU-2.4-configuracion-onboarding-por-org/HU-2.4-configuracion-onboarding-por-org.md) — Los pasos del tour vienen de la config

## Notas

- El frontend puede implementar el tour con cualquier librería (Shepherd.js, React Joyride, custom). La definición de producto no prescribe la tecnología.
- No se trackea qué pasos vio el usuario ni dónde abandonó. Si quiere saltar, puede hacerlo. El onboarding se marca como completo al final del flujo.
- Un usuario con rol coordinador + docente ve la unión de los pasos de ambos roles, sin duplicados (dedup por key del paso).

# Riesgos, dependencias y preguntas abiertas

## Riesgos

| # | Riesgo | Probabilidad | Impacto | Mitigación |
|---|--------|-------------|---------|------------|
| 1 | GORM genera queries N+1 en documents con 8+ JOINs | Media | Medio | Preload explícito en GORM + `db.Raw()` para queries complejas. Documentado en arquitectura como patrón. Si >50% de repos usan Raw, evaluar migración a sqlx |
| 2 | Config JSONB por org se vuelve inmanejable con muchos campos | Baja | Alto | Validación estricta en backend, schema documentado, defaults sensatos. No permitir campos arbitrarios |
| 3 | IA genera contenido de baja calidad o desalineado | Media | Medio | Prompts iterativos (empezar simple, mejorar con uso real). Review humano obligatorio antes de publicar (status draft). Prompts configurables por provincia |
| 4 | Multi-tenancy data leak (org A ve datos de org B) | Baja | Crítico | Middleware de tenant en TODAS las rutas. Tests específicos de isolation (ver testing.md T1-T4). org_id viene del JWT, no del request |
| 5 | Railway downtime afecta servicio | Baja | Medio | Dockerfile portable. Si Railway cae, migrar a Render/Fly.io/VPS en horas. Zero vendor lock-in |
| 6 | CTE recursivo de topics lento con muchos niveles | Baja | Medio | Level precalculado en tabla. Solo recalcular rama afectada al mover topic. Max 5 niveles en la práctica |
| 7 | Equipo pedagógico no define tipos de recurso a tiempo | Media | Bajo | Arrancar con 2 tipos genéricos (lecture_guide, course_sheet). Agregar más post-MVP |
| 8 | Frontend y backend desalineados en formato de JSONB | Media | Medio | Swagger/OpenAPI como contrato. Validar schemas en CI |
| 9 | Clases compartidas generan edge cases no contemplados | Media | Medio | Feature flag deshabilitado por defecto. Activar solo en orgs que lo necesiten y testear exhaustivamente |

---

## Dependencias

### Internas

| Dependencia | Tipo | Bloqueante | Estado | Notas |
|-------------|------|------------|--------|-------|
| team-ai-toolkit | Librería Go | Sí (Fase 1) | Creado | Repo con tests, compila limpio |
| auth-service | Microservicio | No (futuro) | Futuro (no bloqueante) | Planificado para centralizar emisión de tokens. No bloqueante para Alizia |
| JWT auth config | Infra | Sí (Fase 1) | Configurar | JWT_SECRET (team-ai-toolkit/tokens) |
| Railway account | Infra | Sí (Fase 1) | Configurar | Cuenta + proyecto + PostgreSQL |
| PostgreSQL en Railway | Infra | Sí (Fase 1) | Provisionar | O DB externa |
| Azure OpenAI access | Servicio | Sí (Fase 4) | Ya disponible | Mismo acceso que el POC |
| Diseño UX/UI | Entregable | No (backend first) | En progreso | Frontend es RFC separado |

### Externas

| Dependencia | Tipo | Bloqueante | Contacto |
|-------------|------|------------|----------|
| Azure OpenAI | API LLM | Sí (Fase 4) | Ya configurado |
| SendGrid | Email (auth-service) | No (noop funciona) | Cuenta por configurar |
| Equipo pedagógico provincial | Contenido | No (usamos defaults) | Reuniones pendientes |

---

## Preguntas abiertas

| # | Pregunta | Área | Estado |
|---|----------|------|--------|
| 1 | ¿Cómo se cargan los datos iniciales de una provincia? (manual, CSV, API) | Producto/Ops | Pendiente |
| 2 | ¿Quién crea las organizaciones? (super admin de Educabot o self-service) | Producto | Pendiente |
| 3 | ¿Los docentes pueden ver docs de otras áreas? (permiso configurable por org) | Producto | Pendiente |
| 4 | ¿Se mantiene historial de versiones de coordination documents? | Producto | Pendiente |
| 5 | ¿Cuántos concurrent users se esperan por org? (para dimensionar Railway) | Infra | Pendiente |
| 6 | ¿Qué pasa si el docente no tiene internet al grabar bitácora? (escuelas rurales) | Producto | Pendiente |
| 7 | ¿Se permite subida de fuentes propias del docente? (decisión por provincia) | Producto | Pendiente |
| 8 | ¿Cómo se exporta el lesson plan a PDF? (template configurable, formato) | Producto/Front | Pendiente |
| 9 | ¿El dashboard necesita notificaciones push o solo polling? | Frontend | Pendiente |
| 10 | ¿Rate limiting en endpoints de generación IA? (costo por request) | Backend | Pendiente |

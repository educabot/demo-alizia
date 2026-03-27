# Rollout

## Plan de rollout

| Fase | Alcance | Criterio para avanzar | Duración estimada |
|------|---------|----------------------|-------------------|
| 1 | Staging — equipo interno | CI verde, /health responde, auth funciona, CRUD básico | 1 semana |
| 2 | Org piloto (1 provincia) | Coordinador crea doc + genera con IA + publica. Docente planifica 1 clase | 2 semanas |
| 3 | 2-3 orgs adicionales | Feedback positivo, sin bugs bloqueantes, config por org funciona | 2 semanas |
| 4 | Todas las orgs | Métricas de éxito alcanzadas, 80% coverage, docs API actualizados | Continuo |

---

## Plan de rollback

1. **Railway**: revertir al deploy anterior (1 click en dashboard)
2. **Migraciones**: ejecutar `.down.sql` correspondiente
3. **Config**: revertir JSON de organización a versión anterior
4. **Comunicar** al equipo y documentar causa del rollback

---

## Monitoreo post-deploy

| Qué monitorear | Herramienta | Umbral de alerta |
|---|---|---|
| Errores 5xx | Bugsnag | > 5 en 5 minutos |
| Latencia de endpoints | Railway logs (applog) | p95 > 2 segundos |
| Healthcheck | Railway built-in | /health no responde en 30s |
| Errores de IA | Bugsnag + applog | Azure OpenAI timeout > 30s |
| Login failures | applog (login_failed events) | > 20 en 5 minutos desde misma IP |

# Comparativa de deploy — Cloud Functions vs Cloud Run vs Railway

## ¿Qué es cada uno?

| | Cloud Functions | Cloud Functions agrupadas | Cloud Run | Railway |
|---|---|---|---|---|
| **Qué subís** | 1 función Go | 1 función por módulo | 1 container Docker | Código o Dockerfile |
| **Qué corre** | 1 endpoint por función | Varios endpoints por función | Todos los endpoints en 1 proceso | Todos los endpoints en 1 proceso |
| **Ejemplo** | 55+ funciones (como tich-cronos hoy) | 5 funciones (1 por módulo) | 1 container | 1 servicio |
| **Analogía** | 55 microaplicaciones | 5 miniservices | 1 servidor normal en la nube | 1 servidor con deploy automático |

---

## Comparativa detallada

| Aspecto | Cloud Functions (1:1) | Cloud Functions agrupadas | Cloud Run | Railway |
|---|---|---|---|---|
| **Unidad de deploy** | 1 función = 1 endpoint | 1 función = 1 módulo (N endpoints) | 1 container = todos los endpoints | 1 servicio = todos los endpoints |
| **Cantidad de deploys** | 55+ (como tich-cronos) | 5 (admin, coordination, teaching, resources, ai) | 1 solo | 1 solo |
| **Cold start** | Si, en cada función | Si, pero solo 5 funciones | Configurable (min instances = 1) | No (siempre corriendo) |
| **Latencia cold start** | ~500ms - 2s (Go) | ~500ms - 2s (Go) | ~200ms - 500ms (container buildeado) | 0ms (no hay cold start) |
| **Escalado** | Por endpoint individual | Por módulo | Por container (réplicas) | Por réplicas (manual o auto) |
| **Dockerfile** | No | No | Sí (container estándar) | Opcional (Nixpacks auto-detect o Dockerfile) |
| **Portabilidad** | Solo GCP | Solo GCP | Cualquier cloud, VPS, Docker | Cualquier cloud, VPS, Docker |
| **Complejidad operativa** | Alta (55+ registros) | Media (5 registros) | Baja (1 deploy, 1 config) | Muy baja (git push = deploy) |
| **Debugging local** | Emulador o Go local | Emulador o Go local | `docker run` o `go run` | `go run` o `docker run` |
| **Logs** | 55+ streams | 5 streams (1 por módulo) | 1 stream unificado | 1 stream unificado |
| **CI/CD** | Deploy selectivo o todo | Deploy por módulo | 1 pipeline, 1 build, 1 deploy | Auto-deploy desde branch (zero config) |
| **Rollback** | Por función individual | Por módulo | Todo junto | Todo junto (redeploy commit anterior) |
| **Max request timeout** | 9 min (Gen2) | 9 min (Gen2) | 60 min | Sin límite práctico |
| **Max instances** | 1000 por función | 1000 por función | 1000 containers | Configurable por plan |
| **Min instances** | 0 o 1+ por función | 0 o 1+ por función | 0 o 1+ por container | 1 (siempre corriendo) |
| **Conexiones DB** | 55+ pools (saturan PostgreSQL) | 5 pools (manejable) | 1 pool compartido | 1 pool compartido |
| **Estado en memoria** | No (stateless) | Limitado (dentro del módulo) | Sí (cache, connection pool) | Sí (cache, connection pool) |
| **Vendor lock-in** | Alto (GCP) | Alto (GCP) | Bajo (container estándar) | Bajo (Dockerfile estándar) |

---

## Costos

| Escenario | Cloud Functions (1:1) | Cloud Functions agrupadas | Cloud Run | Railway |
|---|---|---|---|---|
| **Tráfico bajo** (< 2M req/mes) | Más barato. Free tier generoso | Más barato. Free tier generoso | Más caro si min instances = 1 | ~$5/mes (Hobby plan) |
| **Tráfico medio** (2M - 10M req/mes) | Similar | Similar | Similar | ~$20/mes (Pro plan) |
| **Tráfico alto** (> 10M req/mes) | Más caro (overhead por invocación) | Más caro (overhead por invocación) | Más barato (container absorbe) | Más barato (uso de recursos) |
| **Idle** (sin tráfico) | $0 | $0 | $0 o ~$5-15/mes (min instances) | ~$5/mes (servicio siempre corriendo) |
| **Free tier** | 2M invocaciones, 400K GB-sec | 2M invocaciones, 400K GB-sec | 2M requests, 360K vCPU-sec | Trial: $5 crédito, luego Hobby $5/mes |
| **PostgreSQL incluido** | No (Cloud SQL aparte) | No (Cloud SQL aparte) | No (Cloud SQL aparte) | Sí (plugin, mismo proyecto) |

---

## Pros y Contras

### Cloud Functions

**Pros:**
1. Free tier generoso para bajo tráfico
2. Escalado granular por endpoint (si /generate necesita más, solo esa escala)
3. No necesitás Dockerfile
4. Aislamiento: si un endpoint crashea, los otros siguen
5. Ya lo usa tich-cronos (experiencia del equipo)
6. Pay-per-use real (0 tráfico = $0)

**Contras:**
1. Cold starts en cada función (mala UX en primera request)
2. 55+ funciones = 55+ deploys = 55+ configs = mantenimiento tedioso
3. Cada función abre su propio pool de DB (puede saturar PostgreSQL)
4. No portable (solo GCP)
5. Logs fragmentados (1 stream por función)
6. CI/CD más complejo (deploy selectivo o deploy de todo)
7. Debugging local requiere emulador
8. Registrar cada función nueva es manual y propenso a errores

### Cloud Functions agrupadas por módulo (opción intermedia)

**Pros:**
1. Solo 5 funciones en vez de 55+ (admin, coordination, teaching, resources, ai)
2. Free tier de Cloud Functions (bajo costo)
3. Escalado por módulo (si AI necesita más, solo esa función escala)
4. Misma experiencia del equipo (ya conocen Cloud Functions)
5. 5 pools de DB en vez de 55+ (no satura PostgreSQL)
6. Si un módulo crashea, los otros siguen
7. Deploy por módulo (cambio en teaching no redeploya admin)
8. Mejora incremental sobre lo que ya tienen

**Contras:**
1. Cold starts siguen existiendo (5 funciones que arrancan)
2. Solo GCP (no portable)
3. 5 registros de funciones para mantener (poco pero no cero)
4. Cada función sigue teniendo su propio pool de DB
5. Timeout máximo 9 min (AI generation larga puede ser problema)

### Cloud Run

**Pros:**
1. 1 deploy = todos los endpoints
2. Cold start mínimo con min instances = 1
3. Container estándar → portable a AWS, Azure, o VPS si algún día migran
4. 1 pool de conexiones DB compartido (eficiente)
5. Cache in-memory posible (entre requests)
6. Logs unificados (1 stream)
7. CI/CD simple: build, push, deploy
8. Debugging local: `docker run` y listo
9. Misma experiencia dev y prod

**Contras:**
1. Con min instances = 1 pagás idle (~$5-15/mes por servicio)
2. Escalado es todo-o-nada (no por endpoint individual)
3. Necesitás Dockerfile (aunque es simple)
4. Si el container crashea, caen TODOS los endpoints
5. Rollback es todo junto (no por endpoint)

### Railway

**Pros:**
1. Deploy más simple posible: `git push` = deploy automático
2. Zero cold start (servicio siempre corriendo)
3. PostgreSQL como plugin en el mismo proyecto (sin configurar Cloud SQL)
4. Dashboard intuitivo con logs, métricas y env vars en un solo lugar
5. Dockerfile opcional (Nixpacks detecta Go automáticamente)
6. Container estándar → portable, zero vendor lock-in
7. 1 pool de conexiones DB compartido
8. CI/CD zero config (auto-deploy desde branch)
9. Preview environments por PR (Pro plan)
10. Rollback con un click (redeploy de commit anterior)

**Contras:**
1. Sin free tier real (~$5/mes mínimo, servicio siempre corriendo)
2. Escalado menos granular que Cloud Functions
3. Plataforma más nueva/pequeña que GCP
4. Si el servicio crashea, caen todos los endpoints
5. Rollback es todo junto (no por endpoint)
6. Menos integración con ecosistema GCP (Pub/Sub, Cloud Storage, etc.)

---

## Para nuestro caso específico (Alizia)

| Factor | Cloud Functions (1:1) | Cloud Functions agrupadas | Cloud Run | Railway | Observación |
|---|---|---|---|---|---|
| **26+ tablas, JOINs complejos** | 55+ pools saturan DB | 5 pools manejable | 1 pool compartido | 1 pool compartido | Cloud Run o Railway mejor para DB-heavy |
| **AI generation (10-30s)** | Función ocupada esperando | Función ocupada esperando | Container maneja concurrencia | Servicio maneja concurrencia | Cloud Run o Railway mejor para long-running |
| **4+ devs** | 55+ funciones para coordinar | 5 funciones claras | 1 deploy coordinado | 1 deploy coordinado | Agrupadas, Cloud Run o Railway buen balance |
| **Experiencia del equipo** | Ya lo conocen (tich-cronos) | Mismo approach mejorado | Curva mínima (Docker) | Curva mínima (git push) | Railway más simple de adoptar |
| **Presupuesto limitado** | Free tier generoso | Free tier generoso | Min instances tiene costo | ~$5/mes fijo | Cloud Functions si ajusta el presupuesto |
| **Portabilidad futura** | Solo GCP | Solo GCP | Cualquier cloud/VPS | Cualquier cloud/VPS | Cloud Run o Railway si quieren flexibilidad |
| **Simplicidad operativa** | Baja (55+ configs) | Media (5 configs) | Alta (1 config) | Muy alta (zero config) | Railway la opción más simple |
| **PostgreSQL** | Cloud SQL ($7+/mes) | Cloud SQL ($7+/mes) | Cloud SQL ($7+/mes) | Plugin integrado ($5/mes) | Railway incluye DB en el mismo proyecto |
| **Speed to market (POC)** | Lento (setup 55+ funciones) | Medio (setup 5 funciones) | Rápido (1 Dockerfile) | Muy rápido (git push y listo) | Railway ideal para POC |

---

## Opción intermedia: Cloud Functions con pocas funciones

En vez de 55+ funciones (1 por endpoint), agrupar por módulo:

```
b2b-alizia-http-admin          → Todos los endpoints de /admin/*
b2b-alizia-http-coordination   → Todos los endpoints de /coordination-documents/*
b2b-alizia-http-teaching       → Todos los endpoints de /lesson-plans/*
b2b-alizia-http-resources      → Todos los endpoints de /resources/*
b2b-alizia-http-ai             → Todos los endpoints de /chat, /generate
```

5 funciones en vez de 55+. Reduce la complejidad operativa de Cloud Functions manteniendo el escalado granular.

---

## Resumen para la decisión

| Si el equipo prioriza... | Elegir |
|---|---|
| Experiencia existente + bajo costo + no cambiar nada | Cloud Functions (1:1) |
| Mejorar lo actual sin cambio radical + bajo costo | Cloud Functions agrupadas por módulo |
| Simplicidad operativa + portabilidad + long-running | Cloud Run |
| **Máxima velocidad de entrega + simplicidad + DB integrada** | **Railway** ✓ |

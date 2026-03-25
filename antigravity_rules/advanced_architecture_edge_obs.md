# Patrones Arquitectónicos: Telemetría Distribuida (OpenTelemetry) y Edge Computing

## Arquitecturas y Ecosistemas

### 1. Observabilidad y OpenTelemetry (OTel)
- **Trilogía de la Observabilidad:** Un sistema moderno no confía en hacer `console.log`. Se basa en **Métricas** (CPU, memoria, latencias), **Logs Estruturados** (JSON logs con IDs correlacionados) y **Traces Distribuidos** (peticiones viajando de microservicio a microservicio).
- **Vendor-Neutrality:** OpenTelemetry es el estándar de oro (CNCF). La aplicación no sabe a dónde van los datos. Ella se instrumenta con OTel, expulsa los datos a un **OTEL Collector**, y el colector decide si los manda a DataDog, Grafana Loki, Jaeger, etc.

### 2. Edge Computing y Serverless (Cloudflare Workers / Vercel Edge)
- **Ejecución V8 Isolate:** Las arquitecturas en el Edge no arrancan un contenedor Docker pesado que tarda 2 segundos. Usan V8 Isolates (como Chrome) para arrancar el código en milisegundos en el CDN más cercano al usuario.
- **Serverless Databases:** Correr computo en el Edge es inútil si la base de datos está en una sola región física. Herramientas como Neon (Postgres Serverless) o Turso (SQLite Edge) permiten a las funciones al borde de la red consultar datos sin cruzar el océano.

## 2. Anti-patrones de Integración

- **Silenciamiento de Trace Contexts:** Permitir que una petición HTTP entre a un servicio `Backend A`, el cual lanza un mensaje a RabbitMQ, lo tome `Backend B`, y no se pase el `trace-id` original en los headers HTTP/AMQP. Rompe la trazabilidad visual distribuida.
- **Logs No Estructurados ("Spaghetti Logs"):** Usar sentencias planas de log: `INFO: El usuario 123 ha fallado el login`. Deben escribirse en diccionarios JSON nativos: `{"level":"info","event":"login_failed","user_id":123,"ip":"8.8.8.8"}`.
- **Node.js APIs en el Edge:** Intentar ejecutar código fuertemente enlazado con la API de SO de Node.js (`fs`, `child_process`) dentro de Cloudflare Workers (que son V8 Isolates puros de API Web standard: `fetch()`, `Request`, `Response`). El despliegue fallará.

## 3. Heurísticas para GahenaxAI

- **[HEURISTICA-OBS-OTEL-01 "Distributed Context Propagation"]:** "Toda integración entre dos componentes distribuidos (sea vía REST, gRPC, o Mensajes Pub/Sub) DEBE inyectar el protocolo estandar de W3C Trace Context en sus headers (`traceparent`, `tracestate`). Nunca interrumpas la cadena de propagación."
- **[HEURISTICA-OBS-LOG-01 "Structured JSON Logging Only"]:** "Queda formalmente vetado emitir logs de texto plano en servidores de producción. Todos los logs se estructurarán como JSON para su correcta ingesta e indexación en sistemas como Loki o Elasticsearch."
- **[HEURISTICA-EDGE-COMPUTE-01 "Stateless Edge Functions"]:** "Al proponer funciones Edge (Cloudflare/Vercel), asume que son amnésicas e inestables (viven ms). Nunca declares variables globales esperando que se compartan entre peticiones diferentes. Todo estado persistente debe ir a bases de datos kv locales al edge (Workers KV) o remotas."

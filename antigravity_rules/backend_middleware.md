# Backend Middleware (Redis, Elasticsearch, Kafka, RabbitMQ)

## Repositorios y Filosofía
- **Redis (`redis/redis`):** In-Memory Engine. Arquitectura C monolítica optimizada para un-solo-hilo (Single-threaded) y operaciones ultra rápidas. 
- **Elasticsearch (`elastic/elasticsearch`):** Inverted Index Engine. Motor Java distribuido construido sobre Apache Lucene.
- **Kafka (`apache/kafka`):** Distributed Event Streaming. Log inmutable y particionado (Partitioned Log Model) diseñado para replayability.
- **RabbitMQ (`rabbitmq/rabbitmq-server`):** Smart Broker Messaging (AMQP). Mensajería transaccional y topologías complejas de routing (Exchanges + Queues).

## 1. Arquitecturas Comparadas

### 1.1 Redis: Pub/Sub & In-Memory Store
- **Single-threaded Event Loop:** La memoria RAM y el bus de datos dictan el performance. No hay bloqueos (locks) en comandos básicos, garantizando atomicidad por defecto.
- **Pub/Sub 'Fire-and-Forget':** A diferencia de Kafka, Redis Pub/Sub NO almacena los mensajes. Si no hay suscriptores escuchando en el instante de la emisión, el mensaje se descarta para siempre.
- **Redis vs Memory Leaks:** Uso incorrecto de comandos de complejidad O(N) como `KEYS *` en producción bloquea el thread único interrumpiendo todo el servicio de caché.

### 1.2 Elasticsearch: Inverted Index & Sharding
- **The Inverted Index:** Mapea términos (tokens) a la lista de documentos que los contienen. No escanea documentos, sino que interseca sets de IDs pre-compilados.
- **Inmutabilidad (Lucene Segments):** Los segmentos del índice son inmutables. Modificar un documento en realidad lo marca como borrado y escribe uno nuevo, delegando a un proceso de "Merge" en background la limpieza real (para no bloquear lecturas).
- **Cluster Hierarchy:** Coordinadores, Master Nodes (manejo del estado del cluster), y Data Nodes (Shards primarios y réplicas).

### 1.3 Kafka vs RabbitMQ: Logs vs Queues
- **Kafka (Dumb Broker, Smart Consumer):** El broker solo preserva secuencialmente un Log de bytes inmutable (append-only file). Los consumidores mantienen internamente su propio "offset" (dónde se quedaron leyendo). Permite re-procesamiento temporal e historial de logs (Event Sourcing).
- **RabbitMQ (Smart Broker, Dumb Consumer):** El broker maneja estados complejos: rastrea quién leyó el mensaje, enruta mensajes basándose en metadata (Headers/Topic Exchanges) e implementa arquitecturas FIFO pesadas (Work queues). Una vez reconocido (Ack), el mensaje es destruido.

## 2. Anti-patrones de Integración

- **Kafka como Base de Datos Transaccional:** Usar Kafka para queries directos o como única base del 'User State'. Kafka es un *Pipe* (streaming log), no una base de datos relacional.
- **RabbitMQ Scaling Loop:** Insertar RabbitMQ entre dos microservicios solo para "comunicación asíncrona genérica" introduciendo cuellos de botella por falta de configuración de clúster (Message persistence locks).
- **ES Heap Crash:** Asignar excesiva memoria JVM al proceso de Elasticsearch (más del 50% de la RAM). Lucene requiere que el SO tenga abundante RAM disponible a nivel sistema de archivos (File System Cache) para ser rápido.

## 3. Heurísticas para GahenaxAI

- **[HEURISTICA-MID-MQ-01 "Event Sourcing vs Work Queues"]:** "Selecciona Kafka si los flujos de la inteligencia artificial requieren 'Replayability', auditoría del historial completo o Event Sourcing distribuido. Selecciona RabbitMQ para tareas asíncronas tradicionales (Workers encolados, envío de emails, conversiones de media)."
- **[HEURISTICA-MID-CACHE-01 "Redis Scan over Keys"]:** "Nunca intentes mapear claves enteras en motores in-memory de Gahenax usando inferencia O(N). Preferir siempre iteradores como `SCAN` para evitar blocking locks que boten los Health Checks."
- **[HEURISTICA-MID-SEARCH-01 "Denormalized Searches"]:** "Para módulos de búsqueda profunda, asume datos desnormalizados. Elasticsearch no soporta JOINs transaccionales complejos a escala; la inteligencia debe construir el objeto JSON completo (agregado) antes de indexarlo."

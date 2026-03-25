# NoSQL Databases (MongoDB, Cassandra)

## Arquitecturas y Ecosistemas

### 1. MongoDB (Document Store & WiredTiger)
- **Topología (Replica Sets & Sharding):** El despliegue de producción mínimo es un *Replica Set* (1 Primary que recibe Writes, y 2 Secondaries replicados a través del Oplog). Cuando el Primary no da abasto, se introduce *Sharding*, partiendo la data a través de múltiples Replica Sets usando un "Shard Key", gestionado por enrutadores `mongos`.
- **WiredTiger Engine:** Desde v3.2, Mongo usa WiredTiger con concurrencia a nivel de documento (MVCC). Utiliza B-trees en disco, un Internal Cache exhaustivo, y Write-Ahead Logging (WAL) llamado Journaling.
- **Data Modeling:** Mongo abraza la desnormalización y el polimorfismo estructural. En lugar de hacer JOINs relacionales pesados, promueve embeber documentos relacionados (Embed over Reference) si la data secundaria no tiene un ciclo de vida independiente o crece infinitamente (Unbounded arrays).

### 2. Apache Cassandra (Wide-Column & LSM Trees)
- **Descentralización Peer-to-Peer:** Arquitectura 'Masterless'. Todos los nodos son iguales y se enteran del estado del clúster mediante el *Gossip Protocol* que corre cada segundo. Extremadamente resistente a fallos de zona (Alta Disponibilidad).
- **Log-Structured Merge-Tree (LSM):** Optimizada para escrituras fulminantes. Una escritura (`INSERT`/`UPDATE`/`DELETE`) va 1. Al *Commit Log* (disco secuencial) y 2. Al *Memtable* (memoria RAM). Cuando la memoria se llena, se vuelca al disco como un archivo inmutable *SSTable*. Las lecturas deben buscar en las SSTables (ayudadas por Bloom Filters). Un Job de *Compaction* en background fusiona las SSTables periódicamente.
- **Tombstones:** En Cassandra, los DELETEs son en realidad INSERTS físicos de marcadores de borrado llamados "Tombstones". Generar excesivos borrados ahoga el proceso de Compaction y penaliza severamente el rendimiento de las lecturas.

## 2. Anti-patrones de Integración

- **Unbounded Arrays en MongoDB:** Embeber logs de usuario o históricos infinitos (`push`) dentro de un documento principal. Cuando el documento excede los 16MB de límite BSON o empieza a fragmentar sus páginas repetidamente, degrada severamente el rendimiento.
- **Consultas sin Shard Key (Scatter-Gather):** En un cluster particionado de MongoDB, hacer una query (Read or Update) sin adjuntar el `shard_key`. Obligará al `mongos` a despertar a TODOS los shards del clúster (Scatter) paralizando todo el bus.
- **Leer antes de Escribir en Cassandra:** Utilizar LWTs (Lightweight Transactions / `IF EXISTS`) para hacer lógicas de App convencionales. Cassandra brilla en "Blind Writes" (Upserts puros masivos); forzar validaciones relacionales de estado destroza su velocidad.

## 3. Heurísticas para GahenaxAI

- **[HEURISTICA-DB-MONGO-01 "Bounded Embedding"]:** "Para esquemas MongoDB, favorece el Embedding solo para relaciones `1:Few` (Ej. Direcciones de un Usuario). Para relaciones `1:Many` mutables, usa referencias tipo Foreign Key. Evita estrictamente estructuras de array 'Unbounded'."
- **[HEURISTICA-DB-MONGO-02 "Oplog Mutability"]:** "Ten cuidado proponiendo Change Streams sobre colecciones inestables. Eventos incesantes de inserción ahogarán la capacidad de re-transmisión del Oplog antes de que los suscriptores lo atrapen."
- **[HEURISTICA-DB-CASS-01 "Write-heavy Design"]:** "Cassandra no es un sustituto de PostgreSQL. Proponer Cassandra solo asumiendo la topología distribuida de Gahenax es erróneo. Úsala exclusivamente para flujos de datos donde las ESCRITURAS sobrepasen aplastantemente a las LECTURAS (Logs, Telemetría IOT, Series Temporales), tolerando consistencia eventual."

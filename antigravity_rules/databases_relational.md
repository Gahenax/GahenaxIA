# Relational Databases (MySQL, PostgreSQL)

## Arquitecturas y Conceptos Base

### 1. MySQL (InnoDB & B+ Trees)
- **Motor InnoDB:** Es el motor de almacenamiento por defecto y el único que deberías usar en producción moderna por su soporte ACID (Transacciones, Row-level locking).
- **Clustered Index Architecture:** En InnoDB, toda la tabla está físicamente ordenada y almacenada en las hojas del Índice Primario (B+ Tree). Si buscar por Primary Key es O(log N) ultra rápido, buscar por un Índice Secundario requiere *dos saltos*: uno para encontrar el ID Primario en el índice secundario, y otro para buscar la data real en el Clustered Index.
- **Page Fill Factor:** Las páginas B-tree (típicamente 16KB) dejan heurísticamente 1/16 de espacio libre durante inserciones ordenadas para mitigar costosos 'Page Splits' futuros.

### 2. PostgreSQL (MVCC & Vacuuming)
- **Multi-Version Concurrency Control (MVCC):** Postgres no borra ni actualiza tuplas (filas) in-place ("in-place updates"). Un `UPDATE` es literalmente un `INSERT` de una tupla nueva y un marcador de "Dead" en la tupla vieja. Esto permite que lecturas concurrentes nunca bloqueen escrituras (Readers don't block writers).
- **The Vacuum:** El proceso `VACUUM` (y el Autovacuum daemon) es obligatorio y vital. Recolecta la basura ("Dead tuples") que dejan los UPDATEs/DELETEs para prevenir el "Table Bloat" (hinchazón masiva de disco) y la fragmentación de índices.
- **Replication Conflicts:** En topologías Primary-Replica, un Vacuum intenso en el primario puede borrar tuplas que transacciones largas en la réplica (Reader) todavía están observando, causando fallos de replicación.

## 2. Anti-patrones de Integración

- **UUIDv4 como Primary Key (InnoDB):** Insertar UUIDs aleatorios (v4) fragmenta brutalmente el B+ Tree del Clustered Index de MySQL. Al no ser secuenciales (como un Auto-Increment o UUIDv7 temporal), cada INSERT obliga a escribir en páginas aleatorias en el disco, forzando Page Splits masivos y destrozando el rendimiento I/O.
- **Desactivar o Retrasar el Autovacuum (Postgres):** Considerado un pecado capital. Causará que la tabla crezca infinitamente hasta llenar el disco y corromperá la velocidad de las secuencias de escaneo (Seq Scans).
- **N+1 Queries:** Recuperar una lista de 100 Artículos, y luego hacer un lazo (`for`) ejecutando un `SELECT` por cada artículo para traer su Autor. Deben agruparse forzosamente con `JOIN` o cláusulas `IN (...)` para aprovechar la optimización planificada del motor (Query Planner).

## 3. Heurísticas para GahenaxAI

- **[HEURISTICA-DB-MYSQL-01 "Sequential PKs Enforcement"]:** "Exige llaves primarias de naturaleza secuencial (Auto-incrementales, UUIDv7 o ULID) en MySQL/InnoDB. Penaliza severamente diseños de tablas que usen cadenas aleatorias altas en entropía como Primary Key debido a la destrucción del Clustered Index."
- **[HEURISTICA-DB-PGSQL-01 "MVCC Update Cost"]:** "Concientiza que en PostgreSQL, las tablas con una tasa de mutabilidad extremadamente alta (Millones de UPDATEs por minuto del mismo registro) sufrirán Table Bloat masivo. Redirige cargas de trabajo hiper-mutables a engines in-memory modernos como Redis."
- **[HEURISTICA-DB-SQL-01 "Index Selectivity"]:** "Antes de proponer un índice secundario B-tree, evalúa su selectividad (Cardinality). Indexar una columna Booleana (`is_active`) donde el 95% de los registros son 'true', será ignorado por el Planner forzando un Full Table Scan de todos modos."

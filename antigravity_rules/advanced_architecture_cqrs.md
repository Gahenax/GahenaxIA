# Patrones Arquitectónicos: Event-Driven, CQRS y Event Sourcing

## Arquitecturas y Ecosistemas

### 1. Event-Driven Architecture (EDA)
- **Desacoplamiento asíncrono:** Los microservicios no se llaman directamente (RPC/HTTP), sino que se comunican emitiendo y reaccionando a **Eventos de Dominio** (ej. `UserRegistered`, `OrderShipped`).
- **Resiliencia:** Si el servicio de facturación falla, el servicio de órdenes sigue aceptando peticiones. Cuando facturación vuelve a levantarse, procesa la cola de eventos acumulada (Eventual Consistency).

### 2. CQRS (Command Query Responsibility Segregation)
- **Separación de Responsabilidades:** Divide las rutas de la arquitectura en dos modelos aislados:
  - **Command Model (Writes):** Encargado de validar la lógica de negocio y alterar el estado (INSERT/UPDATE/DELETE). Alta consistencia.
  - **Query Model (Reads):** Creado exclusivamente para consultas de lectura en alta disponibilidad. Frecuentemente desnormalizado como *Materialized Views* para leer de forma instantánea sin JOINs complejos.

### 3. Event Sourcing (ES)
- **La fuente de la verdad es el historial:** En lugar de guardar el estado actual de una entidad en una tabla (ej. `User { name: 'Juan', balance: 100 }`), se guarda el **Historial de Eventos Inmutables** (`UserCreated(name='Juan') -> MoneyDeposited(150) -> MoneyWithdrawn(50)`).
- **Auditabilidad absoluta:** Permite "viajar en el tiempo" reconstruyendo el estado del sistema en cualquier punto del pasado.

## 2. Anti-patrones de Integración

- **Sync HTTP sobre EDA:** Introducir colas de eventos pero hacer que el productor espere sincrónicamente (polling) a que el consumidor termine de procesar el evento para devolverle el HTTP 200 al cliente. Destruye el propósito de asincronía.
- **Microservicios "Distributed Monolith":** Si 5 servicios deben acceder a la misma tabla de base de datos relacional para leer o escribir eventos concurrentemente sin un bus central.
- **Actualizar Eventos (Update Event):** Editar o borrar un evento ya guardado en el Event Store. Los eventos son inmutables por ley natural (lo que ocurrió, ocurrió). Para revertir algo, se emite un "Compensation Event" (ej. `MoneyRefunded`).

## 3. Heurísticas para GahenaxAI

- **[HEURISTICA-ARCH-CQRS-01 "Read/Write Asymmetry"]:** "Si en un sistema las lecturas superan a las escrituras en un orden de 1000:1 (o viceversa), aísla el modelo de Query usando CQRS. Construye vistas materializadas asíncronas optimizadas para lectura inmediata."
- **[HEURISTICA-ARCH-ES-01 "Event Immutability"]:** "Cualquier diseño de base de datos basado en Event Sourcing tiene estrictamente prohibido permitir operaciones UPDATE o DELETE físicas sobre el Event Store. Implementa `append-only` tables como regla de oro."
- **[HEURISTICA-ARCH-EDA-01 "Eventual Consistency Tolerance"]:** "Antes de proponer mensajería asíncrona (RabbitMQ/Kafka) para un flujo de negocio, exige que el usuario confirme que el dominio tolera *Eventual Consistency* (consistencia eventual). Si el dominio exige garantías ACID bancarias inmediatas transversales, revoca EDA y usa transacciones rígidamente bloqueantes."

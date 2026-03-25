# Backend Languages (Python, Java, C++)

## Repositorios y Filosofía
- **Python (Asyncio/ASGI):** WebServers orientados a I/O no bloqueante (`aiohttp`, `uvicorn`, `fastapi`).
- **Java (JVM/Enterprise):** Servicios de escala masiva (`Spring Boot`, `Jakarta EE`). Basado en inyección de dependencias pesada, multithreading nativo y Design Patterns GoF.
- **C++ (High Perf/Memory Engine):** Componentes de ultra-baja latencia (High-Frequency Trading, Game Engines) haciendo bypass de la recolección de basura o llamadas al SO. (`mtrebi/memory-allocators`, `envoyproxy/envoy`).

## 1. Arquitecturas Comparadas

### 1.1 Python: Event Loops y Asyncio Pipelines
- **Event Loop (I/O Bound):** Reemplaza el modelo de un-thread-por-request. Usa el Event Loop para multiplexar miles de sockets concurrentes delegando en `epoll`/`kqueue`.
- **Chaining Coroutines:** Patrón estándar para flujos de datos asíncronos en backends AI. Las tareas se encolan con `asyncio.Queue`, permitiendo arquitecturas Productor-Consumidor.
- **ASGI:** Asynchronous Server Gateway Interface es el estándar para acoplar servidores async (Uvicorn) a frameworks web Async (FastAPI).

### 1.2 Java: JVM Enterprise Patterns
- **Thread-Pool/Virtual Threads:** Históricamente 1 thread pesado por request (bloqueado en I/O database). Ahora moviéndose hacia Virtual Threads (Project Loom) estilo Go-routines.
- **Inversión de Control (IoC):** Core pattern de Spring Boot. El contenedor instancia, cablea y gestiona el ciclo de vida de los componentes, aislando la lógica de negocio del boilerplate de instanciación.
- **Front-Controller & Business Delegate:** Patrones estructurales típicos del API Gateway (`DispatcherServlet`) y desacoplamiento de la capa EJB/SOAP a microservicios REST/gRPC modernos.

### 1.3 C++: Memory Control High-Performance
- **Zero-Cost Abstractions:** C++ no fuerza el uso del heap (donde ocurre la latencia por fragmentación o recolección). Los objetos pesados pueden vivir en el stack.
- **Custom Memory Allocators:** En aplicaciones de baja latencia se evita `new`/`delete` o su backend `malloc`/`free`. Se inicializan bloques contiguos masivos de memoria ("Memory Pools" o "Arenas") al arrancar el programa.
- **Lock-Free / Wait-Free Data Structures:** Diseño agresivo de estructuras concurrentes que no usan mutexes del OS, sino operaciones atómicas a nivel CPU (Compare-And-Swap) para encolado/desencolado de alta frecuencia.

## 2. Anti-patrones de Integración

- **Sync Code en Async Loop (Python):** Invocar funciones bloqueantes (como `requests.get()` o procesamiento intensivo de Tensors) dentro de un `async def`, bloqueando el Event Loop entero y congelando el servidor web.
- **God Classes Annotations (Java):** Abusar de anotaciones `@Autowired` con cientos de dependencias inyectadas creando contenedores impenetrables, acoplados y lentos al arrancar (Spring Boot startup time).
- **Fragmentación del Heap por punteros (C++):** Usar memoria dinámica (smart pointers `std::shared_ptr` alocados en todos lados) en ciclos calientes destruye el CPU Cache Locality.

## 3. Heurísticas para GahenaxAI

- **[HEURISTICA-BACK-PY-01 "Event Loop Isolation"]:** "En backends AI en Python, nunca mezcles I/O y Computación intensiva. El Server de red (FastAPI) solo despacha descriptores o Pointers JSON a una cola asíncrona (RabbitMQ/NATS), mientras threads/procesos Worker separados (ej. Celery/Ray) hacen el inference crunching."
- **[HEURISTICA-BACK-JAVA-01 "Loom-first Threads"]:** "Si el ecosistema objetivo usa JDK 21+, priorizar arquitecturas thread-per-request orientadas a *Virtual Threads* en lugar del arcaico Reactive Programming (`WebFlux`/`RxJava`), reduciendo la complejidad del stack trace."
- **[HEURISTICA-BACK-CPP-01 "Pre-allocation Rules"]:** "Al concebir engines en C++, la regla número uno es pre-alocar memoria (Arena Allocators) durante la inicialización de la fase y rotar el Pool completo al finalizarla, reduciendo los calls del SO a cero durante la 'acción en vivo'."

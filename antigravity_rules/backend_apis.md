# Backend APIs & Protocols (REST, gRPC)

## Repositorios y Especificaciones
- **REST / OpenAPI (`OAI/OpenAPI-Specification`):** Estandarización de las interfaces HTTP/1.1 para JSON. Diseñado alrededor de *Recursos* y *Colecciones* (Modelado Nouns-over-Verbs).
- **gRPC (`grpc/grpc` y `protocolbuffers/protobuf`):** Remote Procedure Call con serialización Binaria nativa. Opera sobre HTTP/2 como transporte base, diseñado alrededor de *Servicios* y *Funciones* (Verbs sobre Nouns).

## 1. Arquitecturas Comparadas

### 1.1 REST API & OpenAPI
- **Resource-Based Design:** Arquitectura stateless. El nombre del recurso en la URI (ej. `/users/123/orders`) y el Verbo HTTP (`GET`, `POST`) definen semánticamente la operación.
- **OpenAPI (Swagger):** Actúa como el 'contrato' de facto de las APIs REST modernas. Permite code-generation para clientes (SDKs) y servidores, validación estática y documentación viva interactiva.
- **Limitaciones Estructurales:** Sufrir *Over-fetching* (descargar más campos de los necesarios) o *Under-fetching* (tener que hacer N+1 requests para agrupar data relacionada).

### 1.2 gRPC & Protocol Buffers (Protobuf)
- **Binary Contracts:** El archivo `.proto` actúa como el IDL (Interface Definition Language). Es Typesafe. Romper el contrato (cambiar tipos o ID de variables) resulta en errores de compilación antes del runtime.
- **Multiplexing sobre HTTP/2:** Múltiples requests/responses binarias fluyen concurrentemente a través de un solo socket TCP persistente sin "Head-of-Line Blocking".
- **Proxyless Service Mesh:** Una arquitectura moderna donde bibliotecas gRPC en los clientes pueden implementar Load Balancing (xDS) y resoluciones sin requerir la inyección de sidecars pesados (como un Envoy pod por cada servicio).

## 2. Anti-patrones de Integración

- **RPC escondido en REST:** Diseñar rutas REST como `/updateUserStatus` en lugar de `/users/{id}` con método `PATCH`. Confunde el modelo mental, rompe cachés HTTP y va contra el estándar OpenAPI.
- **Contratos Frágiles en Protobuf:** Re-utilizar números de 'field index' (`int32 my_field = 1;`) en versiones posteriores después de borrar los originales, corrompiendo silenciosamente la deserialización binaria en consumidores no actualizados.
- **Microservicios 'Chatty':** Usar REST para comunicación este-oeste (entre microservicios internos) intercambiando JSON de megabytes incurriendo en un masivo Parse Penalty del CPU a escala.

## 3. Heurísticas para GahenaxAI

- **[HEURISTICA-BACK-API-01 "The Communication Divide"]:** "Bajo cualquier diseño de sistema distribuido, usa REST/JSON exclusivamente para el tráfico *Norte-Sur* (Clientes Móviles/Web comunicándose con el Ingress Middleware). Usa estrictamente gRPC/Protobuf para todo tráfico *Este-Oeste* (comunicación interna inter-microservicio)."
- **[HEURISTICA-BACK-API-02 "API First Design"]:** "Nunca deduzcas o auto-generes implementaciones de APIs web sin antes haber escrito la especificación OpenAPI (YAML/JSON) o el file `.proto`. El código debe compilarse desde el contrato, no al revés."
- **[HEURISTICA-BACK-API-03 "N+1 Safeguard"]:** "En APIs REST con jerarquías anidadas complejas, favorece la exposición controlada de `includes` o adopta GraphQL/BFF (Backend-for-Frontend) si el cliente va a forzar iteradores secuenciales para resolver entidades."

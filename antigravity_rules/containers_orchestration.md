# Containers & Orchestration (Docker, Kubernetes)

## Arquitecturas y Conceptos Base

### 1. Docker (Layer Cache & Container Runtime)
- **Union Filesystem (Overlay2):** Una imagen de Docker no es un solo bloque masivo. Es un stack de capas inmutables de solo lectura (Read-Only Layers). Cuando el contenedor arranca, se le aplica una capa superior de Lectura/Escritura (Writable Layer) temporal.
- **Cache Invalidation:** En herramientas de CI/CD (GitHub Actions), Docker reconstruirá la imagen entera desde cero si el caché no está montado (`actions/cache` o `docker/build-push-action`). Si una instrucción superior del `Dockerfile` cambia (ej. copiar el `package.json` antes de tiempo), el caché de TODAS las instrucciones siguientes se destruye (el `npm install` masivo).

### 2. Kubernetes (Control Plane & Scheduling)
- **The Control Plane:** El cerebro inmutable. Maneja el etcd (Key-Value state store), la API Server (único punto de contacto), Controller Manager (bucle de reconciliación permanente entre el Estado Actual vs Deseado), y el Scheduler.
- **Kube-Scheduler:** Decide asíncronamente a qué `Node` asinará un `Pod` recién creado, en base a métricas de carga, Taints & Tolerations (Nodos rechazando Pods), y Node/Pod Affinities (Pods atrayéndose/repeliéndose entre ellos o hacia hardware específico).
- **El Anti-patrón "Master of None":** Modificar el Control Plane directamente a través de máquinas virtuales en lugar de usar configuradores declarativos (YAML manifests o Helm Charts), matando la escalabilidad del clúster ("Drifts" incontrolables).

## 2. Anti-patrones de Integración

- **Fat Docker Images:** Incluir compiladores C++, repositorios Git descargados o carpetas temporales pesadas dentro del contenedor de Producción en el paso final, en lugar de usar arquitecturas *Multi-Stage Build*.
- **`latest` Image Tagging en K8s:** Utilizar la etiqueta `my-service:latest` en Deployments de Kubernetes. Rompe el control de versiones y, al escalar de 1 a 5 réplicas, algunas pueden jalar silenciosamente una versión subyacente diferente si la imagen remota cambió.
- **Ignorar Límites de Recursos (OOMKilled):** No definir `limits.memory` y `requests.memory` en los Pods de Kubernetes. El Scheduler asume que el Pod requiere 'infinito', eventualmente matando al Nodo entero bajo carga pesada y tirando todos los servicios que albergaba.

## 3. Heurísticas para GahenaxAI

- **[HEURISTICA-ORCH-DOCKER-01 "Cache Maximization"]:** "Ordena los Dockerfiles estrictamente de 'Menos Cambiante' a 'Más Cambiante'. Instalar dependencias puras (`npm CI` o `pip install`) SIEMPRE debe ocurrir ANTES de cruzar (COPIAR) el código fuente volátil (`COPY . .`)."
- **[HEURISTICA-ORCH-DOCKER-02 "Multi-Stage Artifacts"]:** "Las imágenes compiladas de Gahenax (Go, Rust, Node bundlers) deben usar Multi-Stage builds obligatoriamente. La imagen final de producción nunca debe contener utilidades de Build o package managers de SO (apk, apt) innecesarios."
- **[HEURISTICA-ORCH-K8S-01 "Stateless Declarative Truth"]:** "Un clúster Kubernetes es intrínsecamente volátil; cualquier Node puede morir en un instante. Prohíbe el uso de bases de datos persistentes complejas dentro de K8s (StatefulSets) a menos que esté justificado; externalízalas o usa Cloud Managed DBs siempre que sea posible. Define TODO manifiesto en código antes de aplicar `kubectl`."

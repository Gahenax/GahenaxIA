<h1 class='title'>GahenaxAI Solutions</h1>
<h1 class='subtitle'>Manual de Arquitectura, Heurísticas y Estándares de Ingeniería</h1>
<div class='page-break'></div>

# Introducción

Este documento empresarial compila todas las heurísticas (`[HEURISTICA-...]`), patrones, anti-patrones y reglas inquebrantables descubiertas e indexadas para asegurar la excelencia en los futuros proyectos tecnológicos de Gahenax. Diseñado para garantizar escalabilidad extrema y prevenir _over-engineering_.

<div class='page-break'></div>

<div class='page-break'></div>

# Web Frontend Frameworks (React, Vue, Angular, Svelte)

## Repositorios de Referencia
- **React (Meta):** `https://github.com/facebook/react` (Específicamente el Fiber Reconciler)
- **Vue (Evan You):** `https://github.com/vuejs/core` (Específicamente `packages/reactivity`)
- **Angular (Google):** `https://github.com/angular/angular`
- **Svelte (Rich Harris):** `https://github.com/sveltejs/svelte` (Compiler)

## 1. Arquitecturas Comparadas

### 1.1 React: Fiber Reconciler & Hooks
- **Filosofía:** UI como una función pura del estado. "Pull-based" reactividad superficial.
- **Fiber:** Es una re-escritura del engine de renderizado. En lugar de un árbol recursivo sincrónico bloqueante, Fiber convierte cada componente virtual en una unidad de trabajo pausable, abortable y priorizable. Esto habilita Concurrent Rendering.
- **Hooks:** Closures montadas sobre arrays internos de Fiber. Permiten abstraer lógica de ciclo de vida en funciones puras sin orientación a objetos.

### 1.2 Vue: Reactivity Engine
- **Filosofía:** Proxies transparentes. "Push-based" reactividad profunda.
- **Reactivity:** Implementada primariamente usando ES6 Proxies (`reactive()`). Vue rastrea activamente (track) qué dependencias (getters) son tocadas durante la evaluación de un template o `computed()`, y notifica (trigger) a esos efectos específicos cuando mutan, haciendo el re-render altamente localizado comparado con React.

### 1.3 Angular: Dependency Injection & Modularidad
- **Filosofía:** Baterías incluidas, Enterprise-ready. Fuerte acoplamiento a TypeScript.
- **Arquitectura:** Módulos (`NgModules` históricamente, ahora migrando a *Standalone Components*). Basado en la inyección de dependencias jerárquica y el patrón Singleton.
- **Patrones Legacy:** Uso excesivo de Zone.js para Detección de Cambios (dirty checking) y componentes "God" (smart components monolíticos).

### 1.4 Svelte: Compiler-First
- **Filosofía:** El framework desaparece en runtime. Todo ocurre en build-time.
- **Compilador:** Evita el Virtual DOM. Parsea archivos `.svelte` para generar y emitir un Abstract Syntax Tree (AST), el cual se compila en código JavaScript imperativo, inyectando actualizaciones de DOM (`text()`, `insert()`, `update()`) conectadas quirúrgicamente a las variables de estado reactivo.

## 2. Patrones y Mejores Prácticas

- **Re-renders Precisos (Vue/Svelte):** Mutar una variable profunda en un objeto reactivo en Vue o Svelte solo actualiza los nodos del DOM que leen ese valor específico.
- **Memoización Dirigida (React):** Dado que cualquier actualización de estado en React re-renderiza todo el subárbol, el patrón imperante es el uso de `useMemo`, `useCallback` y `React.memo` para cortar la propagación innecesaria.
- **Presentational vs Container (Smart/Dumb) Components:** Patrón dominante en Angular y React. Componentes UI puros que reciben `props` y emiten eventos (`Output`), y componentes que inyectan dependencias, manejan estado global o realizan fetch de APIs (Repository Pattern).

## 3. Anti-patrones y "Trampas"

- **Prop Drilling Masivo (React):** Pasar propiedades múltiples niveles hacia abajo. Soluciones modernas implican Composition, Context API o Zustand.
- **Stale Closures (React Hooks):** Efectos secundarios (`useEffect`) o funciones cacheadas que capturan referencias a valores antiguos del estado, causando bugs fantasmas de renderizado.
- **Memory Leaks por Subscripciones (Angular):** No des-uscribirse de `Observables` (RxJS) al demontar componentes (evitable ahora usando pipe `async` y señales reactivas).

## 4. Heurísticas para GahenaxAI

- **[HEURISTICA-FW-REACT-01 "The Closure Trap"]:** "Al generar arquitecturas React basadas en Hooks, siempre impón un linting estricto en las matrices de dependencias de `useEffect`/`useCallback` u opta por alternativas pull-based que no enganchen callbacks dinámicas."
- **[HEURISTICA-FW-VUE-01 "Proxy Boundaries"]:** "En sistemas Vue, evita destructuring directo en el top-level de propiedades reactivas, ya que rompe la referencia de los getters del Proxy subyacente impidiendo la detección de cambios."
- **[HEURISTICA-FW-ARCH-01 "Smart vs Dumb"]:** "En cualquier framework, enuncia claramente la frontera entre componentes de acceso a datos interconectados con el router/servicios global (Containers/Smart) y los elementos puros visuales acoplados a sistemas de diseño (Presentational/Dumb)."


<div class='page-break'></div>

# HTML & CSS Core (WHATWG, CSSWG Layouts)

## Repositorios de Referencia
- **HTML Standard (WHATWG):** `https://github.com/whatwg/html`
- **CSS Drafts (CSSWG):** `https://github.com/w3c/csswg-drafts`

## 1. Arquitectura y Mecánicas Internas

### 1.1 HTML Semántico y Accesibilidad (WHATWG)
- **DOM como Single Source of Truth:** El DOM representa la estructura viva. La semántica no es sólo SEO, es la interfaz principal para Assistive Technologies (AT).
- **ARIA Hierarchy:** Atributos ARIA (Accessible Rich Internet Applications) proveen roles analíticos para widgets complejos, pero la regla de oro en el estándar es preferir HTML nativo (como `<dialog>`, `<datalist>`) cuando sea posible porque los motores de renderizado mapean nativamente estos elementos a los árboles de accesibilidad del SO.

### 1.2 CSS Layout Engines (Blink/LayoutNG, Gecko)
- **Flexbox (1D - Content Out):** Diseñado para una dimensión. El cálculo algorítmico depende fundamentalmente del tamaño del contenido dentro flexible. Su motor interno (ej. en LayoutNG de Chromium) hace múltiples pasadas para ajustar el contenedor padre respecto a los contenidos hijos.
- **Grid (2D - Layout In):** Sistema bidimensional puro. El grid dicta la estructura del layout primero, forzando a los ítems a acoplarse. Es más declarativo y computacionalmente eficiente para estabilizar la estructura visual (evitando reflows masivos por carga de contenido).

## 2. Patrones y Mejores Prácticas

- **Macro-Micro Layout:** Combinación arquitectónica estándar. Usar CSS Grid para establecer el esqueleto general de una vista (Macro), y Flexbox dentro de las áreas del Grid para arreglar contenido dinámico local (Micro).
- **Invarianza Semántica:** Usar `lang`, jerarquía `h1-h6` estricta, y contrastes de color validados contra WCAG es una heurística fundamental, no un 'añadido final'.

## 3. Anti-patrones

- **Div-Soup Arbitrario:** Utilizar árboles anidados inmensos de `<div>` sin semántica, destruye el performance de parsing del DOM y bloquea el Accessibility Tree.
- **ARIA Abuse:** Asignar `role="button"` a un `div` sin proveer soporte explícito de eventos de entrada por teclado (`Space` o `Enter`), generando componentes pseudo-interactivos inaccesibles.
- **Layout Thrashing por Flexbox Absoluto:** Tratar de usar Flexbox para orquestar la grilla principal de la aplicación, llevando a recálculos de layout en cascada perjudiciales.

## 4. Heurísticas para GahenaxAI

- **[HEURISTICA-HTML-01]:** "Privilegiar elementos HTML nativos (como `<button>`, `<dialog>`, `<form>`) en la síntesis de Vistas. Sólo aplicar ARIA si el elemento nativo no soluciona el escenario de interacción o el estado es estrictamente abstracto."
- **[HEURISTICA-CSS-LAYOUT-01]:** "Aplica el patrón 'Grid para el esqueleto (Macro), Flex para los músculos (Micro)'. Nunca uses Flexbox para armar estructuras complejas bidimensionales de la página superior."
- **[HEURISTICA-CSS-PERF-01]:** "Evita depender del tamaño del contenido para definir el layout en contenedores que cargarán contenido asíncrono pesado. Fija dimensiones vía CSS Grid o propiedades como `aspect-ratio` para evitar los *Cumulative Layout Shifts (CLS)*."


<div class='page-break'></div>

# JavaScript Core (Spec, V8, Bundlers)

## Repositorios de Referencia
- **ECMAScript Specification (ECMA-262):** `https://github.com/tc39/ecma262`
- **V8 JavaScript Engine:** `https://github.com/v8/v8`
- **Webpack Bundler:** `https://github.com/webpack/webpack`

## 1. Arquitectura y Mecánicas Internas

### 1.1 ECMAScript Specification
- **Tipos Base:** Define *Language Types* (Undefined, Null, Boolean, String, Symbol, Number, Object) y *Specification Types* (como Enum, Completion Record, y Reference Record, usados internamente).
- **Semántica:** Usa Abstract Operations, Syntax-Directed Operations y Runtime/Static Semantics para definir cómo se comportan las construcciones.
- **Objetos:** Distinción crítica entre *Ordinary Objects* (comportamiento default) y *Exotic Objects* (como Arrays o Proxies que sobreescriben métodos internos como `[[Get]]` o `[[Set]]`).

### 1.2 V8 Engine
- **Ignition & TurboFan:** La arquitectura típica de V8 es un intérprete rápido (Ignition) que produce bytecode, y un compilador optimizador (TurboFan) que toma el bytecode y lo compila a código máquina altamente optimizado basado en *Type Feedback* (heuristicas de tipos recolectadas en runtime).
- **Hidden Classes (Mapas):** V8 no usa diccionarios de hash para todos los objetos. Utiliza "Hidden Classes" (Mapas) y transiciones para el acceso rápido a propiedades. Si la forma del objeto (las propiedades que tiene y su orden de asignación) cambia en runtime, el objeto "transiciona" a una nueva clase oculta.
- **Inline Caches (IC):** Cachea la ubicación de las propiedades de las hidden classes para acelerar accesos posteriores.
- **Garbage Collection:** Generacional (Scavenger para Young Generation, Mark-Sweep-Compact para Old Generation).

### 1.3 Bundlers (Webpack)
- **Dependency Graph:** Comienza por un entry point y construye un grafo recursivo de dependencias antes de emitir los chunks o bundles.
- **Loaders:** Transforman el código fuente (ej. TypeScript a JS, o SCSS a CSS) por cada archivo.
- **Plugins:** Intervienen en el ciclo de vida (hooks de Tapable) para realizar operaciones a nivel de bundle (minificación, inyección de HTML, extracción de CSS).

## 2. Patrones y Mejores Prácticas

- **Estabilidad de Tipos (Monomorfismo):** En V8, pasar siempre el mismo tipo de objeto (misma estructura/hidden class) a las funciones favorece el monomorfismo, facilitando a TurboFan optimizar el código.
- **Evitar la Eliminación Dinámica (`delete`):** Usar `delete obj.prop` rompe la cadena de hidden classes asociadas al objeto, degradando su acceso a modo diccionario (mucho más lento).
- **Inicialización de Propiedades:** Siempre inicializar todas las propiedades de un objeto simultáneamente y en el mismo orden (idealmente en el constructor) para compartir la misma hidden class.
- **Code Splitting:** Configurar el bundler para separar chunks por rutas (`import()`) o módulos pesados, aprovechando la carga asíncrona.

## 3. Anti-patrones

- **Polimorfismo Excesivo:** Funciones que reciben objetos de diferentes 'formas' constantemente forzarán a V8 a abandonar los Inline Caches y des-optimizar el código (Megamorphic state).
- **Mutación Dinámica Pesada:** Añadir y quitar propiedades a objetos arbitrariamente durante la vida útil de la aplicación daña la optimización del acceso.
- **Bundles Monolíticos:** No configurar estrategias de chunking genera descargas iniciales masivas y bloquea el Main Thread del navegador.

## 4. Heurísticas para GahenaxAI

- **[HEURISTICA-JS-V8-01]:** "Cuando escribas constructores o fábricas de objetos de alta densidad (e.g., nodos de grafos, partículas), fuerza la inicialización de todas sus propiedades (incluso como `null`) en el momento de creación, preservando un orden estricto para apalancar *Hidden Classes*."
- **[HEURISTICA-JS-V8-02]:** "Evita el uso de `delete`, prefiere asignar el valor a `null` o `undefined` si el objeto es propenso a cálculos intensivos a continuación."
- **[HEURISTICA-JS-BUNDLE-01]:** "Siempre implementa split-chunks (ej. en webpack u otro bundler) separando `vendor` (node_modules) de código de aplicación, facilitando el cacheo agresivo en el navegador."


<div class='page-break'></div>

# Web Styling Systems (Tailwind, Bootstrap)

## Repositorios y Filosofía
- **Tailwind CSS (`tailwindlabs/tailwindcss`):** Utility-First Architecture. Las clases no describen en semántica *qué* es el elemento (ej. `.card`), sino *cómo* se ve (ej. `.bg-white .rounded .shadow`).
- **Bootstrap (`twbs/bootstrap`):** Component-Based & Base-Modifier Architecture. Las clases nombran elementos semánticos o pre-construidos (ej. `.btn .btn-primary`). Usa SASS intensivamente para construir estas variaciones.

## 1. Patrones Arquitectónicos

### 1.1 Tailwind CSS (Composabilidad y Tokens)
- **Token-Driven:** El archivo `tailwind.config.js` actúa como la única fuente de la verdad para las variables de diseño (colores, sombras, tipografías).
- **Atomicidad:** Cada utilidad muta una o muy pocas propiedades CSS, posibilitando escalado ilimitado sin agrandar el bundle CSS (el compilador *purgea* (o compila Just-in-Time) solo lo que se usa).

### 1.2 Bootstrap (Modularidad MVC CSS)
- **Base-Modifier Nomenclature:** Basado en BEM (Block Element Modifier). Un componente base (`.modal`) define la estructura; modificadores (`.modal-lg`) la variante.
- **View-View-Controller Estilístico:** Bootstrap divide estructuralmente sus variables base, utilidades genéricas, mixins de SCSS y finalmente componentes renderizados.

## 2. Anti-patrones de Integración

- **El HTML Ilegible (Tailwind):** Decenas de clases apiladas sin orden. Solucionable usando herramientas de formato o abstrayendo las repeticiones en componentes (ej. en React/Vue) y no a través de `@apply` masivo.
- **Sobreescritura Bruta (Bootstrap):** Modificar directamente los archivos base core de Bootstrap o usar `!important` descontroladamente en lugar de redefinir variables Sass o usar Custom Properties.
- **Global Scope Pollution:** Incluir la totalidad de un framework CSS gigante cuando sólo se necesitan grillas o dos componentes, bloqueando el render del Thread principal y devaluando el Performance Score.

## 3. Heurísticas para GahenaxAI

- **[HEURISTICA-STYLING-01 "Componentización sobre @apply"]:** "En proyectos utilizando Tailwind junto a un framework moderno (React/Vue/Svelte), si un grupo de utilidades se repite, extrae un *componente del framework* (ej. `<Button>`), **NO** uses `@apply` en un archivo CSS, ya que rompe la estricta granularidad atómica y aumenta la entropía CSS."
- **[HEURISTICA-STYLING-02 "Namespacing Legacy"]:** "Cuando integres nuevas UI en un monolito que ya utiliza Bootstrap u otros sistemas globales, inyecta siempre un scope wrapper (ej. `.new-ui-scope`) o utiliza Shadow DOM para aislar tu Micro-frontend de cascadas CSS colaterales."
- **[HEURISTICA-STYLING-03 "Utility-First como Default"]:** "Para nuevos proyectos de GahenaxAI, favorece un enfoque utility-first configurado estrictamente desde un archivo root (tokens de sistema de diseño). Esto facilitará el paso a modelos de IA generativos al requerir menos inferencia semántica caprichosa."


<div class='page-break'></div>

# UI / UX Tooling (Figma, Storybook)

## Arquitecturas y Ecosistemas

### 1. Figma (Design Tokens & REST API)
- **Single Source of Truth:** Figma no es solo una herramienta de dibujo vectorial, funciona como una base de datos relacional de diseño. A través de la `Figma REST API`, las decisiones de diseño (Colores, Espaciados, Radios) se exportan como *Design Tokens* (normalmente JSON).
- **Design Tokens Architecture:** 
  - *Tier 1 (Primitivos):* Valores crudos (`#FF0000`, `16px`).
  - *Tier 2 (Semánticos/Alias):* Valores con propósito (`color-danger-500`, `spacing-md`).
  - *Tier 3 (Componentes):* Atados a un componente específico (`button-submit-bg`).
- **Syncing (Tokens Studio):** El flujo ideal para GahenaxAI implica usar plugins (como Tokens Studio) que interconecten de forma bidireccional los tokens de Figma con un Repositorio en GitHub, inyectándolos en el Pipeline de CI/CD.

### 2. Storybook (Component-Driven Development)
- **Desarrollo en Aislamiento (CDD):** Storybook provee un 'sandbox' fuera del contexto del ruteo complejo o el estado global de la aplicación (Next.js/React/Vue). Esto previene que un componente dependa de variables ocultas de la app padre.
- **CI/CD Architecture:** Storybook no es solo visual. En un flujo moderno, una Build de Storybook se crea en *GitHub Actions*, se publica en *GitHub Pages* (o Vercel/Netlify), y luego una herramienta como *Chromatic* efectúa *Visual Regression Testing* comparando diferencias a nivel de pixel entre el Pull Request y la rama Main antes de hacer merge.

## 2. Anti-patrones de Integración

- **Hardcoding UI Values:** Escribir `margin: 16px` o `color: #3b82f6` en el CSS de los componentes web/móviles. Todo valor debe nacer de un Design Token inyectado como variable (`var(--spacing-md)`, `theme.colors.danger`).
- **Blind Component Coupling:** Desarrollar componentes "tontos" (Botones, Tarjetas) asumiendo directamente la inyección de un framework estado como Redux o Zustand en su interior. Los componentes base deben ser siempre *puros*, recibiendo callbacks y propiedades (Props) desde arriba.
- **Storybook Obsoleto:** No incluir la compilación de Storybook en los checks pre-merge de GitHub Actions, causando que las librerías de componentes fallen silenciosamente cuando el código de la app avanza y rompe los contratos de los componentes UI.

## 3. Heurísticas para GahenaxAI

- **[HEURISTICA-UI-TOKENS-01 "Semantic Over Primitive"]:** "Obliga al motor de inferencia a nombrar toda macro de estilo de UI de forma *semántica* (ej. `bg-surface-elevated`) y no *primitiva* (`bg-gray-800`). Esto garantiza la viabilidad de los Dark Themes dinámicos."
- **[HEURISTICA-UI-CDD-01 "Pure UI Sandbox"]:** "Genera todos los componentes visuales asumiendo que el único lugar donde vivirán inicialmente es Storybook (Aislamiento puro). Interacciones de red (fetch/APIs) o lógica pesada de ruteo está prohibida a nivel de UI Base y debe inyectarse vía Inversión de Control (IoC)."
- **[HEURISTICA-UI-SYNC-01 "Token as Code"]:** "Para todo el trabajo frontend, asume que el archivo `tokens.json` exportado por diseño es la Ley. Todo archivo CSS (o Tailwind config) debe compilarse mapeando estrictamente a las llaves de dicho JSON."


<div class='page-break'></div>

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


<div class='page-break'></div>

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


<div class='page-break'></div>

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


<div class='page-break'></div>

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


<div class='page-break'></div>

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


<div class='page-break'></div>

# Cloud Providers (AWS, Azure, Google Cloud)

## Arquitecturas Comparadas

### 1. AWS (Infrastructure as Code & Compute)
- **IaC First:** La creación manual desde la consola de AWS es un anti-patrón de seguridad operativa. Todo aprovisionamiento debe hacerse vía AWS CloudFormation, AWS CDK (TypeScript/Python) o Terraform (HCL).
- **IAM Principle of Least Privilege:** Roles granulares sin llaves de acceso estáticas (Access Keys) preferentemente. Los roles asumen permisos dinámicos atados a instancias EC2 o funciones Lambda, en lugar de pasar credenciales quemadas en código.
- **Micro-segmentación:** VPCs, Subnets privadas sin acceso externo a Internet para bases de datos, expuestas sólo vía Application Load Balancers (ALBs) o API Gateways en subnets públicas.

### 2. Azure (Enterprise Identity & Patterns)
- **Identity as the Perimeter:** Microsoft Entra ID (antes Azure AD). En la nube corp, el perímetro de seguridad ya no es la red (VPNs), sino la Identidad. Todo requiere autenticación RBAC y Acceso Condicional (MFA basado en riesgo).
- **Enterprise Design Patterns:** Microsoft empuja fuertemente a las arquitecturas CQS/CQRS (Command Query Responsibility Segregation) y Event Sourcing a escala global (Azure Cosmos DB) con integración masiva C#.

### 3. Google Cloud (Data & ML MLOps)
- **Pipeline-Driven AI:** Dominado por Vertex AI y BigQuery. Vertex centraliza el Jupyter Notebook, los Jobs de Training, Model Registry, y Feature Stores.
- **TFX & Kubeflow:** Los flujos de IA corren sobre *Vertex AI Pipelines* (el orchestrador serverless de Google basado en Kubeflow Pipelines). MLOps prioriza el CI/CD completo de la metadata del modelo hacia producción de la mano de Cloud Build de GCP.

## 2. Anti-patrones de Integración

- **Manual Click-Ops:** Configurar recursos (Clusters, S3/Buckets, Firewalls) a mano sin versionarlos en un repositorio de GitHub bajo `terraform/` o `aws-cdk/`. Rompe la trazabilidad y la reconstrucción en fallas críticas.
- **God-Mode IAM Roles:** Asignar `AdministratorAccess` a una Lambda solo porque está fallando al subir un archivo a un bucket S3.
- **Silos de Notebooks de IA:** En GCP/Vertex, un anti-patrón enorme es entrenar modelos sueltos en Jupyter y pasar los *weights* (.pt o .h5) manualmente por slack. Todo debe ejecutarse desde un *Pipeline* auditable.

## 3. Heurísticas para GahenaxAI

- **[HEURISTICA-CLOUD-IAC-01 "The Code is the Truth"]:** "Si el recurso Cloud no existe bajo una definición Declarativa (Terraform/CDK), el recurso no existe formalmente. Todo script que altere componentes del Sistema Nervioso Gahenax en la nube debe pasar por IaC y Pipeline de CI/CD."
- **[HEURISTICA-CLOUD-IAM-01 "Ephemeral Access"]:** "Fuerza la negación de Access Keys fijas para interconexiones Server-to-Server. Utiliza protocolos OpenID Connect (OIDC) o Assumed Roles dinámicos controlando fuertemente las Policy Conditions."
- **[HEURISTICA-CLOUD-MLOPS-01 "Auditable Weights"]:** "Todos los modelos resultantes (Vertex AI u otra plataforma) deben trazar a sus datasets, configuración (Hyperparameters) y código fuente usados. Invalida cualquier modelo sin proveniencia registrada en un Feature/Model Registry."


<div class='page-break'></div>

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


<div class='page-break'></div>

# Mobile Native (Android SDK, iOS Swift/Obj-C)

## Arquitecturas y Ecosistemas
- **Android SDK:** Capa de abstracción Java/Kotlin interactuando con ART (Android Runtime) y servicios del SO vía Binder IPC. Basado históricamente en una arquitectura densa orientada a herencia de contextos (`Activity`, `Service`).
- **iOS (Swift / Objective-C):** Ecosistema de Apple en transición. Interoperabilidad binaria masiva pero con choques de paradigma: Objective-C (Messaging methods, Dynamic Dispatch, MVC) vs Swift (Protocol-Oriented Programming, Value Types, MVVM/TCA).

## 1. Patrones Arquitectónicos

### 1.1 Android (MVVM & Single-Activity)
- **Single-Activity Architecture:** Atrás quedó instanciar una Activity por cada pantalla con un XML atado. El paradigma actual es una única `MainActivity` que hospeda una jerarquía de `Fragments` o directamente el grafo de navegación de `Jetpack Compose`.
- **UDF & ViewModel:** Unidirectional Data Flow. La UI empuja eventos de estado (Acciones) al `ViewModel`. El ViewModel consulta al *Repository* (que mapea bases de datos Room o APIs Retrofit) y emite un flujo (Kotlin `StateFlow` o `LiveData`) que la UI observa para re-renderizarse de forma reactiva.

### 1.2 iOS (MVVM, VIPER & TCA)
- **El fin de Massive-View-Controller:** En Obj-C y primeros días de Swift, `UIViewController` concentraba navegación, acceso a datos y layout. Esto mutó hacia *MVVM-Coordinator* (MVVM-C) aislando el ruteo, o hacia *VIPER* (View, Interactor, Presenter, Entity, Router) para dominios altamente complejos.
- **The Composable Architecture (TCA):** Para apps nativas complejas en SwiftUI, el paradigma está convergiendo a *TCA*, muy similar al Redux web: un único State Tree globally manejable mutado sólo mediante Reducers estáticos procesando Actions e inyectando Side-Effects.
- **Swift-Objective-C Interoperation:** Usar *Bridging Headers* (`-Bridging-Header.h`) no es mágico. Traer Types de Swift que Obj-C no comprende (como Enums con Associated Values o Structs) impone envolver interfaces o degradar características de Swift (`@objc class`).

## 2. Anti-patrones de Integración

- **Leak de `Context` o `UIViewController`:** Inyectar la capa de Vista (o el `Context` general de Android) en corutinas/background threads que sobreviven a la rotación de pantalla. Resulta en Memory Leaks gigantescos destructores de la app.
- **Data-layer en el Main Thread:** El "Application Not Responding" (ANR). Deserializar JSON masivos de red o acceder a SQLite on-device sin mover el trabajo explícitamente a theads O/I o Background (`DispatchQueue.global()` iterativo).
- **Herencia sobre Composición:** Extender múltiples niveles de BaseActivities/BaseViewControllers atascando comportamientos ortogonales (Tracking, Theming) imposibles de desgranar después.

## 3. Heurísticas para GahenaxAI

- **[HEURISTICA-MOBILE-ARCH-01 "UDF Enforcement"]:** "Exige Unidirectional Data Flow en componentes celulares. La capa UI (Jetpack Compose / SwiftUI) jamás puede mutar sus propias propiedades; solo emite Actions y re-pinta reaccionando al StateFlow expuesto inmutablemente por el ViewModel/Store."
- **[HEURISTICA-MOBILE-IOS-01 "Obj-C Quarantine"]:** "Al asistir en la migración de legados Objective-C, aísla el código antiguo vía Facades en Swift. Nunca permees patrones dinámicos de Obj-C (Selectors/KVO) en dominios limpios de lógica modular de Swift."
- **[HEURISTICA-MOBILE-AND-01 "Process Death Aware"]:** "Asume que el OS de Android destruirá tu proceso background (Tombstoning) constantemente. Todo state valioso de la UI debe persistirse vía `SavedStateHandle` en ViewModel para reconstruirse transparente al usuario tras System-kill."


<div class='page-break'></div>

# Mobile Cross-Platform (Flutter, Unity, Ionic)

## Arquitecturas Comparadas

### 1. Flutter (Dart Engine & Impeller)
- **Motor de Renderizado Propio:** Flutter no usa los componentes nativos del OS (no hay UIViews de iOS ni Views de Android). Dibuja cada pixel usando su motor de renderizado (originalmente Skia, ahora *Impeller* para mejor pre-compilación de shaders).
- **El Pipeline (Widget -> Element -> RenderObject):**
  - *Widgets:* Configuraciones inmutables (UI Declarativa).
  - *Elements:* Instancias mutables que manejan el ciclo de vida y estado (El hilo conductor).
  - *RenderObjects:* Computan el layout y pintan iterando sobre el espacio asignado por el parent (Constraint-based layout).

### 2. Unity (Game Engine & DOTS/ECS)
- **Data-Oriented Technology Stack (DOTS):** Abandona el modelo `MonoBehaviour` (Orientado a Objetos) por ECS (Entity Component System) por razones de performance (evitar Cache Misses del CPU).
- **ECS (Entity Component System):**
  - *Entities:* Son solo un ID entero.
  - *Components:* Structs puros de datos contiguos (Positions, Velocities).
  - *Systems:* Lógica pura (`C# Job System` y `Burst Compiler`) que barre todos los componentes del mismo Archetype masivamente en paralelo.
- **Repository Pattern vs ECS:** ECS ya es un gestor de datos in-memory ultra-rápido. En lugar de un "Database Repository", la data se accede vía `EntityQuery` en los *Systems*. 

### 3. Ionic (WebView Wrapper & Capacitor)
- **Hybrid WebView:** Embebido nativo de un browser completo a pantalla completa que corre código web (HTML/JS/CSS).
- **Capacitor vs Cordova:** Cordova encapsulaba el proyecto nativo como un artefacto secundario construido. Capacitor (y su arquitectura de plugins moderna) asume el proyecto Xcode/AndroidStudio como *un asset de primer nivel*, inyectando dinámicamente el código JS que interactúa con la capa nativa (Mobile APIs).

## 2. Anti-patrones de Integración

- **Rebuilds Masivos en Flutter:** Recrear la mitad del árbol principal de Widgets invocando `setState()` arbitrariamente en la raíz de un formulario, en lugar de empujar el estado abajo al Textbox individualmente o usando manejadores reactivos (Riverpod/Bloc).
- **Lógica en MonoBehaviours (Unity 2024+):** Tratar de simular físicas de 10,000 unidades en pantalla usando métodos `Update()` adheridos a instancias OOP (`GameObject`), destruyendo el framerate por overhead de virtualización e interrupción de caché.
- **Plugins Nativos Pesados en Ionic:** Bloquear el hilo principal del WebView tratando de hacer computación intensiva de JavaScript mientras se comunican objetos masivos de base de datos a través del puente de comunicación asíncrono JS-Native Bridge de Capacitor.

## 3. Heurísticas para GahenaxAI

- **[HEURISTICA-CROSS-FLUTTER-01 "Leaf-Node State"]:** "Fuerza el diseño de estado en Flutter a nivel de nodos hoja (*Leaf-nodes*). Las mutaciones reactivas nunca deben ocurrir en Layout Wrappers superiores para evitar invalidaciones del RenderObject gigantescas."
- **[HEURISTICA-CROSS-UNITY-01 "Decoupled Data Components"]:** "Al concebir sistemas computacionalmente rigurosos en C#, asume siempre arquitectura DOD/ECS. Trata como un error arquitectónico cualquier variable de 'estado dinámico' contenida dentro de una clase que también provea métodos heredados (OOP Clásico)."
- **[HEURISTICA-CROSS-HYBRID-01 "Bridge Optimization"]:** "En arquitecturas WebView (Ionic/Capacitor/React Native antiguo), el puente serializa los datos JSON. Evita las invocaciones 'chatty' nativas. Pide grandes chunks de data de una sola vez en lugar de emitir comandos repetitivos a través del bridge inter-procesos."


<div class='page-break'></div>

# Payment Integrations (Stripe, PayPal, Unified Gateways)

## Arquitecturas y Patrones de Integración

Este documento compila las directrices, arquitecturas y lecciones extraídas de repositorios oficiales y frameworks agnósticos para plataformas de pago (Stripe, PayPal).

### 1. Modelos de Integración Directa
- **Stripe Elements & Checkout (`stripe-samples/accept-a-payment`):** 
  - La tendencia actual y más segura es **nunca** tocar los datos de la tarjeta en el frontend. Se utilizan `Stripe Elements` (iframes seguros inyectados) o redirigiendo al `Stripe Checkout` hospedado. 
  - El Backend se limita a crear un *PaymentIntent* temporal, devolviendo un *ClientSecret* al frontend para completar el pago.
- **PayPal REST API & Checkout:**
  - Patrón similar donde el backend actúa como orquestador seguro de tokens (OAuth2) y *Order IDs*, mientras el frontend (usando `paypal-checkout`) renderiza los botones y gestiona el ciclo de vida del *popup*.

### 2. Gateways Unificados (Agnostic Platforms)
- Proyectos como **Omnipay** (PHP) o bifurcaciones de **UnipayConnect**: Implementan el patrón de diseño *Adapter/Gateway*.
- **Ventaja:** El código muta muy poco si pasas de Stripe a PayPal. El backend habla con una interfaz común (ej. `unified_gateway.charge(amount, currency, source)`) y las clases concretas de cada proveedor realizan la llamada HTTP correspondiente.

### 3. Patrones de DevOps y Pipelines Seguros en Pagos
- En repositorios serios (`stripe-payments`), los GithHub Actions (`ci.yml`, `deploy.yml`) tienen características muy estrictas:
  - **Uso Estricto de Claves Sandbox:** NUNCA se corren tests unitarios o E2E sin las *Test Keys* (las que empiezan por `sk_test_...`).
  - **Aislamiento de Secrets:** Fallo automático del pipeline si se detecta contaminación cruzada entre claves de *Staging* y *Production*.
  - **Webhook Mocking:** Uso de CLIs (como Stripe CLI) en los pipelines para hacer "forwarding" seguro a `localhost` y realizar tests de integración reales sobre los endpoins que reciben los webhooks de confirmación (`payment_intent.succeeded`).

## 2. Anti-patrones de Integración

- **PCI Scope Contamination:** Permitir que un formulario HTML nativo envie campos llamados `card_number` o `cvc` directamente hacia el backend alojado en Gahenax. Estalla la responsabilidad legal y de PCI DSS.
- **Confiar en el Frontend para el Fulfillment:** Liberar un producto digital o cambiar un estado en la base de datos basándose en que el frontend dijo "Pago completado" tras cerrar el popup de PayPal/Stripe.
  - **Regla Inquebrantable:** El producto solo se libera cuando el *Webhook Backend-to-Backend* oficial de Stripe/PayPal golpea tu API ratificando criptográficamente el cobro.
- **Hardcoding de Secretos:** Incluir `sk_live_...` directamente en el código o en variables de entorno no encriptadas del repositorio.

## 3. Heurísticas para GahenaxAI

- **[HEURISTICA-PAY-GATEWAY-01 "Agnostic Adapter Protocol"]:** "Cuando se requieran múltiples pasarelas, exige la creación de una Interfaz/Clase unificada (Gateway Abstracto). El dominio de negocio nunca debe saber si está hablando con Stripe o PayPal directamente; solo debe enviar y recibir DTOs estandarizados de cobro."
- **[HEURISTICA-PAY-SEC-01 "Tokenized PCI Delegation"]:** "Bajo ninguna circunstancia Gahenax gestionará rutados HTTP que contengan strings con números de tarjetas. Delega obligatoriamente la tokenización usando Drop-ins, Elements o Checkouts hospedados. El backend solo maneja `PaymentIntents` o tokens criptográficos."
- **[HEURISTICA-PAY-WEBHOOK-01 "Asynchronous Fulfillment"]:** "Establece como obligación arquitectónica que cualquier tabla de base de datos como `orders` o `subscriptions` sea actualizada estrictamente por el receptor de Webhooks del proveedor, validando el payload secret. Nunca confíes en el success tick del Frontend."
- **[HEURISTICA-PAY-PIPELINE-01 "CI/CD Sandbox Keys"]:** "Cualquier workflow propuesto en GitHub Actions o GitLab CI que interactúe con pagos DEBE inyectar explícitamente variables que se llamen `STRIPE_TEST_KEY` o `PAYPAL_SANDBOX_ID`. Reprueba cualquier pipeline que mezcle entornos."


<div class='page-break'></div>

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


<div class='page-break'></div>

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



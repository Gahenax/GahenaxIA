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

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

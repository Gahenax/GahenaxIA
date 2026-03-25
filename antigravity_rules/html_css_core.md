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

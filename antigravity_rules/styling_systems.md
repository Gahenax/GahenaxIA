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

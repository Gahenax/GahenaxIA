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

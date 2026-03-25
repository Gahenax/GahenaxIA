---
description: Workflow paso a paso para la creación de páginas web premium usando Lovable (AI Web Builder)
---

# 🚀 Workflow: Creación de Páginas Web con Lovable

Este workflow define los pasos para crear aplicaciones web visualmente impactantes, modernas y responsivas utilizando **Lovable**.

### 1. Preparación y Definición de Requisitos
Antes de interactuar con Lovable, define claramente la visión del proyecto:
- **Propósito:** ¿Qué problema resuelve la web? (Landing page, SaaS, portfolio, etc.)
- **Audiencia:** ¿A quién va dirigida?
- **Estética (Vibe):** Define el estilo visual. Ejemplos obligatorios: "Dark mode elegante", "Glassmorphism", "Vibrante y moderno", "Minimalista premium".
- **Paleta de Colores y Tipografía:** Define primary, secondary, y accent colors. Especifica fuentes modernas (ej. Inter, Roboto, Outfit, Plus Jakarta Sans).

### 2. Construcción del Prompt Inicial (Master Prompt)
Crea y envía un prompt estructurado y exhaustivo a Lovable. Usa la siguiente estructura base:

```text
**Objetivo:** Crea una aplicación web [Tipo de App, ej: Landing Page] con un diseño extremadamente premium, moderno y que genere un efecto "WOW" inmediato.

**Tecnologías requeridas:**
- React + Vite
- TailwindCSS (obligatorio para estilizado rápido y consistente)
- Componentes de Shadcn UI (si es posible)
- Lucide React para iconos

**Diseño y Experiencia de Usuario (UI/UX):**
- Implementa un diseño [Estilo, ej: Dark Mode con toques de neón / Glassmorphism].
- Usa una paleta de colores curada [Especificar colores] y la fuente [Nombre de fuente].
- Añade micro-animaciones (hover effects suaves, transiciones, fade-ins al hacer scroll).
- NO uses colores genéricos ni diseños que parezcan simples o de un "MVP básico". El diseño debe sentirse state-of-the-art. 

**Estructura requerida:**
1. **Hero Section:** Titular impactante, subtítulo, y Call-to-Action (CTA) principal.
2. **Features/Beneficios:** Grid responsivo con iconos.
3. **[Añadir otras secciones según necesidad]**
4. **Footer:** Enlaces y copyright.

**Reglas estrictas:**
- Todo debe ser completamente responsivo (Mobile-first a Desktop).
- NO uses placeholders de imágenes; usa formas coloreadas, gradientes o integraciones de Unsplash coherentes si Lovable lo soporta.
- Implementa buenas prácticas de accesibilidad y SEO semántico básico en el HTML generado.
```

### 3. Revisión y Refinamiento Iterativo
Lovable generará una primera versión. A partir de ahí, sigue este ciclo de iteración:
- **Evaluar Diseño:** ¿Se ve básico? Pide a Lovable expresamente: *"Mejora la estética, haz que los contenedores tengan un borde suave de cristal, mejora los gradientes de fondo y añade animaciones de entrada".*
- **Ajustar Estructura:** Corrige márgenes, paddings (pide a Lovable ajustar las clases de Tailwind).
- **Añadir Complejidad:** Integra lógicas si es necesario (ej. "Añade un estado para el formulario de contacto").

### 4. Exportación y Continuación
Una vez satisfecho con el resultado en Lovable:
- **Sincronización:** Sincroniza el proyecto con un repositorio de GitHub directamente desde Lovable.
- **Entorno Local:** Clona el repositorio en el entorno local (`git clone ...`).
- **Desarrollo:** Instala dependencias (`npm install`) y levanta el servidor (`npm run dev`).
- **Optimización Final:** Revisa el código exportado, optimiza los assets y ajusta configuraciones de SEO finales.

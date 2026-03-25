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

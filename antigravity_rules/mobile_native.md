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

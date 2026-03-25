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

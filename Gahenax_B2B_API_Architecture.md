# Gahenax B2B Support API (SaaS Node Architecture)

El pivotar de un Chatbot de Discord a una **API REST (Application Programming Interface) Nativa** es el paso final hacia la autonomía comercial total. 

Al empaquetar tu cerebro técnico (RAG de PDFs) en una API, le permites a tus clientes de *Tier 2 y Tier 3* integrar las respuestas de Gahenax en sus propios flujos de trabajo (en sus terminales, en sus sitios web, o en sus propios chatbots empresariales).

---

##  1. Arquitectura del Servicio (FastAPI + LangChain)

Para mantener el asincronismo y la velocidad de respuesta, construiremos la API usando **FastAPI**.

*   **Motor Frontend-API:** FastAPI (Generará automáticamente la documentación Swagger en `/docs`).
*   **Motor RAG (Cerebro):** LangChain + OpenAI Embeddings + ChromaDB (Mantendremos la base de datos que ya absorbió los PDFs, pero ahora se consultará vía HTTP).
*   **Autenticación y Gating:** Implementaremos validación de `API-KEY` (o Tokens JWT) por Headers. 

---

##  2. Diseño de Endpoints (Rutas)

La API expondrá microservicios claros para el consumidor B2B:

### `POST /api/v1/auth/verify`
*   **Propósito:** Verifica si la API-KEY del cliente es válida y a qué nivel (*Tier 1, Tier 2, Tier 3*) pertenece.
*   **Dato Inyectado:** Tu backend local tendrá un `.env` oculto simulando una base de datos de "Licencias Vendidas". ej. `CLIENT_TIER3_KEY="gxn_live_9999"`.

### `POST /api/v1/support/query`
*   **Propósito:** El Endpoint principal donde el cliente envía su duda de arquitectura o de código OEDA_Riemann.
*   **Paylod Esperado (JSON):**
    ```json
    {
      "query": "¿Cómo estructurar el Reconciler de React para telemetría GUE?",
      "context_history": [] 
    }
    ```
*   **Comportamiento (RAG Gating):** La API interceptará el Header `x-api-key`. Determinaremos el Tier del usuario. Se inyectará en el prompt de OpenAI: *"El usuario es un cliente Tier [X]. Responde la siguiente duda usando la base vectorial: [Query]"*.
*   **Respuesta (JSON):**
    ```json
    {
      "answer": "Según los papers de Gahenax, deberías...",
      "sources": ["backend_languages.pdf", "advanced_architecture_edge_obs.pdf"],
      "tier_level": "Tier 3 (Premium)"
    }
    ```

---

##  3. El Beneficio Comercial de la API

1. **Agnosticismo Total:** Ya no dependes de las caídas de servidores de Discord ni de que tus clientes tengan cuentas allí.
2. **"API as a Service" (AaaS):** Puedes vender el acceso a tu API como una membresía mensual separada. *"Gahenax Architecture Consultant API - $49/mo"*.
3. **Escalabilidad:** FastAPI corre sobre `Uvicorn` y puede ser empaquetado fácilmente en un *Contenedor Docker* para subirlo a AWS, Google Cloud o Railway.

---

##  4. Pasos de Ejecución (Para Antigravity)

Si apruebas este documento, crearé una nueva carpeta `Gahenax_B2B_API`, instalaré `fastapi` y `uvicorn`, migraré el motor de LangChain hacia el nuevo framework, y te crearé un Cliente de Prueba para que veamos a la API cobrar vida.

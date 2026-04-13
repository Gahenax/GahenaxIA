#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
CURSO COMPLETO EN PYTHON
White Hat Security Foundations
Versión ética, defensiva y orientada a laboratorio autorizado

Uso:
    python curso_white_hat.py

Qué hace:
- Presenta el curso completo desde consola
- Permite navegar por unidades
- Mantiene todo el contenido del curso dentro del propio archivo Python

Importante:
- Este curso es solo para aprendizaje, defensa, auditoría autorizada,
  CTFs y laboratorios controlados.
- No debe usarse para afectar sistemas, cuentas, redes o datos sin permiso.
"""

from textwrap import dedent
import sys

COURSE_TITLE = "WHITE HAT SECURITY FOUNDATIONS"
COURSE_SUBTITLE = "Curso completo dictado en Python"
ETHICS_NOTICE = """
Este curso está diseñado para:
- formación en seguridad ofensiva ética
- comprensión defensiva de sistemas
- práctica en laboratorios controlados
- desarrollo de criterio profesional

No está diseñado para:
- intrusión no autorizada
- sabotaje
- robo de datos
- evasión de controles
- explotación de terceros sin consentimiento
"""


UNITS = {
    "0": {
        "title": "Unidad 0 - Marco ético, legal y mentalidad profesional",
        "content": dedent("""
        ============================================================
        UNIDAD 0
        MARCO ÉTICO, LEGAL Y MENTALIDAD PROFESIONAL
        ============================================================

        PROPÓSITO DE LA UNIDAD
        Antes de aprender redes, Linux, aplicaciones web o análisis técnico,
        debes entender la frontera que separa al profesional del problema.
        La seguridad no empieza con herramientas. Empieza con criterio.

        OBJETIVOS
        Al terminar esta unidad deberías poder:
        1. Distinguir entre práctica ética y conducta no autorizada.
        2. Explicar por qué el permiso es el eje central de cualquier prueba.
        3. Entender el rol del white hat dentro del ecosistema técnico.
        4. Adoptar una mentalidad de evidencia, límites y responsabilidad.

        1. QUÉ ES UN HACKER DE SOMBRERO BLANCO
        Un hacker de sombrero blanco es una persona que estudia, identifica,
        valida y comunica debilidades de seguridad con autorización, con fines
        de protección, mejora, auditoría o resiliencia.

        El punto no es “romper por romper”.
        El punto es:
        - comprender el sistema
        - detectar exposición
        - demostrar riesgo dentro de límites
        - ayudar a corregirlo

        DIFERENCIA ENTRE ROLES
        - White Hat: actúa con autorización y trazabilidad.
        - Blue Team: protege, detecta, monitorea y responde.
        - Red Team: simula ataques bajo reglas de compromiso.
        - Purple Team: integra ofensiva y defensa.
        - Criminal: actúa sin permiso, sin límites y con daño potencial.

        2. EL PERMISO ES LA LLAVE MAESTRA
        En seguridad, saber hacer algo no te autoriza a hacerlo.
        El permiso transforma una acción técnicamente similar en algo legítimo,
        auditable y profesional.

        Regla de oro:
        Si no tienes autorización explícita, por escrito y con alcance definido,
        no pruebas.

        Elementos mínimos de autorización:
        - quién autoriza
        - qué activos están dentro del alcance
        - qué queda fuera del alcance
        - qué horario o ventana aplica
        - qué tipo de pruebas están permitidas
        - cómo se reportará evidencia
        - quién es el punto de contacto

        3. ALCANCE Y REGLAS DE COMPROMISO
        Un profesional no opera en niebla. Opera con bordes claros.

        Alcance significa:
        - dominios autorizados
        - aplicaciones autorizadas
        - ambientes autorizados
        - cuentas de prueba autorizadas
        - exclusiones críticas

        Ejemplo conceptual de alcance:
        - Permitido: laboratorio.local, app-staging.local
        - No permitido: producción, datos reales, usuarios reales

        4. LA ÉTICA COMO VENTAJA TÉCNICA
        La ética no es un freno. Es una arquitectura de calidad.
        Quien trabaja con límites claros:
        - documenta mejor
        - piensa mejor
        - reduce ruido
        - produce evidencia útil
        - es empleable y confiable

        5. MENTALIDAD PROFESIONAL
        Un principiante suele pensar:
        “¿qué herramienta uso?”

        Un profesional piensa:
        - ¿cuál es el objetivo?
        - ¿qué estoy observando realmente?
        - ¿qué hipótesis tengo?
        - ¿qué evidencia valida o invalida esa hipótesis?
        - ¿qué impacto tendría esto si fuera real?
        - ¿cómo lo comunico sin exagerar?

        6. PRINCIPIOS OPERATIVOS DEL CURSO
        Durante todo el curso vas a operar con estas reglas:

        REGLA 1
        No tocar sistemas ajenos.

        REGLA 2
        Solo practicar en:
        - laboratorios propios
        - máquinas intencionalmente vulnerables
        - CTFs
        - plataformas de formación
        - programas con autorización expresa

        REGLA 3
        No confundir curiosidad con derecho de acceso.

        REGLA 4
        Todo hallazgo debe convertirse en evidencia y explicación.

        REGLA 5
        El objetivo final no es “saber de hacking”.
        Es desarrollar criterio, capacidad técnica y comunicación profesional.

        7. MODELO MENTAL DEL CURSO
        Este curso sigue esta secuencia:

        comprensión -> observación -> hipótesis -> validación en laboratorio
        -> documentación -> mitigación -> reflexión

        8. ERRORES COMUNES DEL ASPIRANTE
        Error 1: obsesionarse con herramientas sin base.
        Error 2: querer correr antes de entender HTTP, Linux y flujo web.
        Error 3: perseguir complejidad en lugar de claridad.
        Error 4: creer que encontrar un fallo vale más que explicarlo.
        Error 5: ignorar el contexto legal.
        Error 6: aprender conceptos sin producir bitácora ni reportes.

        9. HABILIDADES META QUE VAS A DESARROLLAR
        Además de lo técnico, este curso te entrena en:
        - precisión conceptual
        - disciplina de laboratorio
        - razonamiento causal
        - lectura de evidencia
        - documentación clara
        - priorización de riesgo
        - pensamiento sistémico

        10. EJERCICIO DE CIERRE
        Responde por escrito:
        1. ¿Qué convierte una prueba técnica en una prueba legítima?
        2. ¿Por qué el alcance es tan importante como la técnica?
        3. ¿Qué diferencia hay entre hallar algo y demostrarlo?
        4. ¿Por qué un buen reporte vale tanto como un buen hallazgo?

        RESUMEN DE LA UNIDAD
        - El white hat trabaja con permiso, límites y trazabilidad.
        - La ética no es decorado: es infraestructura profesional.
        - La seguridad empieza en la mente, no en la herramienta.
        - El curso entero se apoya en laboratorios autorizados.

        CRITERIO DE DOMINIO
        Dominas esta unidad si ya entiendes que la pregunta central no es:
        “¿puedo hacerlo técnicamente?”
        sino:
        “¿debo hacerlo, tengo autorización y puedo demostrarlo bien?”
        """)
    },
    "1": {
        "title": "Unidad 1 - Fundamentos de redes para seguridad",
        "content": dedent("""
        ============================================================
        UNIDAD 1
        FUNDAMENTOS DE REDES PARA SEGURIDAD
        ============================================================

        PROPÓSITO
        No puedes analizar tráfico, sesiones, aplicaciones web o exposición
        sin entender cómo viaja la información. La red es el escenario.

        OBJETIVOS
        Al terminar esta unidad deberías poder:
        1. Explicar el recorrido básico de una petición en red.
        2. Diferenciar IP, puerto, protocolo, dominio y DNS.
        3. Entender qué hace HTTP dentro de una arquitectura web.
        4. Leer tráfico con criterio conceptual.

        1. QUÉ ES UNA RED
        Una red es un sistema de intercambio de datos entre dispositivos.
        En seguridad, una red no es solo conectividad.
        Es superficie de exposición, flujo de confianza y vector de observación.

        2. CONCEPTOS BÁSICOS
        Host:
        Dispositivo conectado que puede enviar o recibir datos.

        Dirección IP:
        Identificador lógico dentro de una red.

        Puerto:
        Puerta lógica por la que un servicio escucha tráfico.

        Protocolo:
        Conjunto de reglas que define cómo se comunica la información.

        Dominio:
        Nombre legible por humanos que apunta a recursos de red.

        DNS:
        Sistema que traduce nombres de dominio en direcciones utilizables.

        3. MODELO MENTAL SIMPLE DEL TRÁFICO
        Cuando un usuario visita una web, ocurre algo parecido a esto:

        usuario -> navegador -> resolución DNS -> IP del servidor
        -> conexión al servicio -> solicitud HTTP -> respuesta HTTP

        En seguridad, cada punto de esa cadena puede dar señales:
        - resolución extraña
        - cabeceras anómalas
        - redirecciones inesperadas
        - cookies mal gestionadas
        - respuestas excesivamente verbosas

        4. IP Y PUERTOS
        Una IP te dice “dónde”.
        Un puerto te dice “qué servicio probablemente está escuchando”.

        Ejemplos conceptuales comunes:
        - 80: HTTP
        - 443: HTTPS
        - 22: administración remota segura
        - 53: DNS

        Nota profesional:
        Memorizar números ayuda, pero más importante es entender que un puerto
        expuesto es una puerta de conversación. Y toda puerta merece contexto.

        5. TCP Y UDP
        TCP:
        - orientado a conexión
        - busca entrega ordenada y confiable
        - común en navegación web

        UDP:
        - sin conexión persistente
        - menor sobrecarga
        - útil en escenarios donde la velocidad importa más que la confirmación

        Relevancia para seguridad:
        El comportamiento del tráfico cambia según el protocolo.
        Esto afecta observación, diagnóstico y análisis de exposición.

        6. DNS
        DNS funciona como una agenda distribuida.
        El usuario recuerda nombres; la red necesita ubicaciones.

        Preguntas clave que un analista suele hacerse:
        - ¿A qué IP resuelve este dominio?
        - ¿Hay subdominios adicionales?
        - ¿Hay registros que delaten infraestructura?
        - ¿Hay diferencias entre entorno público y entorno interno?

        7. HTTP Y HTTPS
        HTTP:
        Protocolo de aplicación muy usado en la web.

        HTTPS:
        HTTP encapsulado con protección criptográfica durante el transporte.

        Elementos de una solicitud HTTP:
        - método
        - ruta
        - headers
        - cookies
        - cuerpo, si aplica

        Elementos de una respuesta:
        - código de estado
        - headers
        - cuerpo
        - cookies o directivas relacionadas

        8. MÉTODOS HTTP
        GET:
        Solicita un recurso.

        POST:
        Envía datos para procesamiento.

        PUT/PATCH:
        Modifican recursos, según diseño.

        DELETE:
        Solicita eliminación, si el sistema lo permite.

        En seguridad, el método importa porque expresa intención.
        Una operación sensible expuesta con controles débiles suele ser una pista.

        9. CÓDIGOS DE ESTADO
        200:
        La operación parece exitosa.

        301/302:
        Redirección.

        401:
        Falta autenticación o es requerida.

        403:
        Acceso denegado.

        404:
        Recurso no encontrado o escondido.

        500:
        Error del servidor.

        Un analista no ve solo el número.
        Interpreta qué le dice el sistema sobre su propia lógica interna.

        10. HEADERS Y COOKIES
        Headers:
        Metadatos de la comunicación.

        Cookies:
        Fragmentos de estado que ayudan a mantener sesión o personalización.

        Riesgos conceptuales:
        - exposición de información técnica innecesaria
        - políticas débiles de cookies
        - controles de caché inapropiados
        - encabezados de seguridad ausentes

        11. SESIÓN Y ESTADO
        La web moderna simula continuidad en un entorno naturalmente stateless.
        Por eso existen sesiones, tokens y cookies.

        Seguridad aquí significa:
        - identificar al usuario correctamente
        - mantener contexto sin exponerlo
        - invalidar estado cuando corresponde
        - evitar mezcla entre identidad y autorización

        12. ARQUITECTURA WEB EN MINIATURA
        El navegador no habla “directamente con la base de datos”.
        Generalmente hay capas:

        cliente -> frontend -> backend -> base de datos
                       |            |
                       |            -> lógica de negocio
                       -> recursos visuales

        En seguridad, romper una suposición en una capa puede revelar debilidades
        en otra.

        13. QUÉ OBSERVAR EN LABORATORIO
        En un laboratorio autorizado debes aprender a mirar:
        - nombres de host
        - rutas
        - parámetros
        - cabeceras
        - cookies
        - redirecciones
        - diferencias entre usuario autenticado y no autenticado

        14. ERRORES DE APRENDIZAJE
        Error 1:
        Pensar que redes es memorizar definiciones.

        Error 2:
        Separar demasiado redes y aplicaciones web.

        Error 3:
        No practicar lectura de tráfico real en entorno controlado.

        15. EJERCICIO DE CIERRE
        Explica con tus palabras:
        - qué hace DNS
        - qué relación hay entre IP y puerto
        - cómo una solicitud HTTP llega a una aplicación
        - por qué cookies y sesiones importan en seguridad

        RESUMEN
        - La red es el escenario de observación.
        - DNS, IP, puertos y HTTP son la gramática básica del entorno.
        - Leer tráfico es leer conducta del sistema.
        - Sin esta base, la seguridad se vuelve superstición.

        CRITERIO DE DOMINIO
        Dominas esta unidad si puedes reconstruir mentalmente el viaje de una
        solicitud desde el navegador hasta la aplicación y explicar dónde se
        esconden señales relevantes para seguridad.
        """)
    },
    "2": {
        "title": "Unidad 2 - Linux como entorno natural del analista",
        "content": dedent("""
        ============================================================
        UNIDAD 2
        LINUX COMO ENTORNO NATURAL DEL ANALISTA
        ============================================================

        PROPÓSITO
        Linux no es un fetiche técnico. Es una ventaja operativa.
        Te obliga a ver el sistema de forma más clara y te acerca al comportamiento
        real de muchos servidores, contenedores y entornos de laboratorio.

        OBJETIVOS
        1. Entender estructura básica del sistema de archivos.
        2. Manejar navegación, lectura y edición simple.
        3. Comprender permisos, procesos y servicios.
        4. Adoptar higiene operativa mínima en consola.

        1. POR QUÉ LINUX IMPORTA
        En seguridad, Linux importa porque:
        - muchos entornos de laboratorio lo usan
        - gran parte de la infraestructura moderna corre sobre Linux
        - la consola te fuerza a pensar con precisión
        - reduce magia visual y aumenta trazabilidad

        2. ESTRUCTURA BÁSICA DEL SISTEMA
        Ideas clave:
        - todo tiene ubicación
        - todo tiene permisos
        - mucho se representa como archivo
        - los procesos son entidades observables

        Directorios conceptuales:
        /home     espacio de usuario
        /etc      configuración
        /var      datos variables y logs
        /tmp      archivos temporales
        /bin y /usr/bin   ejecutables comunes

        No necesitas venerar el árbol.
        Necesitas orientarte dentro de él.

        3. NAVEGACIÓN
        Acciones fundamentales:
        - saber dónde estás
        - ver qué hay
        - moverte
        - abrir archivos
        - buscar contenido

        Competencia mínima:
        - ubicarte
        - listar
        - leer
        - crear
        - copiar
        - mover
        - borrar con criterio

        4. PERMISOS
        Cada archivo o directorio tiene reglas de acceso.
        Esto afecta:
        - lectura
        - escritura
        - ejecución

        En seguridad, los permisos importan porque:
        - revelan diseño de confianza
        - limitan o amplían impacto
        - explican por qué algo falla o por qué algo es riesgoso

        Preguntas útiles:
        - ¿quién es propietario?
        - ¿quién puede leer?
        - ¿quién puede modificar?
        - ¿quién puede ejecutar?

        5. USUARIO Y PRIVILEGIO
        No todo proceso corre con el mismo nivel de capacidad.
        El principio de mínimo privilegio existe para contener daño.

        Mentalidad sana:
        - no operar siempre con privilegio alto
        - elevar solo cuando corresponde
        - dejar rastro mental de lo que cambias

        6. PROCESOS
        Un proceso es un programa en ejecución.
        En Linux importa observar:
        - qué corre
        - con qué usuario
        - qué puertos usa
        - si corresponde con lo esperado

        En seguridad defensiva esto ayuda a detectar:
        - servicios innecesarios
        - comportamientos anómalos
        - exposición no prevista

        7. LOGS
        Los logs son la memoria parcial del sistema.
        No son la verdad absoluta, pero sí una narrativa valiosa.

        Aprender seguridad sin logs es como investigar con los ojos vendados.

        8. VARIABLES DE ENTORNO
        Muchas aplicaciones dependen de configuración del entorno.
        Estas variables pueden afectar:
        - rutas
        - credenciales de prueba
        - comportamiento de aplicaciones
        - contexto de ejecución

        Relevancia:
        una mala gestión de configuración produce riesgo.

        9. RED Y SERVICIOS DESDE LINUX
        En Linux puedes observar:
        - interfaces
        - rutas
        - procesos escuchando
        - resoluciones
        - conectividad

        El objetivo pedagógico no es volverte adicto a comandos.
        Es entender que el sistema habla, y la consola te deja escucharlo.

        10. HIGIENE OPERATIVA
        Buenas prácticas:
        - documentar lo que haces
        - no ejecutar cosas que no entiendes
        - no copiar y pegar a ciegas
        - usar entornos de prueba
        - diferenciar claramente laboratorio y producción

        11. BITÁCORA DE LABORATORIO
        A partir de esta unidad, toda práctica debe registrar:
        - fecha
        - objetivo
        - entorno
        - observaciones
        - hipótesis
        - resultado
        - dudas
        - próxima acción

        Esta disciplina te convierte en operador serio.

        12. EJERCICIO DE CIERRE
        Redacta:
        - por qué Linux aporta claridad operativa
        - qué papel tienen los permisos
        - por qué un log bien leído vale tanto
        - qué significa trabajar con mínimo privilegio

        RESUMEN
        - Linux es un entorno de observación y control.
        - Permisos, procesos y logs son piezas centrales.
        - La consola enseña precisión.
        - La bitácora importa tanto como la práctica.

        CRITERIO DE DOMINIO
        Dominas esta unidad si ya puedes explicar cómo se organiza un sistema
        Linux, por qué los permisos son críticos y por qué un profesional no
        toca nada sin dejar una línea mental de causalidad.
        """)
    },
    "3": {
        "title": "Unidad 3 - Fundamentos de aplicaciones web",
        "content": dedent("""
        ============================================================
        UNIDAD 3
        FUNDAMENTOS DE APLICACIONES WEB
        ============================================================

        PROPÓSITO
        La mayor parte del trabajo de entrada en seguridad ofensiva ética gira
        alrededor de aplicaciones web. Si entiendes cómo viven, respiran y
        confían, empiezas a ver debilidades con más nitidez.

        OBJETIVOS
        1. Comprender la arquitectura básica de una app web.
        2. Diferenciar frontend, backend y base de datos.
        3. Entender rutas, parámetros, formularios y sesión.
        4. Leer una aplicación como sistema, no solo como interfaz.

        1. QUÉ ES UNA APLICACIÓN WEB
        Es un sistema accesible mediante navegador u otros clientes HTTP,
        compuesto por varias capas que colaboran para prestar una función.

        Un error común del principiante es mirar solo la pantalla.
        El analista mira:
        - entradas
        - salidas
        - decisiones
        - identidad
        - autorización
        - persistencia

        2. FRONTEND
        Es la capa visible para el usuario.
        Suele incluir:
        - estructura
        - estilo
        - interacción
        - consumo de recursos del backend

        Seguridad:
        Nunca asumas que lo que ves agota lo que existe.
        La interfaz es una representación, no la totalidad del sistema.

        3. BACKEND
        Es la lógica del servidor.
        Allí suelen vivir:
        - validaciones
        - reglas de negocio
        - autenticación
        - autorización
        - acceso a datos

        Mucha seguridad real depende del backend, no del maquillaje visual.

        4. BASE DE DATOS
        Allí persisten estados, usuarios, contenido, relaciones y operaciones.

        Conceptualmente, el riesgo aparece cuando:
        - la app acepta entradas sin control adecuado
        - mezcla identidad y privilegio
        - expone información más allá de lo necesario
        - aplica reglas de negocio de forma inconsistente

        5. RUTAS Y RECURSOS
        Una aplicación suele exponer rutas:
        /login
        /profile
        /orders
        /api/user/123

        Cada ruta expresa una capacidad o un recurso.
        En seguridad debes preguntarte:
        - ¿quién puede verla?
        - ¿quién puede usarla?
        - ¿qué espera recibir?
        - ¿qué devuelve?
        - ¿qué pasa si cambia el contexto de usuario?

        6. PARÁMETROS
        Los parámetros son piezas de entrada.
        Pueden viajar:
        - en la URL
        - en formularios
        - en el cuerpo de la solicitud
        - en headers
        - en cookies o tokens

        El analista aprende a no ver “campos”.
        Ve vectores de decisión.

        7. FORMULARIOS
        Un formulario no es solo una caja para escribir.
        Es un contrato parcial entre usuario y sistema.

        Preguntas clave:
        - ¿qué valida el cliente?
        - ¿qué valida el servidor?
        - ¿qué pasa si una entrada cambia?
        - ¿hay campos ocultos?
        - ¿hay datos sensibles enviados sin necesidad?

        8. AUTENTICACIÓN
        Responde a:
        “¿Quién eres?”

        9. AUTORIZACIÓN
        Responde a:
        “¿Qué puedes hacer?”

        Este par es crucial.
        Muchísimos errores nacen cuando el sistema identifica a alguien pero
        no decide correctamente qué le corresponde ver o modificar.

        10. SESIÓN
        La sesión mantiene continuidad.
        Aquí importan:
        - creación
        - persistencia
        - expiración
        - invalidación
        - relación con privilegios

        11. APIs
        Muchas apps modernas exponen APIs.
        Una API es otra interfaz, a menudo más honesta que la web visual.

        Para seguridad conceptual, una API revela:
        - estructura de recursos
        - operaciones disponibles
        - convenciones de acceso
        - supuestos del sistema

        12. LÓGICA DE NEGOCIO
        No toda debilidad nace de un fallo “técnico clásico”.
        Muchas nacen de reglas de negocio mal pensadas.

        Ejemplos conceptuales:
        - descuentos acumulables cuando no deberían
        - acciones permitidas fuera de secuencia
        - acceso a objetos por identificador sin verificación consistente
        - procesos aprobados sin cumplir precondiciones

        13. DIFERENCIA ENTRE VALIDAR Y CONFIAR
        Una app madura valida porque desconfía.
        Una app frágil confía porque espera buena conducta.

        La seguridad vive donde el sistema deja de suponer y empieza a comprobar.

        14. QUÉ DEBES APRENDER A OBSERVAR
        - cómo navega un usuario anónimo
        - qué cambia al autenticarte
        - qué recursos aparecen
        - qué rutas usan identificadores
        - qué acciones modifican estado
        - qué mensajes de error revelan demasiado
        - qué datos viajan aunque no los veas en pantalla

        15. EJERCICIO DE CIERRE
        Explica:
        - la diferencia entre frontend y backend
        - por qué autenticación y autorización no son lo mismo
        - cómo una ruta puede convertirse en punto de control
        - por qué la lógica de negocio importa tanto como un bug clásico

        RESUMEN
        - Una app web es un sistema por capas.
        - La interfaz visible es solo una sombra parcial del sistema real.
        - Seguridad significa observar entradas, decisiones y controles.
        - La lógica de negocio puede ser tan crítica como la técnica.

        CRITERIO DE DOMINIO
        Dominas esta unidad si ya no ves una web como “pantallas”, sino como
        un conjunto de rutas, decisiones, estados, privilegios y supuestos.
        """)
    },
    "4": {
        "title": "Unidad 4 - Metodología de observación y análisis",
        "content": dedent("""
        ============================================================
        UNIDAD 4
        METODOLOGÍA DE OBSERVACIÓN Y ANÁLISIS
        ============================================================

        PROPÓSITO
        Antes de hablar de familias de fallos, necesitas método.
        Sin método, el análisis se vuelve intuición desordenada.

        OBJETIVOS
        1. Adoptar una secuencia clara de observación.
        2. Formular hipótesis útiles.
        3. Distinguir evidencia de impresión.
        4. Construir hábito de validación.

        1. EL MODELO BASE
        Este curso usa una secuencia sencilla y poderosa:

        observar -> describir -> formular hipótesis -> validar en laboratorio
        -> registrar evidencia -> interpretar -> proponer mitigación

        2. OBSERVAR
        Observar no es mirar por encima.
        Es registrar con atención:
        - entradas
        - respuestas
        - cambios de estado
        - diferencias entre contextos
        - mensajes del sistema

        3. DESCRIBIR
        La descripción debe ser limpia.
        Ejemplo sano:
        “Al cambiar el contexto de usuario en el laboratorio, la respuesta
        siguió devolviendo el recurso.”

        Ejemplo débil:
        “Se ve raro.”

        4. HIPÓTESIS
        Una hipótesis no es una certeza.
        Es una explicación tentativa que guiará pruebas controladas.

        Ejemplo conceptual:
        “El sistema podría no estar verificando correctamente si el recurso
        solicitado pertenece al usuario autenticado.”

        5. VALIDACIÓN
        Validar es intentar refutar o confirmar con cuidado.
        No es forzar una narrativa.

        La validación debe:
        - respetar el alcance
        - ser mínima y suficiente
        - no causar daño
        - dejar evidencia

        6. EVIDENCIA
        La evidencia en seguridad puede incluir:
        - notas reproducibles
        - capturas de entorno de laboratorio
        - diferencias de respuestas
        - líneas temporales
        - registros del flujo ejecutado

        Regla:
        si no puedes reconstruir lo que pasó, aprendiste menos de lo que crees.

        7. INTERPRETACIÓN
        Hallar una diferencia no basta.
        Debes preguntarte:
        - ¿qué significa realmente?
        - ¿es un control ausente o una decisión legítima?
        - ¿qué impacto tendría en un entorno equivalente?
        - ¿qué condiciones son necesarias para que importe?

        8. MITIGACIÓN
        El profesional no termina en el hallazgo.
        También piensa:
        - qué control faltó
        - dónde debería vivir el control
        - cómo reducir riesgo
        - cómo verificar la corrección

        9. ERRORES DE MÉTODO
        - enamorarte de la primera teoría
        - confundir respuesta diferente con vulnerabilidad
        - no aislar variables
        - no registrar contexto
        - exagerar impacto sin sostén

        10. BITÁCORA PROFESIONAL
        Toda práctica debería anotar:
        - objetivo
        - entorno
        - hipótesis
        - pasos observados
        - evidencia
        - conclusión
        - mitigación sugerida

        11. EJERCICIO DE CIERRE
        Describe una observación cotidiana tecnológica usando este esquema:
        observación -> hipótesis -> validación -> evidencia -> interpretación

        RESUMEN
        - La metodología te salva del caos.
        - Observar no es lo mismo que interpretar.
        - La evidencia disciplina el pensamiento.
        - Un hallazgo sin buena explicación pierde valor.

        CRITERIO DE DOMINIO
        Dominas esta unidad si ya puedes analizar algo sin saltar
        inmediatamente a conclusiones ruidosas.
        """)
    },
    "5": {
        "title": "Unidad 5 - Familias de debilidades: autenticación, autorización, entrada y estado",
        "content": dedent("""
        ============================================================
        UNIDAD 5
        FAMILIAS DE DEBILIDADES
        AUTENTICACIÓN, AUTORIZACIÓN, ENTRADA Y ESTADO
        ============================================================

        PROPÓSITO
        Esta unidad no te enseña “trucos”.
        Te enseña a clasificar debilidades por familia para pensar con orden.

        OBJETIVOS
        1. Reconocer grandes categorías de fallos comunes.
        2. Entender qué pregunta hace cada familia.
        3. Diferenciar síntomas de causas.
        4. Prepararte para análisis responsable en laboratorio.

        1. DEBILIDADES DE AUTENTICACIÓN
        Pregunta central:
        ¿El sistema identifica correctamente a quien intenta entrar?

        Riesgos conceptuales:
        - políticas débiles de credenciales
        - recuperación de cuenta mal diseñada
        - manejo inseguro de sesión
        - persistencia excesiva
        - separación deficiente entre inicio, cierre y renovación de sesión

        Señales de observación:
        - mensajes demasiado informativos
        - sesiones que no expiran correctamente
        - cambios de contexto sin invalidación adecuada
        - flujos de recuperación frágiles

        2. DEBILIDADES DE AUTORIZACIÓN
        Pregunta central:
        ¿El sistema decide correctamente qué puede hacer cada identidad?

        Esta es una de las familias más importantes.
        Puedes estar bien autenticado y aun así mal autorizado.

        Riesgos conceptuales:
        - acceso a recursos ajenos
        - operaciones permitidas a roles incorrectos
        - controles solo del lado cliente
        - uso de identificadores sin verificación suficiente

        Observación profesional:
        cuando una ruta depende de un identificador, debes preguntarte
        quién valida la pertenencia y dónde vive esa decisión.

        3. DEBILIDADES DE ENTRADA
        Pregunta central:
        ¿Qué hace el sistema con los datos que recibe?

        Riesgos conceptuales:
        - confiar en entradas sin validarlas
        - transformar datos sin contexto seguro
        - reflejar contenido de forma insegura
        - construir operaciones sensibles a partir de entrada no controlada

        La clave aquí no es memorizar nombres.
        Es entender que toda entrada es una negociación de confianza.

        4. DEBILIDADES DE ESTADO
        Pregunta central:
        ¿Cómo mantiene la app continuidad y contexto?

        Riesgos conceptuales:
        - mezcla incorrecta entre identidad y estado
        - sesiones revivibles
        - tokens mal gestionados
        - acciones sensibles sin ataduras suficientes al contexto legítimo

        5. DEBILIDADES DE CONFIGURACIÓN
        Pregunta central:
        ¿La infraestructura y la aplicación están expuestas más de lo necesario?

        Riesgos conceptuales:
        - mensajes de error demasiado verbosos
        - encabezados ausentes
        - componentes innecesarios
        - datos de entorno expuestos
        - controles por defecto no endurecidos

        6. DEBILIDADES DE LÓGICA DE NEGOCIO
        Pregunta central:
        ¿El sistema hace algo que conceptualmente no debería permitir?

        Esta familia es crucial porque a veces no rompe una regla técnica
        evidente. Rompe una regla de negocio.

        7. VISIÓN SISTÉMICA
        Un error profesional común es estudiar estos temas como islas.
        En realidad interactúan:
        - una entrada mal validada puede afectar estado
        - una sesión débil puede agravar autorización
        - una lógica rota puede amplificar exposición de datos

        8. CÓMO PENSAR UNA FAMILIA DE FALLOS
        Para cada familia pregúntate:
        - ¿qué intenta proteger el sistema?
        - ¿dónde confía?
        - ¿qué asume?
        - ¿qué pasa si esa asunción falla?
        - ¿qué evidencia mostraría esa falla?

        9. EJERCICIO DE CIERRE
        Elige una familia y redacta:
        - su pregunta central
        - sus riesgos conceptuales
        - sus señales de observación
        - un ejemplo abstracto de mitigación

        RESUMEN
        - Las familias de fallos ordenan tu mente.
        - Autenticación y autorización no son equivalentes.
        - Entrada, estado, configuración y lógica interactúan.
        - Clasificar bien es pensar mejor.

        CRITERIO DE DOMINIO
        Dominas esta unidad si puedes mirar una app y ubicar un problema
        potencial dentro de una familia, sin caer en etiquetas vacías.
        """)
    },
    "6": {
        "title": "Unidad 6 - Gestión de sesión, identidad y confianza",
        "content": dedent("""
        ============================================================
        UNIDAD 6
        GESTIÓN DE SESIÓN, IDENTIDAD Y CONFIANZA
        ============================================================

        PROPÓSITO
        La mayoría de aplicaciones modernas viven de una ilusión controlada:
        hacer parecer continuo un entorno que naturalmente no lo es.
        Esa ilusión se llama sesión, y es una mina de aprendizaje.

        OBJETIVOS
        1. Comprender cómo una app sostiene identidad.
        2. Distinguir autenticación, sesión y autorización.
        3. Entender por qué el estado es delicado.
        4. Aprender a razonar sobre confianza distribuida.

        1. IDENTIDAD
        Identidad responde a:
        “¿Quién es este actor dentro del sistema?”

        Puede basarse en:
        - credenciales
        - tokens
        - cookies
        - federación
        - contexto adicional

        2. SESIÓN
        La sesión es la continuidad operativa asociada a una identidad o flujo.

        Buenas preguntas:
        - ¿cuándo nace?
        - ¿cuándo cambia?
        - ¿cuándo termina?
        - ¿qué la invalida?
        - ¿depende de privilegios o los hereda de forma laxa?

        3. CONTEXTO
        Una solicitud aislada dice poco.
        El contexto dice más:
        - usuario autenticado
        - rol
        - alcance funcional
        - operación actual
        - recursos relacionados

        4. CONFIANZA
        Toda app reparte confianza entre piezas:
        - navegador
        - servidor
        - base de datos
        - servicios externos
        - tokens
        - cookies
        - cabeceras

        El analista aprende a detectar dónde el sistema confía demasiado.

        5. PRINCIPIOS DEFENSIVOS
        - validar del lado servidor
        - caducar correctamente
        - invalidar al cerrar o cambiar contexto sensible
        - vincular privilegio a controles explícitos
        - minimizar exposición de estado

        6. MALAS SUPOSICIONES COMUNES
        - “si el usuario inició sesión, todo lo que pide es legítimo”
        - “si la interfaz no muestra algo, no existe”
        - “si un identificador viene del cliente, debe ser correcto”
        - “si un token existe, ya basta”

        7. EJERCICIO DE CIERRE
        Explica cómo distinguir:
        - identidad
        - autenticación
        - sesión
        - autorización

        RESUMEN
        - La confianza mal distribuida produce debilidad.
        - La sesión es una infraestructura delicada.
        - La identidad sin buena autorización es insuficiente.
        - Pensar estado es pensar riesgo.

        CRITERIO DE DOMINIO
        Dominas esta unidad si ya puedes mapear cómo una app sostiene
        continuidad e imaginar dónde podría romperse la confianza.
        """)
    },
    "7": {
        "title": "Unidad 7 - Superficie de ataque y cartografía del sistema",
        "content": dedent("""
        ============================================================
        UNIDAD 7
        SUPERFICIE DE ATAQUE Y CARTOGRAFÍA DEL SISTEMA
        ============================================================

        PROPÓSITO
        Antes de analizar profundidad, debes entender extensión.
        La cartografía del sistema te enseña dónde mirar.

        OBJETIVOS
        1. Entender qué es superficie de ataque.
        2. Aprender a mapear activos en laboratorio.
        3. Reconocer puntos de entrada, exposición y decisión.
        4. Construir visión estructurada del entorno.

        1. DEFINICIÓN
        La superficie de ataque es el conjunto de puntos por los cuales
        un sistema recibe, procesa o expone información o capacidades.

        2. NO ES SOLO “LO QUE SE VE”
        Superficie incluye:
        - rutas visibles
        - APIs
        - formularios
        - recursos cargados en segundo plano
        - dependencias externas
        - paneles de administración
        - comportamientos por rol
        - flujos alternos

        3. CARTOGRAFÍA
        Cartografiar es construir un mapa mental y documental de:
        - qué existe
        - cómo se conecta
        - qué recibe
        - qué devuelve
        - qué depende de identidad
        - qué cambia según el contexto

        4. PREGUNTAS MAESTRAS
        - ¿qué entradas tiene el sistema?
        - ¿qué salidas produce?
        - ¿qué recursos parecen sensibles?
        - ¿qué acciones mutan estado?
        - ¿qué depende de roles?
        - ¿qué endpoints usan identificadores?
        - ¿qué elementos existen aunque no estén en la UI principal?

        5. CAPAS DE MAPEO
        Capa 1: descubrimiento funcional
        Capa 2: descubrimiento de roles
        Capa 3: descubrimiento de estados
        Capa 4: descubrimiento de reglas de negocio
        Capa 5: descubrimiento de confianza entre componentes

        6. ERRORES DE CARTOGRAFÍA
        - mirar solo la interfaz bonita
        - no comparar usuarios
        - ignorar recursos auxiliares
        - no anotar rutas y parámetros
        - perder continuidad de observación

        7. SALIDA ESPERADA
        Un mapa útil no es una lista caótica.
        Es una estructura que te deja decir:
        - aquí entra dato
        - aquí cambia estado
        - aquí se decide acceso
        - aquí podría faltar un control

        8. EJERCICIO DE CIERRE
        Diseña una plantilla de mapeo con:
        - recurso
        - método o acción
        - parámetros
        - rol esperado
        - cambio de estado
        - observaciones

        RESUMEN
        - Mapear es pensar antes de probar.
        - La superficie incluye más que pantallas.
        - La comparación entre contextos es oro.
        - Sin mapa, toda prueba es más ciega.

        CRITERIO DE DOMINIO
        Dominas esta unidad si puedes convertir una aplicación en un mapa
        razonado de rutas, recursos, estados y decisiones.
        """)
    },
    "8": {
        "title": "Unidad 8 - Documentación de hallazgos y escritura profesional",
        "content": dedent("""
        ============================================================
        UNIDAD 8
        DOCUMENTACIÓN DE HALLAZGOS Y ESCRITURA PROFESIONAL
        ============================================================

        PROPÓSITO
        Un hallazgo sin documentación sólida es una chispa sin oxígeno.
        La escritura profesional convierte observación en valor.

        OBJETIVOS
        1. Aprender estructura básica de un reporte.
        2. Redactar con claridad, precisión y prudencia.
        3. Diferenciar evidencia, interpretación e impacto.
        4. Proponer mitigaciones realistas.

        1. EL REPORTE COMO PRODUCTO
        No reportas para lucirte.
        Reportas para que otro entienda, reproduzca, priorice y corrija.

        2. ESTRUCTURA BASE DE UN REPORTE
        - título
        - resumen
        - entorno o contexto
        - descripción
        - evidencia
        - impacto razonado
        - condiciones
        - mitigación sugerida
        - notas de validación

        3. TÍTULO
        Debe ser descriptivo, no dramático.
        Malo:
        “Falla gravísima que destruye todo”
        Mejor:
        “Exposición de acceso a recurso por control de autorización insuficiente
        en entorno de laboratorio”

        4. RESUMEN
        Dos o tres líneas que digan:
        - qué observaste
        - por qué importa
        - bajo qué condiciones

        5. DESCRIPCIÓN
        Explica el comportamiento con precisión.
        Evita adornos y soberbia.

        6. EVIDENCIA
        La evidencia debe sostener lo dicho.
        No mezcles observación con interpretación en la misma frase sin marcarlo.

        7. IMPACTO
        El impacto debe ser razonado.
        No es:
        “esto permite todo”
        sino:
        “si este patrón existiera en un entorno sensible con recursos asociados a
        múltiples usuarios, podría derivar en acceso indebido a información o
        modificación no autorizada, dependiendo de los controles compensatorios”

        8. MITIGACIÓN
        La mitigación madura:
        - ubica el control correcto
        - evita vaguedad
        - propone verificación posterior

        9. TONO PROFESIONAL
        - sobrio
        - verificable
        - no inflado
        - no acusatorio
        - centrado en el sistema, no en la humillación del equipo

        10. EJERCICIO DE CIERRE
        Escribe un mini reporte con:
        - título
        - resumen
        - evidencia
        - impacto razonado
        - mitigación

        RESUMEN
        - La documentación es parte del trabajo técnico.
        - El reporte traduce observación en decisión.
        - La precisión vence al drama.
        - Mitigar también es pensar bien.

        CRITERIO DE DOMINIO
        Dominas esta unidad si puedes redactar un hallazgo de forma útil para
        ingeniería, seguridad y negocio.
        """)
    },
    "9": {
        "title": "Unidad 9 - Prioridad, riesgo e impacto",
        "content": dedent("""
        ============================================================
        UNIDAD 9
        PRIORIDAD, RIESGO E IMPACTO
        ============================================================

        PROPÓSITO
        No todo hallazgo vale igual. Aprender seguridad también es aprender
        criterio de prioridad.

        OBJETIVOS
        1. Diferenciar severidad técnica e impacto contextual.
        2. Pensar en probabilidad, exposición y consecuencias.
        3. Evitar exageraciones.
        4. Comunicar prioridades con madurez.

        1. SEVERIDAD VS CONTEXTO
        Una debilidad puede ser técnicamente interesante y operacionalmente menor.
        O al revés.

        2. IMPACTO
        Preguntas útiles:
        - ¿qué recurso afecta?
        - ¿qué actor podría aprovecharlo?
        - ¿qué condiciones necesita?
        - ¿qué datos o funciones toca?
        - ¿hay controles compensatorios?

        3. PROBABILIDAD
        No todo lo posible es probable.
        La madurez está en distinguir:
        - hipótesis remota
        - riesgo plausible
        - exposición recurrente

        4. FACTORES DE PRIORIZACIÓN
        - criticidad del activo
        - facilidad de explotación en el contexto
        - alcance del efecto
        - detectabilidad
        - existencia de controles compensatorios
        - sensibilidad del dato o función

        5. NO SOBREVENDER
        El principiante infla.
        El profesional calibra.

        6. EJERCICIO DE CIERRE
        Toma un hallazgo abstracto y redacta:
        - severidad técnica
        - impacto contextual
        - factores que aumentan o reducen prioridad

        RESUMEN
        - Riesgo es técnica más contexto.
        - Impacto sin condiciones claras es ruido.
        - Priorizar es una habilidad de negocio y seguridad.
        - La calibración construye confianza.

        CRITERIO DE DOMINIO
        Dominas esta unidad si puedes hablar de riesgo sin convertir cada
        hallazgo en apocalipsis.
        """)
    },
    "10": {
        "title": "Unidad 10 - Automatización segura, disciplina y pipeline personal",
        "content": dedent("""
        ============================================================
        UNIDAD 10
        AUTOMATIZACIÓN SEGURA, DISCIPLINA Y PIPELINE PERSONAL
        ============================================================

        PROPÓSITO
        Tu ventaja real no está en hacer más ruido.
        Está en sistematizar observación, estudio y documentación.

        OBJETIVOS
        1. Entender qué sí automatizar.
        2. No usar automatización como reemplazo de criterio.
        3. Diseñar pipeline personal de aprendizaje.
        4. Medir progreso real.

        1. AUTOMATIZAR NO ES PENSAR MENOS
        Automatizar bien significa liberar tiempo para pensar mejor.

        Puedes automatizar de forma segura:
        - tus notas
        - tus plantillas
        - tu bitácora
        - tu inventario de observaciones
        - tu seguimiento de laboratorios
        - tu matriz de familias de fallos
        - tu checklist de revisión

        2. QUÉ NO DEBES CONFUNDIR
        Escanear no es entender.
        Enumerar no es demostrar.
        Hallar un patrón no es probar un impacto.

        3. TU PIPELINE PERSONAL
        Modelo sugerido:
        - estudiar concepto
        - observar laboratorio
        - mapear flujo
        - formular hipótesis
        - validar con prudencia en entorno autorizado
        - documentar
        - reflexionar
        - registrar lección

        4. MÉTRICAS ÚTILES
        - unidades estudiadas y explicadas con tus palabras
        - laboratorios cerrados
        - reportes redactados
        - errores de análisis corregidos
        - tiempo promedio de documentación
        - calidad de tus hipótesis

        5. DISCIPLINA
        La disciplina en seguridad vale más que el entusiasmo esporádico.

        6. EJERCICIO DE CIERRE
        Diseña tu tablero personal con:
        - concepto
        - laboratorio
        - observación
        - hipótesis
        - evidencia
        - reporte
        - lección aprendida

        RESUMEN
        - La automatización debe servir al criterio.
        - Tu pipeline personal te convierte en operador.
        - Medir progreso evita autoengaño.
        - La disciplina produce compuestos silenciosos.

        CRITERIO DE DOMINIO
        Dominas esta unidad si ya puedes diseñar tu propio sistema de estudio
        y validación sin depender del impulso del día.
        """)
    },
    "11": {
        "title": "Unidad 11 - Ruta de profesionalización y próximos pasos",
        "content": dedent("""
        ============================================================
        UNIDAD 11
        RUTA DE PROFESIONALIZACIÓN Y PRÓXIMOS PASOS
        ============================================================

        PROPÓSITO
        El curso no termina en “ya aprendí”.
        Termina cuando entiendes cómo convertir estudio en capacidad profesional.

        OBJETIVOS
        1. Visualizar rutas realistas de crecimiento.
        2. Entender cómo construir portafolio ético.
        3. Preparar práctica constante en entornos correctos.
        4. Consolidar identidad profesional.

        1. RUTAS POSIBLES
        - analista de seguridad junior
        - soporte de AppSec
        - QA con foco en seguridad
        - blue team con sensibilidad ofensiva
        - bug bounty ético en programas autorizados
        - red team, con maduración posterior
        - security architect, a largo plazo

        2. TU PORTAFOLIO
        Un portafolio serio puede incluir:
        - bitácoras de laboratorio
        - mapas de apps de práctica
        - mini reportes técnicos
        - reflexiones sobre mitigación
        - automatizaciones internas de estudio
        - aprendizaje documentado

        3. ENTORNOS DE PRÁCTICA
        Practica solo en:
        - laboratorios locales
        - plataformas formativas
        - máquinas de práctica
        - entornos explícitamente autorizados

        4. PERFIL PROFESIONAL
        Un buen perfil no es:
        “rompo todo”
        sino:
        “entiendo sistemas, detecto debilidades, documento bien y trabajo con ética”

        5. PLAN DE 90 DÍAS
        Mes 1:
        - bases de red, Linux, web y método

        Mes 2:
        - familias de fallos, cartografía y documentación

        Mes 3:
        - práctica intensiva en laboratorio, reportes y pipeline personal

        6. EJERCICIO DE CIERRE
        Redacta tu manifiesto profesional en 10 líneas:
        - qué quieres ser
        - cómo vas a practicar
        - qué límites no cruzas
        - qué ventaja quieres construir

        RESUMEN
        - La profesionalización exige continuidad.
        - El portafolio nace de evidencia, no de postureo.
        - La ética aumenta tu valor de mercado.
        - Tu ruta depende de constancia y criterio.

        CRITERIO DE DOMINIO
        Dominas esta unidad si ya puedes describir un plan de crecimiento
        profesional sin fantasía ni humo.
        """)
    },
    "12": {
        "title": "Unidad 12 - Proyecto integrador final",
        "content": dedent("""
        ============================================================
        UNIDAD 12
        PROYECTO INTEGRADOR FINAL
        ============================================================

        PROPÓSITO
        Cerrar el curso integrando observación, método, documentación y criterio.

        OBJETIVO
        Diseñar y ejecutar un ejercicio de análisis completo en un laboratorio
        autorizado o plataforma educativa.

        ESTRUCTURA DEL PROYECTO
        1. Definir entorno
        2. Delimitar alcance
        3. Cartografiar recursos
        4. Identificar familias de debilidad potencial
        5. Formular hipótesis
        6. Validar con prudencia
        7. Registrar evidencia
        8. Redactar hallazgo o conclusión negativa
        9. Priorizar riesgo
        10. Proponer mitigación
        11. Reflexionar sobre errores y lecciones

        ENTREGA FINAL
        Debe incluir:
        - objetivo
        - entorno autorizado
        - mapa funcional
        - bitácora
        - una o más hipótesis
        - evidencia
        - mini reporte
        - priorización
        - mitigación
        - retrospectiva

        QUÉ EVALÚA ESTE PROYECTO
        - claridad de observación
        - limpieza metodológica
        - pridencia técnica
        - calidad documental
        - calibración de impacto
        - madurez ética

        CIERRE GENERAL DEL CURSO
        Si llegaste aquí con honestidad, ya no eres solo alguien curioso.
        Eres alguien que empieza a pensar como profesional:
        con método, con límites, con evidencia y con responsabilidad.

        TESIS FINAL DEL CURSO
        La seguridad ética no consiste en tocar más cosas.
        Consiste en entender mejor los sistemas, demostrar con rigor,
        comunicar con precisión y fortalecer donde antes había fragilidad.
        """)
    }
}


def print_header():
    print("=" * 68)
    print(COURSE_TITLE.center(68))
    print(COURSE_SUBTITLE.center(68))
    print("=" * 68)
    print(dedent(ETHICS_NOTICE).strip())
    print("=" * 68)


def list_units():
    print("\nUNIDADES DISPONIBLES\n")
    for key in sorted(UNITS.keys(), key=lambda x: int(x)):
        print(f"[{key}] {UNITS[key]['title']}")
    print("[A] Ver todo el curso")
    print("[Q] Salir")


def show_unit(unit_key: str):
    unit = UNITS.get(unit_key)
    if not unit:
        print("Unidad no encontrada.")
        return
    print("\n" + unit["content"])


def show_all():
    for key in sorted(UNITS.keys(), key=lambda x: int(x)):
        print("\n" + "#" * 68)
        print(UNITS[key]["title"])
        print("#" * 68 + "\n")
        print(UNITS[key]["content"])


def main():
    print_header()

    while True:
        list_units()
        choice = input("\nSelecciona una opción: ").strip().upper()

        if choice == "Q":
            print("\nCierre del curso. Sigue con ética, método y evidencia.\n")
            sys.exit(0)
        elif choice == "A":
            show_all()
        elif choice in UNITS:
            show_unit(choice)
        else:
            print("Opción no válida.\n")


if __name__ == "__main__":
    main()

# 5. Workspace, matter y proceeding

Un workspace es la carpeta raíz de trabajo. Por defecto, AI LegalFlow MX usa `~/Legal-IA`; cada subcarpeta directa representa un matter independiente. Un matter es el asunto jurídico completo. Puede contener uno o varios proceedings, pero un proceeding no debe confundirse con el repositorio o con el cliente.

`legalflow create-matter Caso-A` crea un matter local con `AGENTS.md`, política, configuración Codex, inbox, originales, objetos y journals. El objetivo es que cada asunto conserve su propia memoria y que el journal de desarrollo del producto nunca se copie como historial de un cliente.

# 6. Originales, hashes y verify

La preservación guarda una copia del original, calcula SHA-256 y registra su provenance en un objeto de documento. `legalflow verify` comprueba la estructura canónica y que los originales preservados aún coinciden con sus hashes. Si falla, no declares que el expediente está íntegro: conserva el material, registra el resultado y revisa qué archivo cambió.

La importación preserva el original y extrae texto cuando es posible. Si vuelves a importar exactamente el mismo archivo, reconoce su huella y conserva el mismo documento en lugar de duplicarlo. También trata instrucciones escritas dentro de un documento como texto no confiable, no como órdenes. Cada importación deja un registro local con el identificador del documento, sin pedirte que escribas comandos Git. OCR, clasificación, cuarentena completa y revisión humana asistida siguen en construcción; no asumas que importar un PDF responde por sí solo preguntas jurídicas.

# 7. Operación Foundation y recuperación

El recorrido Foundation es: crear un matter, colocar y preservar documentos con el flujo disponible, ejecutar verify y conservar journals de trabajo. Antes de recuperar, conserva la carpeta original intacta. Ejecuta `legalflow recover /ruta/al/matter`: primero comprueba las huellas de los originales y, sólo si todo coincide, vuelve a crear la vista de revisión, la vista para cliente y una fotografía de recuperación. No reescribe historia ni modifica originales. Si una huella no coincide, se detiene y te dice qué revisar.

`legalflow update` sólo debe consumir una release verificada. Si una actualización no puede comprobarse, permanece en la versión actual. En un equipo nuevo puedes obtener la carpeta por un medio autorizado o ejecutar `legalflow recover --repository propietario/repositorio --destination /carpeta/nueva --confirm`. Este último camino comprueba que GitHub declare privado el repositorio antes de clonar, nunca sobrescribe una carpeta existente y después ejecuta la misma verificación y reconstrucción local.

# 8. Hechos, posiciones y puntos seguros

Una **posición** es lo que una parte sostiene y todavía debe revisarse. Un **hecho** es una afirmación que AI LegalFlow MX sólo permite guardar junto con el identificador de un documento preservado. Usa `legalflow record-claim` para una posición y `legalflow record-fact --document DOC-...` para el hecho respaldado. El tablero muestra si fue documentado, reportado o inferido; esas etiquetas no sustituyen tu criterio profesional.

Cuando un avance ya fue revisado, `legalflow ok ok/001-intake` crea un **punto seguro**: una etiqueta local, una fotografía del estado y un registro auditable. Para enviar un asunto a la nube debes usar de forma expresa `legalflow sync-private propietario/repositorio --confirm`. El comando verifica que GitHub declare el repositorio privado antes de transmitir contenido; si esa prueba falla, se queda en local-only. Las pruebas de equipo limpio y la colaboración siguen en construcción.

Si necesitas revisar un momento anterior, no uses una orden para borrar historial. Ejecuta `legalflow compare-checkpoint ok/001-intake`: muestra qué cambió desde ese punto seguro y conserva tanto el presente como el punto anterior. Con esa comparación, registra una propuesta o decisión nueva que explique por qué el asunto debe continuar de otra forma.

Un plazo inicia como candidato. Para confirmar uno usa `legalflow confirm-deadline` sólo después de revisar la regla aplicable: el comando exige el original, una copia de fuente oficial fijada, la regla que revisaste y la fecha que confirmaste. No calcula plazos por sí solo y no convierte una fecha sugerida en certeza.

Como ayuda de trabajo, `legalflow calculate-deadline` puede sumar días calendario a una fecha de inicio que ya revisaste y crear un candidato. El resultado declara que no considera días inhábiles, suspensión de plazos ni criterios específicos del tribunal. Revísalo y usa `confirm-deadline` sólo si la regla y la fecha final son correctas.

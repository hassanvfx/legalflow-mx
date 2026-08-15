# 8. Privacidad y límites de seguridad

Un repositorio privado no equivale a autorización para tratar información. No incluyas passwords, tokens, passkeys o códigos de MFA en journals, objetos, capturas o prompts. Mantén separados los matters y evita compartir un repositorio completo por defecto: un bundle redactado y revisado es más seguro cuando una persona externa necesita ayuda.

Los originales son WORM en el modelo objetivo: se preservan y se referencian, pero no se reescriben. La versión 0.1 protege esta idea mediante estructura y hashes. La IA debe declarar incertidumbre cuando falte evidencia, no rellenar huecos con una respuesta convincente.

# 9. Protege el trabajo y conserva el control

`legalflow security-audit` revisa la política local y los remotos Git configurados. Si el asunto dice local-only pero aparece un remoto, lo reporta como incumplimiento. `legalflow legal-hold "motivo"` deja una instrucción inmutable de conservación; no borra ni archiva archivos de forma automática. Para una comprobación local de conflictos, usa `legalflow conflict-add "nombre" --role client` y `legalflow conflict-check "nombre"`. El registro se cifra en la carpeta local del equipo, no se agrega al asunto ni se sincroniza; debes proporcionar su clave por una variable de entorno, sin escribirla en el comando o en el expediente. Una coincidencia sólo exige revisar: no decide por ti si hay conflicto. La retención formal y auditorías avanzadas todavía requieren sus propios gates.

Para crear una copia de trabajo, `legalflow redact DOC-... --replace "texto exacto"` sustituye únicamente los términos que tú indiques en el texto extraído. Nunca altera el original; el registro conserva huellas de los términos, no los términos mismos. Debes revisar visualmente la copia antes de compartirla: este flujo no identifica información sensible por su cuenta ni garantiza una redacción jurídica suficiente.

`legalflow dashboard` crea dos vistas reconstruidas: una vista de trabajo para counsel y un resumen de seguimiento para cliente que no incluye el texto de evidencia. `legalflow visual-verify` comprueba que ambas vistas coincidan con la huella del estado actual. Puedes usar `legalflow schedule-review AAAA-MM-DD "qué revisar"` para dejar una revisión de trabajo visible en ambas vistas. Es un recordatorio para la persona profesional, no un plazo legal. Ninguna imagen o vista es evidencia; siempre vuelve a los originales y a los objetos canónicos para revisar el expediente.

AI LegalFlow MX guarda documentos, hechos, actos, fuentes, decisiones, plazos y puntos seguros como registros trazables. Revisa siempre el original, la fuente y la decisión profesional antes de actuar.

El modelo jurídico separa claims de facts. Un claim es una afirmación atribuida; un fact requiere soporte y el nivel de certeza apropiado. Ya existe una primera ruta de fuente official-first y copia fijada, pero la resolución de vigencia todavía es conservadora y pide revisión si faltan fechas. Un plazo ambiguo queda como candidato y pide la constancia faltante; nunca inventa una fecha de vencimiento.

Al fijar una fuente con `legalflow source-resolve`, puedes registrar el inicio y fin de vigencia que revisaste. `legalflow source-temporal` sólo considera el intervalo si la fuente está marcada como oficial; incluso entonces la respuesta es “candidata aplicable”, no una conclusión jurídica ni el cálculo automático de un plazo.

El MCP Legal MX incluido es local y de sólo lectura: permite que el flujo guiado consulte las fuentes que ya fijaste y su revisión temporal candidata. No realiza búsquedas en Internet, no modifica el asunto y no sustituye la investigación ni el criterio jurídico profesional.

También son objetivo una timeline reproducible, estado procesal condicionado a evidencia, opciones por issue, revisión adversarial y dashboard determinista. Las imágenes generativas sólo podrán ser una capa visual: jamás la fuente de verdad jurídica.

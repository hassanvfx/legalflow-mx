# 10. Git, checkpoints y colaboración

El ledger local ya usa Git con un solo `main` y bloquea `reset` y `push` a través del producto. `legalflow ok ok/001-intake` crea un commit, una etiqueta anotada `ok/*`, una fotografía del estado y un registro auditable. `legalflow sync-private propietario/repositorio --confirm` sólo transmite después de comprobar que GitHub declara privado el remoto, y se detiene ante una respuesta ambigua. Esto no equivale a una revisión jurídica automática ni a colaboración gobernada.

Ya puedes registrar una invitación, el rol de la persona, su adhesión al asunto, una contribución compartida y un desacuerdo. Una propuesta no puede aceptarse mientras exista un desacuerdo abierto; sólo el owner deja una resolución auditable. El owner también puede revocar acceso local. Para una revisión externa usa `legalflow review-bundle --include ID`: el bundle entrega sólo los registros seleccionados y la vista reconstruida; no incluye originales ni journals. Si el repositorio es personal, `legalflow reviewer-access` no cambia permisos y te indica usar ese bundle. Si es una GitHub Organization privada, puede otorgar o revocar sólo lectura con confirmación y deja un registro local. El safe sync sólo incorpora por fast-forward contribuciones remotas no materiales; bloquea historias divergentes y cambios de evidencia, decisiones o plazos. Esto preserva las tres capas: notas privadas, contribuciones compartidas y estado aceptado. Aún no anuncies multi-counsel como una función completa: faltan trabajo desconectado y pruebas de integración reales.

# 10.1 Legal Packs

Un Legal Pack es una capa especializada, por ejemplo para contratos o amparo. El framework ya puede validar su manifiesto con `legalflow pack-validate`. Para superar el gate, el pack debe incluir schemas, Skills, fuentes oficiales, reglas de plazo, taxonomía, fixtures sintéticos, ejemplos, disclaimers y evidencia real de revisión del equipo jurídico mexicano: quién aprobó, cuándo y dónde se conserva la constancia. Un template pendiente no es un producto ni asesoría jurídica.

# 11. Troubleshooting seguro

Para Codex ausente, Git ausente, GitHub CLI ausente, autenticación, red, proxy, permisos, Python, Windows, recuperación o actualización, usa la página que el CLI presenta. Cada guía contiene pasos, alternativa segura y reanudación. La base de rutas es `https://hassanvfx.github.io/legalflow-mx/setup/` seguida del identificador del requisito.

No desactives controles de seguridad, no uses permisos administrativos por comodidad y no ignores un checksum fallido. Si no puedes verificar una acción externa, conserva local-only y documenta el bloqueo en lugar de improvisar.

# 12. Referencia rápida

`legalflow setup` revisa requisitos. `legalflow setup --resume` retoma después de resolverlos. `legalflow setup --diagnose --json` y `legalflow doctor --json` ofrecen el contrato legible por máquina. `legalflow create-matter <nombre>` crea el asunto local. `legalflow verify` comprueba estructura y originales. `legalflow recover` y `legalflow update` muestran sus rutas seguras.

Escanea el QR de la última página para abrir la guía viva y recibir ayuda cuando la necesites.

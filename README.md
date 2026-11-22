# D&D 5e / 5.5e Master & Player Suite

Aplicacion de escritorio y servidor web local para la gestion integral de partidas presenciales de **Dungeons & Dragons**, con soporte dual para **5ta Edicion (2014 - sistema imperial: pies/libras)** y **Edicion 2024 / 5.5e (sistema metrico: metros/kilogramos)** en español.

Diseñada especificamente para mesas que utilizan **dados fisicos**, automatizando la contabilidad matematica, el seguimiento de reglas, la gestion de cargas, la proyeccion de mapas, la exportacion de hojas imprimibles y la consulta instantanea de manuales sin reemplazar la experiencia tradicional de tirar los dados en la mesa.

---

## Caracteristicas Principales

### Soporte Dual de Ediciones (5e y 5.5e)
- **Interruptor Global 5e / 5.5e:** Cambia instantaneamente toda la aplicacion de escritorio y el servidor movil entre las reglas de 2014 y 2024.
- **Separacion Automatica de Datos:** Los personajes, el bestiario, los catalogos de equipo/tienda, las unidades de medida (pies/lb vs. metros/kg) y las reglas de descansos se filtran y adaptan automaticamente a la edicion activa.

### Modulo de Jugadores (PC y Dispositivos Moviles)
- **Progresion Acumulativa Nivel 1 a 20 (Estilo Shard):** Constructor paso a paso que habilita las decisiones correspondientes a cada nivel segun la edicion (Razas, Subrazas y bonos raciales en 5e; Especie, Linaje, Trasfondo 2024 y Dote de Origen en 5.5e; subclases en su nivel oficial 1, 2 o 3; Pericias, Invocaciones, Estilos de Combate, Mejoras de Caracteristica, Dotes Generales y Dones Epicos).
- **Combate, Salvaciones contra Muerte y Maestrias de Armas:** Autocompletado de armas con calculo automatico de ataque, daño y Clase de Armadura (CA), maestrias tacticas en 5.5e y casillas interactivas de Salvaciones contra Muerte sincronizadas entre PC y celular.
- **Retrato del Personaje y Exportacion a PDF:** Carga de imagen de perfil para cada heroe (visible en escritorio, celular y PDF) y generador de hoja de personaje en formato PDF de 2 paginas listo para imprimir con el logo de la aplicacion.
- **Lanzamiento de Conjuros:** Rastreador de espacios de conjuro por nivel, listado de conjuros siempre preparados por clase/subclase y consulta directa del texto en los manuales PDF.
- **Inventario Jerarquico y Monturas:** Calculo automatico de peso y sobrecarga (en kg o lb) con soporte para contenedores desplegables, paquetes de aventurero auto-desempaquetables, transferencia de carga hacia monturas/vehiculos y control de las 3 ranuras de sintonizacion magica.

### Modulo del Dungeon Master
- **Carpetas de Aventura y Generador de PNJs:** Gestion organizada de multiples campañas, notas de sesion, lugares y PNJs con registro de actitud social (Amistoso, Indiferente, Hostil) y generador rapido de PNJs aleatorios con rasgos y secretos.
- **Constructor y Rastreador de Combate:** Creacion previa de encuentros con calculo de dificultad segun el grupo activo. Ordenamiento por iniciativa fisica, control de asaltos, consulta rapida de efectos de estados, alerta automatica de pruebas de Concentracion con calculo de CD al recibir daño, y entrega directa de puntos de experiencia (PX) y botin a las hojas de los jugadores.
- **Bestiario y Fragua de Monstruos:** Creacion y edicion de perfiles de criaturas separados por edicion (5e y 5.5e).
- **Tienda y Taberna Interactiva:** Configuracion de comercios en tiempo real con multiplicadores de precio personalizados. Los jugadores pueden comprar desde sus dispositivos moviles con conversion y descuento automatico de monedas, o vender equipo al 50% de su valor oficial.
- **Mesa en Vivo y Proyector de Handouts:** Envio en tiempo real de mapas, cartas o paginas de manuales PDF a los navegadores moviles de los jugadores con actualizacion automatica, acompañado del rastreador publico de iniciativa con niebla de guerra (muestra unicamente si los enemigos estan Intactos, Maltrechos o Derrotados).
- **Pantalla de Referencia Rapida:** Calculadora de ritmo de viaje (km/h en 5.5e y millas/h en 5e), reglas de vision e iluminacion, cobertura y glosario interactivo adaptado a cada edicion.
- **Respaldo de Base de Datos:** Boton de copia de seguridad en un clic que guarda respaldos fechados de `dnd_data.db` en la carpeta local `backups/`.

### Motor de Indexacion y Extraccion PDF
- **Busqueda Full-Text (SQLite FTS5):** Localizacion instantanea de terminos, dotes, reglas y hechizos dentro de manuales PDF indexados localmente, con visor de paginas integrado.
- **Extraccion Automatizada:** Analizadores de texto para importar conjuros y perfiles de monstruos directamente desde manuales PDF de 5e y 5.5e (con capa de texto) hacia la base de datos SQLite.

---

## Estructura del Proyecto

```text
dnd55_suite/
├── database/
│   └── db_manager.py            # Gestor de persistencia SQLite y motor de busqueda FTS5
├── models/
│   ├── character_55e.py         # Reglas, catalogos y calculos de personajes 5.5e y despacho dual
│   ├── rules_5e.py              # Catalogos, razas, subrazas, clases y equipo de D&D 5e (2014)
│   └── monster_55e.py           # Reglas, tablas de VD/PX y plantillas del bestiario
├── pdf_engine/
│   ├── pdf_engine.py            # Indexador PyMuPDF, renderizador y extractores de conjuros/monstruos
│   └── sheet_pdf_exporter.py    # Exportador de hojas de personaje a PDF imprimible de 2 paginas
├── ui/
│   ├── char_sheet_view.py       # Interfaz de hojas de personaje, retrato, inventario y opciones Shard
│   ├── dm_tools_view.py         # Interfaz del DM: carpetas, combate, bestiario, tienda y referencia
│   └── main_indexer_ui.py       # Interfaz de biblioteca y lector de manuales PDF
├── main.py                      # Punto de entrada principal, selector de edicion, respaldo y QR
├── mobile_server.py             # Servidor web multihilo local para iOS y Android
├── build_windows_app.py         # Script de empaquetado para generar el ejecutable de Windows (.exe)
└── requirements.txt             # Dependencias del proyecto
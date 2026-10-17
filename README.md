# D&D 5.5e Master & Player Suite

Aplicacion de escritorio y servidor web local para la gestion integral de partidas presenciales de **Dungeons & Dragons (Edicion 2024 / 5.5e)** en español y sistema metrico. 

Diseñada especificamente para mesas que utilizan **dados fisicos**, automatizando la contabilidad matematica, el seguimiento de reglas, la gestion de cargas, la proyeccion de mapas y la consulta instantanea de manuales sin reemplazar la experiencia tradicional de tirar los dados en la mesa.

---

## Caracteristicas Principales

### Modulo de Jugadores (PC y Dispositivos Moviles)
* **Progresion Acumulativa Nivel 1 a 20:** Constructor paso a paso que habilita las decisiones correspondientes a cada nivel (Especie, Linaje, Trasfondo 2024, Dote de Origen, Subclase en nivel 3, Pericias, Invocaciones, Estilos de Combate, Mejoras de Caracteristica, Dotes Generales y Dones Epicos).
* **Combate y Maestrias de Armas:** Autocompletado de las armas del Capitulo 6 con sus propiedades y maestrias tacticas (Hender, Mellar, Rozar, Empujar, Socavar, Ralentizar, Derribar y Hostigar), calculo automatico de Clase de Armadura (CA) segun el tipo de armadura equipada y escudo.
* **Lanzamiento de Conjuros:** Rastreador de espacios de conjuro por nivel, listado de conjuros siempre preparados por clase/subclase y consulta directa del texto en los manuales PDF.
* **Inventario Jerarquico y Monturas:** Calculo de peso en kilogramos con soporte para contenedores desplegables, paquetes de aventurero auto-desempaquetables, transferencia de carga hacia monturas/vehiculos y control de las 3 ranuras de sintonizacion magica.

### Modulo del Dungeon Master
* **Carpetas de Aventura Desplegables:** Gestion organizada de multiples campañas, notas de sesion, lugares y PNJs con registro de actitud social (Amistoso, Indiferente, Hostil).
* **Constructor y Rastreador de Combate:** Creacion previa de encuentros con calculo de dificultad segun el nivel del grupo. Ordenamiento por iniciativa fisica, control de asaltos, estados/condiciones y entrega directa de puntos de experiencia (PX) y botin a las hojas de los jugadores.
* **Bestiario y Fragua de Monstruos:** Creacion y edicion de perfiles de criaturas en sistema metrico.
* **Tienda y Taberna Interactiva:** Configuracion de comercios en tiempo real con multiplicadores de precio personalizados. Los jugadores pueden comprar desde sus dispositivos moviles con conversion y descuento automatico de monedas, o vender equipo al 50% de su valor oficial.
* **Mesa en Vivo y Proyector de Handouts:** Envio en tiempo real de mapas, cartas o paginas de manuales PDF a los navegadores moviles de los jugadores, acompañado del rastreador publico de iniciativa con niebla de guerra (muestra unicamente si los enemigos estan Intactos, Maltrechos o Derrotados).
* **Pantalla de Referencia Rapida:** Calculadora de ritmo de viaje (Rapido, Normal, Lento), reglas de vision e iluminacion, cobertura y glosario interactivo del Capitulo 1.

### Motor de Indexacion y Extraccion PDF
* **Busqueda Full-Text (SQLite FTS5):** Localizacion instantanea de terminos, dotes, reglas y hechizos dentro de manuales PDF indexados localmente, con visor de paginas integrado.
* **Extraccion Automatizada:** Analizadores de texto para importar conjuros y perfiles de monstruos directamente desde los archivos PDF del usuario hacia la base de datos SQLite.

---

## Estructura del Proyecto

```text
dnd55_suite/
├── database/
│   └── db_manager.py          # Gestor de persistencia SQLite y motor de busqueda FTS5
├── models/
│   ├── character_55e.py       # Reglas, catalogos metricos y calculos de personajes 5.5e
│   └── monster_55e.py         # Reglas, tablas de VD/PX y plantillas del bestiario
├── pdf_engine/
│   └── pdf_engine.py          # Indexador PyMuPDF, renderizador y extractores de conjuros/monstruos
├── ui/
│   ├── char_sheet_view.py     # Interfaz de hojas de personaje, inventario y constructores
│   ├── dm_tools_view.py       # Interfaz del DM: carpetas, combate, bestiario, tienda y referencia
│   └── main_indexer_ui.py     # Interfaz de biblioteca y lector de manuales PDF
├── main.py                    # Punto de entrada principal y barra de navegacion con QR
├── mobile_server.py           # Servidor web multihilo local para iOS y Android
├── build_windows_app.py       # Script de empaquetado para generar el ejecutable de Windows (.exe)
└── requirements.txt           # Dependencias del proyecto
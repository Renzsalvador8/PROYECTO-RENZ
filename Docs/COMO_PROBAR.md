# Cómo probar *The Tester — The Ultimate Test*

Hay dos caminos. Si quieres jugar hoy mismo en tu computadora, usa la **Opción A** (Unity). Si quieres un **link
para jugar en el navegador** y compartirlo con el cliente, usa la **Opción B** (GitHub hace la versión web por ti).

> Importante: el juego se armó sin poder abrir Unity (no está disponible en el entorno donde se programó). La
> lógica está probada (40 pruebas automáticas) y todo el código compila contra las librerías de Unity, pero la
> **primera vez que lo abras en Unity 6 es la primera ejecución real**. Si aparece cualquier error en la consola,
> cópialo y envíamelo tal cual.

---

## Opción A — Jugar en tu computadora con Unity (≈ 30–60 min la primera vez)

1. **Instala Unity Hub** desde <https://unity.com/download> e inicia sesión con una cuenta Unity (gratis).
   En *Preferences ▸ Licenses ▸ Add* elige **"Get a free personal license"**.
2. **Instala Unity 6**: en Hub ▸ *Installs ▸ Install Editor* elige **Unity 6000.0 LTS** (el proyecto usa la
   6000.0.47f1; cualquier 6000.0.x más nueva también sirve, acepta si Hub pregunta por actualizar).
   Marca el módulo **"Web Build Support"** si también quieres generar la versión web desde tu equipo.
3. **Descarga el proyecto**: en GitHub, botón verde **Code ▸ Download ZIP** (rama `claude/eloquent-turing-hyvqcr`)
   y descomprímelo; o con git: `git clone https://github.com/Renzsalvador8/PROYECTO-RENZ.git`.
4. En Unity Hub: **Add ▸ Add project from disk** y elige la carpeta del proyecto. La primera apertura tarda varios
   minutos (Unity importa todo). Si aparece un aviso sobre el *Input System* (“enable the new backends?”), responde
   **Yes**: Unity se reinicia solo.
5. El proyecto se configura automáticamente. En la barra de menú superior aparece **The Tester**:
   * **The Tester ▸ ▶ Jugar desde el menú principal** → empieza el juego.
   * **The Tester ▸ Borrar partida guardada** → reinicia el progreso.
   * **The Tester ▸ Validar contenido** → comprueba que no falte ningún arte, sonido o dato.
   * **The Tester ▸ Configurar proyecto** → vuelve a aplicar la configuración si algo se ve raro.
6. En la pestaña **Game**, pon la resolución en **16:9 (1920×1080)** para verlo como en la web.

**Controles:** **A/D** o **←/→** caminar · **E** (o Enter) inspeccionar/interactuar · **ratón** mover la lupa,
**clic** señalar un detalle · **Esc** (o P) pausa. En el manejo: **D/→** acelerar, **A/←** frenar (mantén el freno
con el auto detenido para retroceder), **W/S** o **↑/↓** cambiar de carril, **Espacio** claxon. En la llegada al
concesionario, Espacio/Enter/E salta la introducción. En celulares y tablets aparecen botones táctiles.

**Pruebas automáticas dentro de Unity:** *Window ▸ General ▸ Test Runner*: pestaña **EditMode ▸ Run All**
(44 pruebas) y pestaña **PlayMode** (una partida completa jugada sola, del menú a la pantalla final, unos minutos).

**Versión web desde tu equipo:** **The Tester ▸ Construir WebGL** → se crea `Builds/WebGL/`. No abras el
`index.html` con doble clic (los navegadores lo bloquean); sírvelo con un servidor local, por ejemplo:

```bash
cd Builds/WebGL
python3 -m http.server 8080      # luego abre http://localhost:8080
```

---

## Opción B — Link para jugar en el navegador (GitHub lo construye solo)

El repositorio ya incluye una automatización (`.github/workflows/webgl.yml`). Cada vez que se suben cambios:

* siempre corre la **verificación sin Unity** (pruebas + compilación);
* si configuras tu licencia de Unity (gratis), además **construye la versión web con Unity 6** y la **publica** en
  **<https://renzsalvador8.github.io/PROYECTO-RENZ/>**.

Configuración, una sola vez:

1. **Archivo de licencia de Unity (.ulf).** Necesitas Unity Hub (paso A.1, no hace falta instalar el editor).
   En *Preferences ▸ Licenses* pulsa **Add ▸ Get a free personal license** (aunque ya veas una licencia).
   Se crea el archivo `Unity_lic.ulf` en:
   * Windows: `C:\ProgramData\Unity\Unity_lic.ulf`
   * Mac: `/Library/Application Support/Unity/Unity_lic.ulf`
   * Linux: `~/.local/share/unity3d/Unity/Unity_lic.ulf`
2. En GitHub, en el repositorio: **Settings ▸ Secrets and variables ▸ Actions ▸ New repository secret**, crea tres:
   * `UNITY_LICENSE` → pega **todo** el contenido del archivo `.ulf` (ábrelo con el Bloc de notas).
   * `UNITY_EMAIL` → el correo de tu cuenta Unity.
   * `UNITY_PASSWORD` → la contraseña de tu cuenta Unity (si entras con Google/Apple, crea una contraseña en
     <https://id.unity.com>; evita símbolos raros).
3. **Settings ▸ Pages ▸ Build and deployment ▸ Source: GitHub Actions.**
4. **Actions ▸ The Tester · WebGL ▸ Run workflow.** La primera vez tarda ~25–45 minutos (descarga Unity);
   después, ~10–20.
5. Juega en **<https://renzsalvador8.github.io/PROYECTO-RENZ/>**. Cada ejecución también deja un ZIP descargable
   (**Actions ▸ la ejecución ▸ Artifacts ▸ TheTester-WebGL**) para subirlo a la web de Zenith Studio.

Si no configuras los secretos, la automatización igual verifica el código y simplemente **omite** (no falla) la
parte de Unity.

### Insertarlo en la web de Zenith Studio

Sube el contenido de `Builds/WebGL/` (o del ZIP) a una carpeta del sitio y usa:

```html
<iframe src="/the-tester/index.html" style="width:100%; aspect-ratio:16/9; border:0" allow="fullscreen; autoplay"></iframe>
```

---

## Qué revisar mientras juegas (lista corta)

1. **Menú**: música (tu canción), botones, ajustes de volumen, créditos.
2. **Concesionario**: llegada, muro con el logo de Hyundai, aviso **PRESIONA E PARA INSPECCIONAR**.
3. **Inspección exterior** (5 zonas con la lupa: faros, ruedas, carrocería, puertas, parrilla con el emblema).
4. **Prueba de detalles interiores** (4 detalles, lupa grande, “Esto es sospechoso.”).
5. **Prueba de manejo** (~50 s): semáforo, obstáculo, zona escolar a 30 km/h, estacionamiento; primer plano final y
   **PRUEBAS COMPLETADAS**.
6. **Zenith Studio** (tu pintura): la cámara arranca en el letrero, se abre a toda la oficina, Jean Paul entra por
   detrás de las cajas; recibe **LUX Grand Prix** y **EFFIE Bronce** (pulsa E dos veces junto a los pedestales); primer plano final con
   la oficina desenfocada; pantalla final con **JUGAR DE NUEVO / VOLVER AL MENÚ**.
7. **Pausa (Esc)**, guardar/continuar (cierra y vuelve a abrir: “Continuar”).

Si algo falla, envíame: qué estabas haciendo, una captura, y el texto rojo de la ventana **Console** de Unity
(o, en el navegador, la consola de desarrollador: F12).

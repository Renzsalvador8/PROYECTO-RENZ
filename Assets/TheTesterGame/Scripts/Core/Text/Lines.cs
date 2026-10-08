using System.Collections.Generic;

namespace TheTester.Core
{
    /// <summary>
    /// Every narrative line and UI string of the game (Spanish). Centralised for easy editing/localisation.
    /// Jean Paul Tester speaks in short, deadpan sentences.
    /// </summary>
    public static class Lines
    {
        // ------------------------------------------------------------------ menu / UI
        public const string MenuPlay = "JUGAR";
        public const string MenuContinue = "CONTINUAR";
        public const string MenuInstructions = "INSTRUCCIONES";
        public const string MenuSettings = "AJUSTES";
        public const string MenuQuit = "SALIR";
        public const string MenuBack = "VOLVER";
        public const string MenuCredits = "CRÉDITOS";
        public const string Footer = "© Zenith Studio · Creado para Hyundai";

        public const string InstructionsTitle = "INSTRUCCIONES";
        public const string InstructionsKeyboard =
            "A / D  o  ← / →    Caminar\n" +
            "E    Interactuar · Inspeccionar\n" +
            "Ratón    Mover la lupa\n" +
            "Clic    Señalar un detalle\n" +
            "Espacio    Acción contextual (claxon)\n" +
            "W / S  o  ↑ / ↓    Cambiar de carril\n" +
            "Esc    Pausa";
        public const string InstructionsTouch =
            "En pantallas táctiles: flechas para caminar, botón de acción para interactuar, " +
            "arrastra el dedo para mover la lupa y usa los pedales para conducir.";
        public const string InstructionsGoal = "Tres pruebas. Un crítico. Ningún defecto… en teoría.";

        public const string SettingsTitle = "AJUSTES";
        public const string SettingsMusic = "MÚSICA";
        public const string SettingsAmbience = "AMBIENTE";
        public const string SettingsSfx = "EFECTOS";
        public const string SettingsFullscreen = "PANTALLA COMPLETA";
        public const string On = "SÍ";
        public const string Off = "NO";

        public const string CreditsTitle = "CRÉDITOS";
        public const string CreditsBody =
            "THE TESTER — THE ULTIMATE TEST\nUn juego original de Zenith Studio\n\n" +
            "Personaje: Jean Paul Tester, creado por Zenith Studio para Hyundai\n" +
            "Tipografías: Cormorant Garamond y Jost (SIL Open Font License)\n" +
            "Música y sonido: diseño procedural original\n\nCREATE BEYOND REAL";

        public const string PauseTitle = "PAUSA";
        public const string PauseResume = "CONTINUAR";
        public const string PauseRestart = "REINICIAR NIVEL";
        public const string PauseMenu = "MENÚ PRINCIPAL";

        public const string TestsLabel = "PRUEBAS";
        public const string ObjectiveLabel = "OBJETIVO";
        public const string Loading = "Cargando…";

        // ------------------------------------------------------------------ prompts
        public const string PromptInspect = "PRESIONA E PARA INSPECCIONAR";
        public const string PromptObserve = "PRESIONA E PARA OBSERVAR";
        public const string PromptDrive = "PRESIONA E PARA LA PRUEBA DE MANEJO";
        public const string PromptAward = "PRESIONA E PARA RECIBIR EL PREMIO";
        public const string PromptAward2 = "PRESIONA E PARA RECIBIR EL SEGUNDO PREMIO";

        /// <summary>Touch-screen wording for a desktop prompt.</summary>
        public static string TouchPrompt(string desktop)
        {
            if (string.IsNullOrEmpty(desktop)) return desktop;
            return desktop.Replace("PRESIONA E PARA", "TOCA").Replace("PRESIONA E", "TOCA");
        }

        // ------------------------------------------------------------------ opening
        public const string Opening1 = "Dicen que nada es perfecto.";
        public const string Opening2 = "Jean Paul Tester está dispuesto a comprobarlo.";
        public const string LocationShowroom = "HYUNDAI · CONCESIONARIO";
        public const string LocationDrive = "PRUEBA 03 · CONDUCCIÓN";
        public const string LocationZenith = "ZENITH STUDIO";

        // ------------------------------------------------------------------ objectives
        public const string ObjExterior = "Inspecciona el exterior del IONIQ 5 · Estación 01";
        public const string ObjInterior = "Inspecciona el interior · Estación 02";
        public const string ObjToDrive = "Dirígete a la prueba de manejo";
        public const string ObjAwardsArea = "Dirígete al área de premiación";
        public const string ObjAward1 = "Recibe el primer premio";
        public const string ObjAward2 = "Recibe el segundo premio";

        public const string GateInteriorFirst = "Primero el exterior. Siempre el exterior.";
        public const string GateDriveFirst = "Aún no. Faltan pruebas.";

        // ------------------------------------------------------------------ test 01 · exterior
        public const string ExteriorTitle = "PRUEBA 01 · EXTERIOR";
        public const string ExteriorHint = "Pasa la lupa sobre cada zona y mantenla quieta.";
        public const string ExteriorHintTouch = "Arrastra la lupa sobre cada zona y mantenla quieta.";
        public static readonly string[] ExteriorOrder = { "headlights", "wheels", "bodywork", "doors", "grille" };
        public static readonly Dictionary<string, string> ExteriorLabels = new Dictionary<string, string>
        {
            { "headlights", "FAROS" },
            { "wheels", "LLANTAS" },
            { "bodywork", "CARROCERÍA" },
            { "doors", "ALINEACIÓN DE PUERTAS" },
            { "grille", "PARRILLA FRONTAL" },
        };
        public static readonly Dictionary<string, string> ExteriorNotes = new Dictionary<string, string>
        {
            { "headlights", "Faros de píxeles paramétricos. Conté cada píxel. Todos encendidos. Todos." },
            { "wheels", "Llantas: presión correcta. Simetría correcta. Qué decepción." },
            { "bodywork", "Ni una onda en el reflejo del capó. Lo miré desde tres ángulos." },
            { "doors", "Separación entre puertas: constante. Medida con mi tarjeta de visita." },
            { "grille", "Parrilla frontal. Limpia. Sospechosamente limpia." },
        };
        public const string ExteriorAllDone = "…";
        public const string ExteriorVerdict = "Interesante…";

        // ------------------------------------------------------------------ test 02 · interior
        public const string InteriorTitle = "PRUEBA 02 · DETALLE";
        public const string InteriorHint = "Encuentra en el habitáculo los cuatro detalles de la libreta. Haz clic con la lupa encima.";
        public const string InteriorHintTouch = "Encuentra los cuatro detalles de la libreta. Tócalos con la lupa encima.";
        public static readonly string[] InteriorOrder = { "volante", "costura", "rejilla", "reloj" };
        public static readonly Dictionary<string, string> InteriorClues = new Dictionary<string, string>
        {
            { "volante", "Cuatro puntos. Un mensaje oculto." },
            { "costura", "Una costura doble. Cuenta las puntadas." },
            { "rejilla", "Seis aletas. ¿Paralelas?" },
            { "reloj", "La hora. Debe coincidir con la mía." },
        };
        public static readonly Dictionary<string, string> InteriorFound = new Dictionary<string, string>
        {
            { "volante", "Cuatro puntos: «H» en código Morse. Lo verifiqué en Morse. Correcto. Lamentablemente." },
            { "costura", "Doce puntadas por decímetro. Conté dos veces. Doce. Las dos veces." },
            { "rejilla", "Aletas paralelas. Medí los ángulos. Idénticos. Esto no es normal." },
            { "reloj", "10:08. Coincide con mi reloj. Al segundo. ¿Quién sincroniza así un reloj?" },
        };
        public static readonly Dictionary<string, string> InteriorDecoys = new Dictionary<string, string>
        {
            { "espejo", "Un retrovisor. Me devuelve la mirada. Sin defectos. Ninguno de los dos." },
            { "portavasos", "Portavasos. Sostiene vasos. Siguiente." },
            { "cargador", "Cargador inalámbrico. Carga. Inalámbricamente." },
            { "guantera", "Guantera. Contiene el manual. Lo leí anoche." },
            { "palanca", "Selector de marcha en la columna. Elegante. No es lo que busco." },
            { "velocimetro", "Cero kilómetros por hora. Exacto." },
            { "reposacabezas", "Un reposacabezas. Reposa cabezas." },
            { "luz_ambiental", "Luz ambiental. Ambienta. Sigo buscando." },
            { "emergencia", "Luces de emergencia. No es una emergencia. Todavía." },
            { "parabrisas", "El parabrisas. Limpio. Demasiado limpio." },
        };
        public static readonly string[] InteriorNothing = { "Nada.", "Nada aquí.", "Sigo buscando.", "Mm. No." };
        public const string InteriorAlready = "Ya lo revisé. Dos veces, de hecho.";
        public const string InteriorRecheck1 = "Un momento.";
        public const string InteriorRecheck2 = "Otra vez. Por si acaso.";
        public const string InteriorSuspicious = "Esto es sospechoso.";

        // ------------------------------------------------------------------ showroom observations
        public static readonly Dictionary<string, string> Observations = new Dictionary<string, string>
        {
            { "coffee", "Café. Noventa y dos grados. Aceptable. Por ahora." },
            { "reception", "Recepción. Nadie. Ni una mota de polvo. Inquietante." },
            { "brochure", "El folleto dice «La perfección no existe». Ya veremos." },
            { "bronze_car", "Otro IONIQ 5. Mismo problema: ninguno." },
            { "desk", "Una línea de tiempo. Veinticuatro fotogramas por segundo. Ni uno más. Bien." },
            { "storyboard", "Alguien dibujó mi bigote. Con precisión. Inquietante." },
            { "poster_tester", "Un retrato. El bigote está… correcto." },
            { "camera", "Cámara de cine. Lente impecable. Lo comprobé. Dos veces." },
        };
        public const string IdleRemark = "…";

        // ------------------------------------------------------------------ test 03 · drive
        public const string DriveTitle = "PRUEBA 03 · CONDUCCIÓN";
        public const string DriveControls = "D / → acelerar · A / ← frenar · W / S cambiar de carril · Espacio claxon";
        public const string DriveControlsTouch = "Usa los pedales para acelerar y frenar, y las flechas para cambiar de carril.";
        public const string DriveObjectiveStart = "Sal del concesionario y acelera";
        public const string DriveObjectiveLight = "Detente antes de la línea del semáforo";
        public const string DriveObjectiveContinue = "Continúa";
        public const string DriveObjectiveObstacle = "Obstáculo adelante · cambia de carril";
        public const string DriveObjectiveBackLane = "Vuelve a tu carril";
        public const string DriveObjectiveSchool = "Zona escolar · máximo 30 km/h";
        public const string DriveObjectiveParking = "Estaciona dentro del recuadro";
        public const string DriveObjectiveDone = "Prueba completada";

        public const string DriveStartRemark = "Aceleración lineal. Sin tirones. Sigo atento.";
        public const string DriveStopped = "Frenado progresivo. Ni una gota de café derramada.";
        public const string DriveRanRed = "Eso era rojo. Lo anotaré… contra mí.";
        public const string DriveTooFar = "Más cerca, por favor. La línea no muerde.";
        public const string DriveObstacle = "Una furgoneta. «Envíos rápidos». Detenida.";
        public const string DriveAutoBrake = "Frenado automático de emergencia. Funciona. Qué fastidio.";
        public const string DrivePassed = "Cambio de carril limpio. Demasiado limpio.";
        public const string DriveSchool = "Zona escolar. Treinta. No treinta y uno.";
        public const string DriveSpeeding = "Treinta. Dije treinta.";
        public const string DriveQuiet = "Silencio en cabina. Puedo oír mis propios pensamientos. Son críticos.";
        public const string DriveParkingAhead = "Ahí. El recuadro. Precisión, por favor.";
        public const string DriveBarrier = "Fin del recorrido. Marcha atrás: mantén A / ←.";
        public const string DriveHorn = "Un claxon… cortés.";
        public const string DriveLaneNeedsSpeed = "Primero, avanzar. Luego, cambiar de carril.";
        public const string DriveParkedFormat = "Precisión: {0} cm.";
        public const string DriveScoreFormat = "Nota de conducción: {0}/10.";
        public const string TestsCompleted = "PRUEBAS COMPLETADAS";

        // ------------------------------------------------------------------ finale
        public const string AwardLuxTitle = "LUX GRAND PRIX";
        public const string AwardLuxSub = "Por una historia imposible de mejorar.";
        public const string AwardEffieTitle = "EFFIE ECUADOR · BRONCE";
        public const string AwardEffieSub = "Por resultados que ni él pudo objetar.";
        public const string FinalVerdict = "Veredicto final: sin defectos. Lamentablemente.";
        public const string EndStudio = "ZENITH STUDIO";
        public const string EndTagline = "CREATE BEYOND REAL";
        public const string EndTitle = "THE TESTER — THE ULTIMATE TEST";
        public const string EndPlayAgain = "JUGAR DE NUEVO";
        public const string EndMenu = "VOLVER AL MENÚ";
    }
}

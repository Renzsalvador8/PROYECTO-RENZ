using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace TheTester.EditorTools
{
    /// <summary>
    /// One-click (and first-load) configuration: scenes + Build Settings, player/WebGL settings, 2D defaults.
    /// Menu: The Tester ▸ …
    /// </summary>
    [InitializeOnLoad]
    public static class TheTesterProjectSetup
    {
        public const string ScenesDir = "Assets/TheTesterGame/Scenes";
        private const string MarkerFile = "ProjectSettings/TheTesterSetup.txt";
        private static readonly (string name, TheTester.GameScene scene)[] Scenes =
        {
            ("00_MainMenu", TheTester.GameScene.MainMenu),
            ("01_Showroom", TheTester.GameScene.Showroom),
            ("02_TestDrive", TheTester.GameScene.TestDrive),
            ("03_ZenithStudio", TheTester.GameScene.ZenithStudio),
        };

        static TheTesterProjectSetup()
        {
            EditorApplication.delayCall += () =>
            {
                if (EditorApplication.isPlayingOrWillChangePlaymode) return;
                if (!File.Exists(MarkerFile)) Configure(false);
                else EnsureScenesInBuildSettings(false);
            };
        }

        [MenuItem("The Tester/Configurar proyecto", priority = 1)]
        public static void ConfigureMenu() => Configure(true);

        public static void Configure(bool verbose)
        {
            EnsureScenes(verbose);
            EnsureScenesInBuildSettings(verbose);
            PlayerSettings.companyName = "Zenith Studio";
            PlayerSettings.productName = "The Tester — The Ultimate Test";
            PlayerSettings.defaultScreenWidth = 1920;
            PlayerSettings.defaultScreenHeight = 1080;
            PlayerSettings.defaultWebScreenWidth = 1280;
            PlayerSettings.defaultWebScreenHeight = 720;
            PlayerSettings.runInBackground = true;
            PlayerSettings.SplashScreen.backgroundColor = new Color32(9, 27, 45, 255);
            if (PlayerSettings.colorSpace != ColorSpace.Gamma) PlayerSettings.colorSpace = ColorSpace.Gamma;
            PlayerSettings.WebGL.compressionFormat = WebGLCompressionFormat.Gzip;
            PlayerSettings.WebGL.decompressionFallback = true;
            PlayerSettings.WebGL.dataCaching = true;
            if (Directory.Exists("Assets/WebGLTemplates/TheTester")) PlayerSettings.WebGL.template = "PROJECT:TheTester";
            EditorSettings.defaultBehaviorMode = EditorBehaviorMode.Mode2D;
            File.WriteAllText(MarkerFile, "The Tester project configured. Delete this file to run the automatic setup again.\n");
            AssetDatabase.SaveAssets();
            if (verbose) Debug.Log("[The Tester] Proyecto configurado: escenas, Build Settings y ajustes de WebGL listos.");
        }

        /// <summary>Creates any missing scene (an empty scene holding only the SceneBootstrap).</summary>
        public static void EnsureScenes(bool verbose)
        {
            if (!Directory.Exists(ScenesDir)) Directory.CreateDirectory(ScenesDir);
            foreach (var (name, scene) in Scenes)
            {
                string path = ScenesDir + "/" + name + ".unity";
                if (File.Exists(path) && HasBootstrap(path)) continue;
                RegenerateScene(path, scene);
                if (verbose) Debug.Log("[The Tester] Escena regenerada: " + path);
            }
        }

        private static bool HasBootstrap(string path)
        {
            string guid = BootstrapScriptGuid();
            return !string.IsNullOrEmpty(guid) && File.ReadAllText(path).Contains(guid);
        }

        private static string BootstrapScriptGuid()
        {
            foreach (var g in AssetDatabase.FindAssets("SceneBootstrap t:MonoScript"))
                if (AssetDatabase.GUIDToAssetPath(g).EndsWith("/SceneBootstrap.cs")) return g;
            return null;
        }

        public static void RegenerateScene(string path, TheTester.GameScene scene)
        {
            var previous = EditorSceneManager.GetActiveScene().path;
            var s = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var go = new GameObject("SceneBootstrap");
            go.AddComponent<TheTester.SceneBootstrap>().scene = scene;
            EditorSceneManager.SaveScene(s, path);
            if (!string.IsNullOrEmpty(previous) && File.Exists(previous)) EditorSceneManager.OpenScene(previous);
        }

        public static void EnsureScenesInBuildSettings(bool verbose)
        {
            var wanted = Scenes.Select(s => ScenesDir + "/" + s.name + ".unity").Where(File.Exists).ToList();
            var current = EditorBuildSettings.scenes.Select(s => s.path).ToList();
            if (current.Take(wanted.Count).SequenceEqual(wanted)) return;
            var list = new List<EditorBuildSettingsScene>();
            foreach (var p in wanted) list.Add(new EditorBuildSettingsScene(p, true));
            foreach (var s in EditorBuildSettings.scenes) if (!wanted.Contains(s.path)) list.Add(s);
            EditorBuildSettings.scenes = list.ToArray();
            if (verbose) Debug.Log("[The Tester] Build Settings actualizados con las 4 escenas del juego.");
        }

        [MenuItem("The Tester/▶ Jugar desde el menú principal", priority = 0)]
        public static void PlayFromMenu()
        {
            if (EditorApplication.isPlaying) return;
            Configure(false);
            if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
            EditorSceneManager.OpenScene(ScenesDir + "/00_MainMenu.unity");
            EditorApplication.isPlaying = true;
        }

        [MenuItem("The Tester/Borrar partida guardada", priority = 20)]
        public static void ClearSave()
        {
            TheTester.SaveManager.ClearProgress();
            Debug.Log("[The Tester] Partida guardada eliminada.");
        }
    }
}

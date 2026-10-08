using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEngine;

namespace TheTester.EditorTools
{
    /// <summary>Build helpers: The Tester ▸ Construir WebGL (and a command-line entry point for CI).</summary>
    public static class TheTesterBuild
    {
        public const string WebGLOutput = "Builds/WebGL";

        [MenuItem("The Tester/Construir WebGL", priority = 40)]
        public static void BuildWebGLMenu()
        {
            if (!BuildPipeline.IsBuildTargetSupported(BuildTargetGroup.WebGL, BuildTarget.WebGL))
            {
                EditorUtility.DisplayDialog("The Tester", "El módulo «Web Build Support» no está instalado.\nInstálalo desde Unity Hub ▸ Installs ▸ Add modules.", "OK");
                return;
            }
            var report = BuildWebGL();
            if (report.summary.result == BuildResult.Succeeded)
                EditorUtility.RevealInFinder(WebGLOutput);
        }

        /// <summary>CLI: Unity -batchmode -quit -projectPath . -executeMethod TheTester.EditorTools.TheTesterBuild.BuildWebGLBatch</summary>
        public static void BuildWebGLBatch()
        {
            var report = BuildWebGL();
            EditorApplication.Exit(report.summary.result == BuildResult.Succeeded ? 0 : 1);
        }

        public static BuildReport BuildWebGL()
        {
            TheTesterProjectSetup.Configure(false);
            if (EditorUserBuildSettings.activeBuildTarget != BuildTarget.WebGL)
                EditorUserBuildSettings.SwitchActiveBuildTarget(BuildTargetGroup.WebGL, BuildTarget.WebGL);
            Directory.CreateDirectory(WebGLOutput);
            var scenes = EditorBuildSettings.scenes.Where(s => s.enabled && s.path.StartsWith(TheTesterProjectSetup.ScenesDir)).Select(s => s.path).ToArray();
            var options = new BuildPlayerOptions
            {
                scenes = scenes,
                locationPathName = WebGLOutput,
                target = BuildTarget.WebGL,
                options = BuildOptions.None,
            };
            var report = BuildPipeline.BuildPlayer(options);
            var sum = report.summary;
            Debug.Log("[The Tester] WebGL build: " + sum.result + " · " + (sum.totalSize / (1024f * 1024f)).ToString("0.0") + " MB · " +
                      sum.totalTime.TotalSeconds.ToString("0") + " s → " + Path.GetFullPath(WebGLOutput));
            return report;
        }
    }
}

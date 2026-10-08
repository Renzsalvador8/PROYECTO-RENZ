using TheTester.Core;
using UnityEngine;

namespace TheTester
{
    /// <summary>Persists progress and settings with PlayerPrefs (IndexedDB on WebGL).</summary>
    public static class SaveManager
    {
        private const string ProgressKey = "tt.progress";
        private const string MusicKey = "tt.vol.music";
        private const string SfxKey = "tt.vol.sfx";
        private const string AmbKey = "tt.vol.amb";

        public static GameProgress LoadProgress() => GameProgress.Deserialize(PlayerPrefs.GetString(ProgressKey, ""));

        public static bool HasSave
        {
            get
            {
                var p = LoadProgress();
                return p.Chapter > Chapter.NewGame && p.Chapter < Chapter.Completed;
            }
        }

        public static void SaveProgress(GameProgress p)
        {
            if (p == null) return;
            PlayerPrefs.SetString(ProgressKey, p.Serialize());
            PlayerPrefs.Save();
        }

        public static void ClearProgress()
        {
            PlayerPrefs.DeleteKey(ProgressKey);
            PlayerPrefs.Save();
        }

        public static float MusicVolume { get => PlayerPrefs.GetFloat(MusicKey, 0.8f); set { PlayerPrefs.SetFloat(MusicKey, value); PlayerPrefs.Save(); } }
        public static float SfxVolume { get => PlayerPrefs.GetFloat(SfxKey, 0.9f); set { PlayerPrefs.SetFloat(SfxKey, value); PlayerPrefs.Save(); } }
        public static float AmbienceVolume { get => PlayerPrefs.GetFloat(AmbKey, 0.8f); set { PlayerPrefs.SetFloat(AmbKey, value); PlayerPrefs.Save(); } }
    }
}

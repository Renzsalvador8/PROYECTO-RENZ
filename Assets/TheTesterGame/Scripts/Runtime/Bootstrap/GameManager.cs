using System.Collections;
using TheTester.Core;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.SceneManagement;

namespace TheTester
{
    /// <summary>
    /// Persistent root of the game: owns progress/save state, audio, UI, input and scene flow.
    /// </summary>
    public sealed class GameManager : MonoBehaviour
    {
        public static GameManager I { get; private set; }

        public GameProgress Progress { get; private set; }
        public DirectorBase Director { get; private set; }
        public GameScene CurrentScene { get; private set; }
        public bool Paused { get; private set; }
        public bool Loading { get; private set; }

        /// <summary>Normally 1. Automated play-through tests raise it to run faster.</summary>
        public static float TimeScaleWhenRunning = 1f;

        public static GameManager Ensure()
        {
            if (I != null) return I;
            var go = new GameObject("TheTester · GameManager");
            DontDestroyOnLoad(go);
            I = go.AddComponent<GameManager>();
            I.Init();
            return I;
        }

        private void Init()
        {
            // WebGL paces frames with requestAnimationFrame; forcing a target frame rate there causes stutter.
            if (Application.platform != RuntimePlatform.WebGLPlayer)
            {
                Application.targetFrameRate = 60;
                QualitySettings.vSyncCount = 0;
            }
            Progress = SaveManager.LoadProgress();
            Progress.ChapterChanged += _ => SaveManager.SaveProgress(Progress);
            gameObject.AddComponent<GameInputUpdater>();
            gameObject.AddComponent<AudioListener>();     // persistent: all game audio is non-spatial
            gameObject.AddComponent<AudioManager>();
            EnsureEventSystem();
            var ui = new GameObject("UI");
            ui.transform.SetParent(transform, false);
            ui.AddComponent<UIManager>();
        }

        private void EnsureEventSystem()
        {
            if (EventSystem.current != null) return;
            var es = new GameObject("EventSystem");
            es.transform.SetParent(transform, false);
            es.AddComponent<EventSystem>();
#if TT_INPUT_SYSTEM && ENABLE_INPUT_SYSTEM
            es.AddComponent<UnityEngine.InputSystem.UI.InputSystemUIInputModule>();
#else
            es.AddComponent<StandaloneInputModule>();
#endif
        }

        internal void OnSceneStarted(GameScene scene, GameObject host)
        {
            CurrentScene = scene;
            SetPaused(false);
            UIManager.I.ResetForScene();
            switch (scene)
            {
                case GameScene.Showroom: Director = host.AddComponent<ShowroomDirector>(); break;
                case GameScene.TestDrive: Director = host.AddComponent<DriveDirector>(); break;
                case GameScene.ZenithStudio: Director = host.AddComponent<ZenithDirector>(); break;
                default: Director = host.AddComponent<MainMenuDirector>(); break;
            }
            Loading = false;
        }

        private void Update()
        {
            if (GameInput.PauseDown && CurrentScene != GameScene.MainMenu && !Loading && Director != null && Director.AllowPause)
                SetPaused(!Paused);
        }

        public void SetPaused(bool paused)
        {
            Paused = paused;
            Time.timeScale = paused ? 0f : TimeScaleWhenRunning;
            if (paused) Cursor.visible = true;
            AudioListener.pause = false;
            if (UIManager.I != null) UIManager.I.ShowPause(paused);
            if (Director != null) Director.OnPauseChanged(paused);
        }

        // ------------------------------------------------------------------ flow
        public void NewGame()
        {
            Progress.ResetStory();
            SaveManager.SaveProgress(Progress);
            GoTo(GameScene.Showroom);
        }

        public void Continue()
        {
            Progress = SaveManager.LoadProgress();
            Progress.ChapterChanged += _ => SaveManager.SaveProgress(Progress);
            Progress.NormalizeForContinue();
            GoTo(GameScenes.ForChapter(Progress.Chapter));
        }

        public void RestartLevel() => GoTo(CurrentScene);

        public void ToMenu() => GoTo(GameScene.MainMenu);

        public void Save() => SaveManager.SaveProgress(Progress);

        public void GoTo(GameScene scene)
        {
            if (Loading) return;
            StartCoroutine(LoadRoutine(scene));
        }

        private IEnumerator LoadRoutine(GameScene scene)
        {
            Loading = true;
            if (Paused) SetPaused(false);
            Time.timeScale = TimeScaleWhenRunning;
            Cursor.visible = true;
            GameInput.ClearVirtual();
            yield return UIManager.I.FadeOut(0.8f);
            AudioManager.I.StopAllLoops();
            string name = GameScenes.SceneName(scene);
            if (Application.CanStreamedLevelBeLoaded(name))
            {
                var op = SceneManager.LoadSceneAsync(name);
                while (!op.isDone) yield return null;
            }
            else
            {
                // Scenes not in Build Settings (e.g. opened as loose files): rebuild in place.
                Debug.LogWarning("[TheTester] Scene '" + name + "' is not in Build Settings. Run 'The Tester ▸ Configurar proyecto'. Building it in a temporary scene.");
                var old = SceneManager.GetActiveScene();
                var tmp = SceneManager.CreateScene(name + "_runtime_" + Time.frameCount);
                SceneManager.SetActiveScene(tmp);
                var unload = SceneManager.UnloadSceneAsync(old);
                while (unload != null && !unload.isDone) yield return null;
                var host = new GameObject("SceneBootstrap");
                host.AddComponent<SceneBootstrap>().scene = scene;
            }
        }
    }
}

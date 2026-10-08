using System.Collections;
using TheTester.Core;
using UnityEngine;

namespace TheTester
{
    /// <summary>Base for the per-scene "directors": build the level, then run the scene script as coroutines.</summary>
    public abstract class DirectorBase : MonoBehaviour
    {
        public CameraController Cam { get; protected set; }
        public LevelInstance Level { get; protected set; }
        public PlayerController2D Player { get; protected set; }
        public InteractionSystem Interactions { get; protected set; }
        public virtual bool AllowPause => true;
        protected GameProgress Progress => GameManager.I.Progress;
        protected UIManager UI => UIManager.I;
        protected AudioManager Audio => AudioManager.I;

        /// <summary>Set by automated tests to speed up waits.</summary>
        public static float CinematicSpeed = 1f;

        protected virtual void Start()
        {
            StartCoroutine(Run());
        }

        protected abstract IEnumerator Run();

        public virtual void OnPauseChanged(bool paused) { }

        protected IEnumerator Wait(float seconds) => Tween.Wait(seconds / Mathf.Max(0.01f, CinematicSpeed));

        protected void BuildCamera(Color background)
        {
            Cam = CameraController.Create(background);
        }

        protected void BuildLevel(string id)
        {
            var data = GameAssets.Level(id);
            Level = LevelInstance.Build(data, null, Cam);
            Cam.SetBounds(data.XMin, data.XMax);
            Cam.SetBaseView(data.CameraY, data.CameraSize);
            Cam.SetBackground(new Color(data.BgR, data.BgG, data.BgB));
        }

        protected PlayerController2D SpawnPlayer(float x, bool reflection, Color? tint = null)
        {
            Player = PlayerController2D.Spawn(new Vector3(x, Level.Data.GroundY, 0f), reflection, Level.Data.GroundY);
            if (tint.HasValue) Player.Rig.SetTint(tint.Value);
            Interactions = Player.gameObject.AddComponent<InteractionSystem>();
            Interactions.Init(Player);
            Cam.Follow(Player.transform);
            return Player;
        }

        /// <summary>Speaks a line as a subtitle and waits for it to be read.</summary>
        protected IEnumerator Say(string line, float extra = 0f)
        {
            float d = UIManager.ReadingTime(line) + extra;
            UI.Caption(line, d);
            yield return Wait(d + 0.25f);
        }
    }
}

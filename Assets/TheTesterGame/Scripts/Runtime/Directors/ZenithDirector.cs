using System.Collections;
using TheTester.Core;
using UnityEngine;

namespace TheTester
{
    /// <summary>
    /// FINAL LEVEL — Zenith Studio, painted after the studio's own concept art: a fixed, theatrical view of the
    /// lobby. The camera opens on the glowing wall sign and pulls back to reveal the room while Jean Paul walks
    /// in from behind the crates; the awards wait on two pedestals by the lounge.
    /// </summary>
    public sealed class ZenithDirector : DirectorBase
    {
        private AwardsSequenceController _awards;
        private Interactable _awardsSpot;
        private SpriteRenderer _halo;
        public bool Finished { get; private set; }
        public AwardsSequenceController Awards => _awards;
        public override bool AllowPause => !Finished && (_awards == null || !_awards.Running);

        protected override IEnumerator Run()
        {
            UI.SetFadeInstant(1f);
#if UNITY_EDITOR
            if (Progress.Chapter < Chapter.ZenithStudio)
            {
                Progress.ResetStory();
                Progress.BeginShowroom();
                Progress.CompleteTest(TestId.Exterior);
                Progress.CompleteTest(TestId.Interior);
                Progress.EnterDrive();
                Progress.CompleteTest(TestId.Drive);
            }
#endif
            // (re)entering the studio always starts the ceremony from the beginning
            if (Progress.Chapter >= Chapter.ZenithStudio) Progress.NormalizeForContinue();
            BuildCamera(UIStyle.Midnight);
            BuildLevel("zenith");
            SpawnPlayer(Level.MarkerX("spawn"), false, new Color(0.9f, 0.96f, 0.98f));
            Player.Face(-1f, true);
            _awards = gameObject.AddComponent<AwardsSequenceController>();
            _awards.Init(this);
            _halo = Level.Get("sign_halo");
            CreateInteractables();
            UI.SetHudVisible(false);
            UI.SetTouchMode(TouchLayout.None);
            Audio.PlayAmbience("amb_studio", 2f, 0.6f);
            Audio.PlayMusic("music_title", 3f, 0.4f);
            UI.SetLetterbox(1f, 0f);

            // the reveal: start on the glowing "Zenith Studio" sign (it is the location title)...
            var sign = Level.Marker("reveal");
            Cam.Cut(new Vector2(sign.X, sign.Y), 0.95f);
            yield return UI.FadeIn(2.0f);
            yield return Wait(2.2f);
            // ...then pull back to the whole studio while he walks in
            StartCoroutine(Cam.MoveTo(new Vector2(0f, Level.Data.CameraY), Level.Data.CameraSize, 5.0f / Mathf.Max(0.01f, CinematicSpeed), true));
            yield return Wait(1.6f);
            yield return Player.WalkTo(Level.MarkerX("entry"), 0.9f);
            UI.SetLetterbox(0f, 1.0f);
            UI.SetHudVisible(true);
            UI.SetTests(Progress);
            UI.SetObjective(Lines.ObjAwardsArea);
            UI.SetTouchMode(TouchLayout.Walk);
            Player.InputEnabled = true;
        }

        private void CreateInteractables()
        {
            foreach (var id in new[] { "storyboard", "sign", "desk", "reels" })
            {
                var m = Level.Marker(id);
                if (m == null) continue;
                string key = id;
                var it = Interactable.Create(id, m.X, Level.Data.GroundY, Lines.PromptObserve, m.Radius, () => Observe(key));
                it.PromptHeight = 2.9f;
            }
            var a = Level.Marker("awards");
            _awardsSpot = Interactable.Create("awards", a.X, Level.Data.GroundY, Lines.PromptAward, a.Radius + 0.6f, ReceiveAward);
            _awardsSpot.PromptHeight = 3.1f;
        }

        private IEnumerator Observe(string id)
        {
            var m = Level.Marker(id);
            Player.Face(Mathf.Sign(m.X - Player.transform.position.x + 0.0001f));
            StartCoroutine(Player.Act("skeptical", 0.25f));
            yield return Say(Lines.Observations[id]);
        }

        /// <summary>The wall sign's back-light breathes, very slowly.</summary>
        private void Update()
        {
            if (_halo == null) return;
            var c = _halo.color;
            c.a = 0.72f + 0.16f * Mathf.Sin(Time.time * 0.9f);
            _halo.color = c;
        }

        private IEnumerator ReceiveAward()
        {
            UI.SetObjective(_awards.Received == 0 ? Lines.ObjAward1 : Lines.ObjAward2);
            yield return _awards.ReceiveNext();
            if (_awards.Received == 1)
            {
                _awardsSpot.Prompt = Lines.PromptAward2;
                UI.SetObjective(Lines.ObjAward2);
                yield break;
            }
            if (_awards.Received >= 2)
            {
                _awardsSpot.Available = false;
                Player.InputEnabled = false;
                yield return _awards.Finale(new Vector2(0f, 220f));
                Finished = true;
                UI.OnEndPlayAgain -= PlayAgain;
                UI.OnEndMenu -= ToMenu;
                UI.OnEndPlayAgain += PlayAgain;
                UI.OnEndMenu += ToMenu;
                while (true) yield return null;   // keep the interaction locked; the end screen drives the flow
            }
        }

        private void PlayAgain() => GameManager.I.NewGame();
        private void ToMenu() => GameManager.I.ToMenu();

        private void OnDestroy()
        {
            if (UI == null) return;
            UI.OnEndPlayAgain -= PlayAgain;
            UI.OnEndMenu -= ToMenu;
        }
    }
}

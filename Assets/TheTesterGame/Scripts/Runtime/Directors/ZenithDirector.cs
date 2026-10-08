using System.Collections;
using TheTester.Core;
using UnityEngine;

namespace TheTester
{
    /// <summary>FINAL LEVEL — Zenith Studio: a cinematic production studio, the reveal of the awards and the ending.</summary>
    public sealed class ZenithDirector : DirectorBase
    {
        private AwardsSequenceController _awards;
        private Interactable _awardsSpot;
        private bool _revealed;
        private float _revealX;
        public bool Finished { get; private set; }
        public AwardsSequenceController Awards => _awards;

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
            if (Progress.Chapter == Chapter.Completed) Progress.NormalizeForContinue();
            BuildCamera(UIStyle.Midnight);
            BuildLevel("zenith");
            float spawn = Level.MarkerX("spawn");
            SpawnPlayer(spawn - 2.6f, true, new Color(0.9f, 0.93f, 1f));
            Player.Face(1f, true);
            _awards = gameObject.AddComponent<AwardsSequenceController>();
            _awards.Init(this);
            _revealX = Level.MarkerX("reveal");
            CreateInteractables();
            UI.SetHudVisible(true);
            UI.SetTests(Progress);
            UI.SetObjective(Lines.ObjAwardsArea);
            UI.SetTouchMode(TouchLayout.Walk);
            Audio.PlayAmbience("amb_studio", 2f, 0.6f);
            UI.SetLetterbox(1f, 0f);
            StartCoroutine(UI.FadeIn(1.6f));
            yield return Player.WalkTo(spawn + 0.8f, 0.9f);
            yield return UI.TitleCard(Lines.LocationZenith, null, 1.5f, 44, true);
            UI.SetLetterbox(0f, 1.0f);
            Player.InputEnabled = true;
        }

        private void CreateInteractables()
        {
            foreach (var id in new[] { "desk", "storyboard", "poster_tester", "camera" })
            {
                var m = Level.Marker(id);
                if (m == null) continue;
                string key = id;
                var it = Interactable.Create(id, m.X, Level.Data.GroundY, Lines.PromptObserve, m.Radius, () => Observe(key));
                it.PromptHeight = 3.0f;
            }
            var a = Level.Marker("awards");
            _awardsSpot = Interactable.Create("awards", a.X, Level.Data.GroundY, Lines.PromptAward, a.Radius + 0.6f, ReceiveAward);
            _awardsSpot.PromptHeight = 3.3f;
        }

        private IEnumerator Observe(string id)
        {
            var m = Level.Marker(id);
            Player.Face(Mathf.Sign(m.X - Player.transform.position.x + 0.0001f));
            StartCoroutine(Player.Act("skeptical", 0.25f));
            yield return Say(Lines.Observations[id]);
        }

        private void Update()
        {
            if (Player == null || _revealed) return;
            if (Player.transform.position.x > _revealX)
            {
                _revealed = true;
                StartCoroutine(Reveal());
            }
        }

        /// <summary>The camera slowly widens and slides toward the two pedestals.</summary>
        private IEnumerator Reveal()
        {
            Audio.PlayMusic("music_title", 4f, 0.3f);
            float from = Cam.TargetOffsetX;
            yield return Tween.Run(3.5f, k =>
            {
                Cam.TargetOffsetX = Mathf.Lerp(from, 2.2f, k);
                Cam.Zoom(Mathf.Lerp(Cam.BaseSize, 5.9f, k));
                Cam.SetVerticalOffset(Mathf.Lerp(0f, 0.45f, k));
            }, Ease.InOutSine);
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

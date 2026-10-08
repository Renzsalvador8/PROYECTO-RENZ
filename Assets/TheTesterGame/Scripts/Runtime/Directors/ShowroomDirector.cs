using System.Collections;
using TheTester.Core;
using UnityEngine;

namespace TheTester
{
    /// <summary>
    /// LEVEL 01 + 02 — the Hyundai showroom: the arrival, the exterior inspection (station 01), the interior
    /// detail test (station 02), optional deadpan observations, and the door to the test drive.
    /// </summary>
    public sealed class ShowroomDirector : DirectorBase
    {
        private static readonly Vector2 ExteriorStage = new Vector2(0f, 150f);
        private static readonly Vector2 InteriorStage = new Vector2(0f, 300f);
        private static readonly Vector2 ArrivalStage = new Vector2(-200f, 0f);
        private Interactable _station1, _station2, _exit;
        public bool StationRunning { get; private set; }

        protected override IEnumerator Run()
        {
            UI.SetFadeInstant(1f);
            BuildCamera(UIStyle.Midnight);
            BuildLevel("showroom");
            Audio.PlayAmbience("amb_showroom", 2f, 0.55f);

            if (Progress.Chapter == Chapter.NewGame)
            {
                yield return Arrival();
                Progress.BeginShowroom();
                GameManager.I.Save();
            }
            if (Progress.Chapter > Chapter.DriveReady && Progress.Chapter < Chapter.TestDrive) Progress.BeginShowroom();

            float spawn = Level.MarkerX("spawn");
            if (Progress.Chapter == Chapter.InteriorTest) spawn = Level.MarkerX("station1") + 3.5f;
            if (Progress.Chapter >= Chapter.DriveReady) spawn = Level.MarkerX("station2") + 3.5f;
            SpawnPlayer(spawn, true);
            Player.Face(1f, true);
            CreateInteractables();

            UI.SetHudVisible(true);
            UI.SetTests(Progress);
            UpdateObjective();
            UI.SetTouchMode(TouchLayout.Walk);
            Audio.PlayMusic("music_title", 3f, 0.16f);
            yield return UI.FadeIn(1.4f);
            StartCoroutine(UI.TitleCard(Lines.LocationShowroom, null, 1.6f, 40, true));
            Player.InputEnabled = true;
        }

        // ------------------------------------------------------------------ opening: the arrival
        private Transform _arrivalRoot;
        private bool _arrivalDone;

        /// <summary>Plays the arrival; Space/Enter/E (or the touch button) skips it after a moment.</summary>
        private IEnumerator Arrival()
        {
            _arrivalDone = false;
            var seq = StartCoroutine(ArrivalSequence());
            float t = 0f;
            while (!_arrivalDone)
            {
                t += Time.deltaTime;
                if (t > 1.5f && (GameInput.ActionDown || GameInput.InteractDown) && !GameManager.I.Paused)
                {
                    StopCoroutine(seq);
                    UI.HideCaption();
                    yield return UI.FadeOut(0.6f);
                    break;
                }
                yield return null;
            }
            UI.SetLetterbox(0f, 0f);
            if (_arrivalRoot != null) Destroy(_arrivalRoot.gameObject);
        }

        private IEnumerator ArrivalSequence()
        {
            var root = new GameObject("Arrival").transform;
            _arrivalRoot = root;
            var bg = new GameObject("Exterior").AddComponent<SpriteRenderer>();
            bg.transform.SetParent(root, false);
            bg.transform.position = ArrivalStage;
            bg.sprite = GameAssets.Sprite("Art/Showroom/exterior_day", 100f, new Vector2(0.5f, 0.5f));
            bg.sortingOrder = -200;
            float ground = ArrivalStage.y + (540f - 860f) / 100f;
            var walker = PlayerController2D.Spawn(new Vector3(ArrivalStage.x - 10.6f, ground, 0f), false, ground);
            walker.transform.SetParent(root, true);
            walker.transform.localScale = Vector3.one * 0.82f;
            walker.Face(1f, true);
            Cam.Cut(ArrivalStage + new Vector2(0.4f, 0f), 5.4f);
            UI.SetLetterbox(1f, 0f);
            Audio.PlayMusic("music_title", 2f, 0.45f);
            yield return UI.FadeIn(2.0f);

            walker.StartCoroutine(walker.WalkTo(ArrivalStage.x - 3.2f, 0.85f));   // owned by the walker: stops if skipped
            yield return Wait(1.2f);
            yield return Say(Lines.Opening1, 0.6f);
            yield return Tween.WaitUntilOrTimeout(() => Mathf.Abs(walker.Velocity) < 0.01f, 8f);
            yield return walker.Act("look_around", 0.3f);
            yield return Say(Lines.Opening2, 0.8f);
            float door = ArrivalStage.x + (1390f - 1024f) / 100f;
            StartCoroutine(Cam.MoveTo(ArrivalStage + new Vector2(1.6f, -0.2f), 4.8f, 3.5f));
            yield return walker.WalkTo(door - 0.2f, 0.85f);
            Audio.Sfx("door_open", 0.3f, 1.4f);
            yield return UI.FadeOut(1.1f);
            _arrivalDone = true;
        }

        // ------------------------------------------------------------------ interactables
        private void CreateInteractables()
        {
            var m1 = Level.Marker("station1");
            _station1 = Interactable.Create("station1", m1.X, Level.Data.GroundY, m1.Prompt, m1.Radius, Station1);
            _station1.PromptHeight = 3.4f;
            var m2 = Level.Marker("station2");
            _station2 = Interactable.Create("station2", m2.X, Level.Data.GroundY, m2.Prompt, m2.Radius, Station2);
            _station2.PromptHeight = 3.4f;
            _exit = Interactable.Create("exit", Level.MarkerX("exit"), Level.Data.GroundY, Lines.PromptDrive, 2.2f, ExitDoor);
            _exit.PromptHeight = 3.9f;
            foreach (var id in new[] { "coffee", "reception", "brochure", "bronze_car" })
            {
                var m = Level.Marker(id);
                if (m == null) continue;
                string key = id;
                var it = Interactable.Create(id, m.X, Level.Data.GroundY, Lines.PromptObserve, m.Radius, () => Observe(key));
                it.PromptHeight = 3.0f;
            }
        }

        private void UpdateObjective()
        {
            switch (Progress.Chapter)
            {
                case Chapter.ExteriorTest: UI.SetObjective(Lines.ObjExterior); break;
                case Chapter.InteriorTest: UI.SetObjective(Lines.ObjInterior); break;
                default: UI.SetObjective(Lines.ObjToDrive); break;
            }
            UI.SetTests(Progress);
        }

        private IEnumerator Observe(string id)
        {
            var m = Level.Marker(id);
            Player.Face(Mathf.Sign(m.X - Player.transform.position.x + 0.0001f));
            Progress.SeenObservations.Add(id);
            StartCoroutine(Player.Act(id == "bronze_car" || id == "brochure" ? "skeptical" : "impressed", 0.25f));
            yield return Say(Lines.Observations[id]);
        }

        // ------------------------------------------------------------------ station 01 · exterior
        private IEnumerator Station1()
        {
            if (Progress.IsDone(TestId.Exterior))
            {
                yield return Say("Ya lo inspeccioné. Cinco veces.");
                yield break;
            }
            StationRunning = true;
            var m = Level.Marker("station1");
            yield return Player.WalkTo(m.X);
            Player.Face(1f);
            yield return Wait(0.3f);
            Player.SetProp("prop_f", "magnifier");
            yield return Player.Act("magnifier_raise", 0.2f);
            Player.Hold("examine");
            Audio.DuckMusic(0.3f, 1f);
            yield return Wait(0.9f);
            yield return UI.FadeOut(0.7f);
            UI.SetHudVisible(false);
            yield return ExteriorInspection.Run(this, ExteriorStage);

            // back in the showroom: close on the critic
            var head = Player.BonePosition("head");
            Cam.Cut(new Vector2(head.x + 0.4f, head.y - 0.6f), 2.3f);
            UI.SetLetterbox(1f, 0f);
            UI.SetTouchMode(TouchLayout.None);
            yield return UI.FadeIn(0.9f);
            yield return Wait(0.6f);
            yield return Player.Act("magnifier_lower", 0.25f);
            yield return Wait(1.1f);
            Player.Hold("idle");
            Audio.DuckMusic(0f, 0.8f);
            yield return Wait(0.9f);
            StartCoroutine(Player.Act("mustache_adjust", 0.3f));
            yield return Wait(0.9f);
            UI.Caption(Lines.ExteriorVerdict, 2.4f);
            yield return Wait(2.6f);
            yield return Wait(0.8f);      // the pause
            Progress.CompleteTest(TestId.Exterior);
            GameManager.I.Save();
            UI.PulseTest(0);
            Audio.Sfx("ui_confirm", 0.4f);
            UI.SetLetterbox(0f, 1.2f);
            yield return Cam.MoveTo(new Vector2(Player.transform.position.x + 1.2f, Cam.BaseY), Cam.BaseSize, 1.6f, true);
            Audio.DuckMusic(1f, 2f);
            Player.Release();
            UI.SetHudVisible(true);
            UI.SetTouchMode(TouchLayout.Walk);
            UpdateObjective();
            StationRunning = false;
        }

        // ------------------------------------------------------------------ station 02 · interior
        private IEnumerator Station2()
        {
            if (!Progress.IsDone(TestId.Exterior))
            {
                StartCoroutine(Player.Act("skeptical", 0.25f));
                yield return Say(Lines.GateInteriorFirst);
                yield break;
            }
            if (Progress.IsDone(TestId.Interior))
            {
                yield return Say("El interior ya fue examinado. Detalladamente.");
                yield break;
            }
            StationRunning = true;
            var m = Level.Marker("station2");
            yield return Player.WalkTo(m.X);
            Player.Face(1f);
            Audio.Sfx("cloth_1", 0.4f);
            Player.SetProp("prop_f", "magnifier");
            yield return Player.Act("magnifier_raise", 0.2f);
            Player.Hold("examine");
            Audio.DuckMusic(0.3f, 1f);
            yield return UI.FadeOut(0.7f);
            UI.SetHudVisible(false);
            yield return DetailTest.Run(this, InteriorStage);

            // he steps back out holding a much larger magnifier
            Player.SetProp("prop_f", "magnifier_big");
            Player.Hold("examine", 0f);
            var head = Player.BonePosition("head");
            Cam.Cut(new Vector2(head.x + 0.6f, head.y - 0.5f), 2.5f);
            UI.SetLetterbox(1f, 0f);
            UI.SetTouchMode(TouchLayout.None);
            yield return UI.FadeIn(0.9f);
            yield return Wait(1.6f);
            yield return Player.Act("magnifier_lower", 0.25f);
            Player.SetProp("prop_f", "magnifier");
            yield return Player.Act("skeptical", 0.25f);
            Progress.CompleteTest(TestId.Interior);
            GameManager.I.Save();
            UI.PulseTest(1);
            Audio.Sfx("ui_confirm", 0.4f);
            UI.SetLetterbox(0f, 1.2f);
            yield return Cam.MoveTo(new Vector2(Player.transform.position.x + 1.2f, Cam.BaseY), Cam.BaseSize, 1.6f, true);
            Audio.DuckMusic(1f, 2f);
            Player.Release();
            UI.SetHudVisible(true);
            UI.SetTouchMode(TouchLayout.Walk);
            UpdateObjective();
            StationRunning = false;
        }

        // ------------------------------------------------------------------ exit to the test drive
        private IEnumerator ExitDoor()
        {
            if (!Progress.IsDone(TestId.Interior))
            {
                StartCoroutine(Player.Act("skeptical", 0.25f));
                yield return Say(Lines.GateDriveFirst);
                yield break;
            }
            yield return Player.WalkTo(Level.MarkerX("exit"));
            Player.Face(1f);
            Audio.Sfx("door_open", 0.4f, 0.9f);
            Progress.EnterDrive();
            GameManager.I.Save();
            Player.InputEnabled = false;
            UI.SetHudVisible(false);
            Audio.StopMusic(1f);
            GameManager.I.GoTo(GameScene.TestDrive);
            yield return Wait(5f);
        }
    }
}

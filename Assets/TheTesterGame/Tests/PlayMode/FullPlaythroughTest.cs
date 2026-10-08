using System;
using System.Collections;
using NUnit.Framework;
using TheTester.Core;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.TestTools;

namespace TheTester.Tests
{
    /// <summary>
    /// Plays the whole game through simulated input — menu, arrival, both inspections, the test drive and the
    /// awards — and checks the end screen appears without errors. Run from Window ▸ General ▸ Test Runner ▸ PlayMode.
    /// The four scenes must be in Build Settings (The Tester ▸ Configurar proyecto does it).
    /// </summary>
    public class FullPlaythroughTest
    {
        private InputSimulation _sim;

        [SetUp]
        public void SetUp()
        {
            SaveManager.ClearProgress();
            _sim = new InputSimulation();
            GameManager.TimeScaleWhenRunning = 3f;
            DirectorBase.CinematicSpeed = 1f;
        }

        [TearDown]
        public void TearDown()
        {
            GameInput.Simulation = null;
            GameManager.TimeScaleWhenRunning = 1f;
            Time.timeScale = 1f;
        }

        private static IEnumerator WaitFor(Func<bool> condition, float timeoutSeconds, string what)
        {
            float t = 0f;
            while (!condition())
            {
                if (t > timeoutSeconds) Assert.Fail("Timed out waiting for: " + what);
                yield return null;
                t += Time.unscaledDeltaTime;
            }
        }

        private static T Director<T>() where T : DirectorBase => GameManager.I != null ? GameManager.I.Director as T : null;

        private IEnumerator WalkTo(DirectorBase d, float x)
        {
            float t = 0f;
            while (Mathf.Abs(d.Player.transform.position.x - x) > 0.25f)
            {
                _sim.MoveX = Mathf.Sign(x - d.Player.transform.position.x);
                if (t > 60f) Assert.Fail("Could not walk to x=" + x);
                yield return null;
                t += Time.unscaledDeltaTime;
            }
            _sim.MoveX = 0f;
            yield return new WaitForSeconds(0.2f);
        }

        private IEnumerator Interact(DirectorBase d, string id)
        {
            yield return WaitFor(() => d.Interactions.Current != null && d.Interactions.Current.Id == id, 10f, "prompt for " + id);
            Assert.IsTrue(UIManager.I.PromptVisible, "prompt visible for " + id);
            _sim.PressInteract();
            yield return null;
        }

        private void PointAt(Vector2 world)
        {
            var cam = GameManager.I.Director.Cam;
            _sim.PointerOverride = true;
            _sim.Pointer = cam.Cam.WorldToScreenPoint(world);
            _sim.PointerHeld = false;
        }

        [UnityTest, Timeout(900000)]
        public IEnumerator CompleteGameFromMenuToEndScreen()
        {
            SceneManager.LoadScene("00_MainMenu");
            yield return WaitFor(() => Director<MainMenuDirector>() != null, 20f, "main menu");
            yield return new WaitForSeconds(1f);
            GameInput.Simulation = _sim;
            GameManager.I.NewGame();

            // ---- showroom: arrival → control
            yield return WaitFor(() => Director<ShowroomDirector>() != null, 30f, "showroom scene");
            var show = Director<ShowroomDirector>();
            yield return WaitFor(() => show.Player != null && show.Player.InputEnabled, 90f, "control after the arrival");
            Assert.AreEqual(Chapter.ExteriorTest, GameManager.I.Progress.Chapter);

            // ---- test 01: exterior
            yield return WalkTo(show, show.Level.MarkerX("station1"));
            yield return Interact(show, "station1");
            ExteriorInspection ext = null;
            yield return WaitFor(() => (ext = UnityEngine.Object.FindAnyObjectByType<ExteriorInspection>()) != null && ext.Session != null, 30f, "exterior inspection");
            foreach (var id in Lines.ExteriorOrder)
            {
                PointAt(ext.WorldOf(id));
                var target = ext.Session.Find(id);
                yield return WaitFor(() => target.Done, 15f, "inspect " + id);
            }
            _sim.PointerOverride = false;
            yield return WaitFor(() => GameManager.I.Progress.IsDone(TestId.Exterior) && !show.StationRunning, 60f, "exterior completed");

            // ---- test 02: interior
            yield return WalkTo(show, show.Level.MarkerX("station2"));
            yield return Interact(show, "station2");
            DetailTest det = null;
            yield return WaitFor(() => (det = UnityEngine.Object.FindAnyObjectByType<DetailTest>()) != null && det.Puzzle != null, 30f, "detail test");
            yield return new WaitForSeconds(1f);
            foreach (var id in Lines.InteriorOrder)
            {
                PointAt(det.WorldOf(id));
                yield return new WaitForSeconds(0.4f);
                _sim.Click();
                var spot = det.Puzzle.Find(id);
                yield return WaitFor(() => spot.Found, 5f, "find " + id);
                yield return new WaitForSeconds(0.5f);
            }
            _sim.PointerOverride = false;
            yield return WaitFor(() => GameManager.I.Progress.IsDone(TestId.Interior) && !show.StationRunning, 60f, "interior completed");

            // ---- to the test drive
            yield return WalkTo(show, show.Level.MarkerX("exit"));
            yield return Interact(show, "exit");
            yield return WaitFor(() => Director<DriveDirector>() != null, 30f, "drive scene");
            var drive = Director<DriveDirector>();
            yield return WaitFor(() => drive.Car != null && drive.Car.InputEnabled, 30f, "car control");
            drive.Car.Autopilot = new DriveAutopilot();   // a careful driver, same rules as the player
            yield return WaitFor(() => drive.Course.IsParked, 150f, "parking");
            Assert.IsFalse(drive.Course.RanRed, "the careful driver stops at the light");

            // ---- Zenith Studio: awards
            yield return WaitFor(() => Director<ZenithDirector>() != null, 60f, "zenith scene");
            var zen = Director<ZenithDirector>();
            yield return WaitFor(() => zen.Player != null && zen.Player.InputEnabled, 30f, "control in the studio");
            Assert.IsTrue(GameManager.I.Progress.AllTestsDone);
            yield return WalkTo(zen, zen.Level.MarkerX("awards"));
            yield return Interact(zen, "awards");
            yield return WaitFor(() => GameManager.I.Progress.LuxReceived && !zen.Awards.Running, 30f, "Lux Grand Prix");
            yield return WaitFor(() => zen.Player.InputEnabled, 10f, "control after the first award");
            yield return Interact(zen, "awards");
            yield return WaitFor(() => GameManager.I.Progress.EffieReceived, 30f, "Effie Bronze");
            yield return WaitFor(() => UIManager.I.EndVisible, 90f, "end screen");
            Assert.AreEqual(Chapter.Completed, GameManager.I.Progress.Chapter);
        }

        [UnityTest]
        public IEnumerator PauseFreezesTimeAndResumes()
        {
            SceneManager.LoadScene("02_TestDrive");
            yield return WaitFor(() => Director<DriveDirector>() != null, 20f, "drive scene");
            yield return new WaitForSeconds(1f);
            GameManager.I.SetPaused(true);
            Assert.AreEqual(0f, Time.timeScale);
            GameManager.I.SetPaused(false);
            Assert.Greater(Time.timeScale, 0f);
        }
    }
}

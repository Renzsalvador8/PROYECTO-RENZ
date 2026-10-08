using System.Collections;
using TheTester.Core;
using UnityEngine;

namespace TheTester
{
    /// <summary>
    /// LEVEL 03 — the test drive through a Quito-inspired city: traffic light, a van blocking the lane,
    /// a school zone and a precision parking box. Ends on a silent close-up of the critic at the wheel.
    /// </summary>
    public sealed class DriveDirector : DirectorBase
    {
        public VehicleDrivingController Car { get; private set; }
        public DriveCourse Course { get; private set; }
        private SpriteRenderer _red, _amber, _green;
        private bool _ending;
        private float _movingTime;
        private bool _startRemark;
        private float _routeStart, _routeEnd;

        protected override IEnumerator Run()
        {
            UI.SetFadeInstant(1f);
#if UNITY_EDITOR
            if (Progress.Chapter < Chapter.TestDrive) EditorPreviewProgress(Chapter.TestDrive);
#endif
            BuildCamera(new Color(0.69f, 0.77f, 0.81f));
            BuildLevel("drive");
            Course = new DriveCourse();
            Course.Configure(Level.Data);
            var props = Level.Layer("props");
            Car = VehicleDrivingController.Create(props, Course, Level.MarkerX("start"));
            Car.NearY = Level.Marker("near_lane").Y;
            Car.FarY = Level.Marker("far_lane").Y;
            Car.CourseEvent += OnCourseEvent;
            Car.LaneRefused += () => UI.Caption(Lines.DriveLaneNeedsSpeed, 2.4f);
            Cam.Follow(Car.transform);
            Cam.FollowDamping = 2.6f;
            Cam.LookAheadSource = () => 2.6f + Car.Model.Speed * 0.22f;
            BuildTrafficLamps();
            _routeStart = Level.MarkerX("start");
            _routeEnd = Level.MarkerX("parking");

            UI.SetHudVisible(true);
            UI.SetTests(Progress);
            UI.SetSpeedVisible(true);
            UI.SetRouteVisible(true);
            UI.SetObjective(Course.Objective);
            UI.SetTouchMode(TouchLayout.Drive);
            Audio.PlayAmbience("amb_city", 2f, 0.5f);
            Audio.PlayMusic("music_drive", 3f, 0.32f);
            Car.StartAudio();
            Audio.Sfx("door_close", 0.6f);
            UI.SetLetterbox(1f, 0f);
            yield return UI.FadeIn(1.4f);
            yield return UI.TitleCard(Lines.LocationDrive, null, 1.4f, 40, true);
            UI.SetLetterbox(0f, 1.0f);
            UI.Caption(GameInput.TouchMode ? Lines.DriveControlsTouch : Lines.DriveControls, 5f);
            Car.InputEnabled = true;
        }

#if UNITY_EDITOR
        /// <summary>Editor-only convenience when this scene is played directly: pretend earlier tests are done.</summary>
        private void EditorPreviewProgress(Chapter target)
        {
            Progress.ResetStory();
            Progress.BeginShowroom();
            Progress.CompleteTest(TestId.Exterior);
            Progress.CompleteTest(TestId.Interior);
            if (target >= Chapter.TestDrive) Progress.EnterDrive();
        }
#endif

        private void BuildTrafficLamps()
        {
            var tl = Level.Get("traffic_light");
            if (tl == null) return;
            var basePos = tl.transform.position;
            _red = Lamp("Art/Drive/lamp_red", basePos + new Vector3(0f, 7.04f, 0f));
            _amber = Lamp("Art/Drive/lamp_amber", basePos + new Vector3(0f, 6.46f, 0f));
            _green = Lamp("Art/Drive/lamp_green", basePos + new Vector3(0f, 5.88f, 0f));
        }

        private SpriteRenderer Lamp(string sprite, Vector3 pos)
        {
            var go = new GameObject(sprite);
            go.transform.SetParent(Level.Layer("props"), false);
            go.transform.position = pos;
            go.transform.localScale = Vector3.one * 0.62f;
            var sr = go.AddComponent<SpriteRenderer>();
            sr.sprite = GameAssets.Sprite(sprite, 100f, new Vector2(0.5f, 0.5f));
            sr.sortingOrder = -930;
            return sr;
        }

        private void Update()
        {
            if (Car == null || Course == null) return;
            if (_red != null)
            {
                _red.enabled = Course.Light == LightState.Red;
                _amber.enabled = Course.Light == LightState.Amber;
                _green.enabled = Course.Light == LightState.Green;
            }
            UI.SetSpeed(Car.Model.Kmh);
            UI.SetRoute(Mathf.InverseLerp(_routeStart, _routeEnd, Car.Model.X));
            if (!_ending) UI.SetObjective(Course.Objective);
            if (Car.InputEnabled && Car.Model.Speed > 3f)
            {
                _movingTime += Time.deltaTime;
                if (!_startRemark && _movingTime > 3.5f)
                {
                    _startRemark = true;
                    UI.Caption(Lines.DriveStartRemark);
                }
            }
            if (Car.InputEnabled && GameInput.ActionDown && Random.value < 0.4f) UI.Caption(Lines.DriveHorn, 1.8f);
        }

        private void OnCourseEvent(DriveEvent e)
        {
            switch (e)
            {
                case DriveEvent.LightAmber: Audio.Sfx("traffic_beep", 0.4f); break;
                case DriveEvent.LightRed: Audio.Sfx("traffic_beep", 0.4f, 0.8f); break;
                case DriveEvent.LightGreen: Audio.Sfx("traffic_beep", 0.4f, 1.25f); break;
                case DriveEvent.StoppedAtLight: UI.Caption(Lines.DriveStopped); break;
                case DriveEvent.RanRedLight: UI.Caption(Lines.DriveRanRed); break;
                case DriveEvent.TooFarFromLine: UI.Caption(Lines.DriveTooFar); break;
                case DriveEvent.ObstacleAhead: UI.Caption(Lines.DriveObstacle); break;
                case DriveEvent.AutoBrake: UI.Caption(Lines.DriveAutoBrake); Cam.Shake(0.04f); break;
                case DriveEvent.PassedObstacle: UI.Caption(Lines.DrivePassed); break;
                case DriveEvent.EnteredSchoolZone: UI.Caption(Lines.DriveSchool); break;
                case DriveEvent.SpeedingInSchoolZone: UI.Caption(Lines.DriveSpeeding); break;
                case DriveEvent.LeftSchoolZone: UI.Caption(Lines.DriveQuiet); break;
                case DriveEvent.ApproachingParking: UI.Caption(Lines.DriveParkingAhead); break;
                case DriveEvent.ReachedBarrier: if (string.IsNullOrEmpty(UI.CurrentCaption)) UI.Caption(Lines.DriveBarrier, 3f); break;
                case DriveEvent.Parked: if (!_ending) StartCoroutine(Ending()); break;
            }
        }

        // ------------------------------------------------------------------ the silent close-up
        private IEnumerator Ending()
        {
            _ending = true;
            Car.InputEnabled = false;
            Car.Autopilot = null;
            float score = Course.Score();
            int cm = Course.ParkingCentimetres;
            Progress.RecordDrive(score, cm);
            UI.SetObjective(Lines.DriveObjectiveDone);
            UI.Caption(string.Format(Lines.DriveParkedFormat, cm), 2.6f);
            Audio.StopMusic(2.5f);
            Audio.SetLoop("motor", 0.05f, 0.6f);
            yield return Wait(2.8f);
            UI.Caption(string.Format(Lines.DriveScoreFormat, score.ToString("0.0", System.Globalization.CultureInfo.InvariantCulture).Replace('.', ',')), 2.6f);
            yield return Wait(2.8f);
            Car.StopAudio();
            UI.SetHudVisible(false);
            UI.SetSpeedVisible(false);
            UI.SetRouteVisible(false);
            UI.SetTouchMode(TouchLayout.None);
            UI.SetLetterbox(1f, 1.2f);
            var head = Car.DriverHead;
            yield return Cam.MoveTo(new Vector2(head.x + 0.35f, head.y - 0.35f), 1.25f, 2.2f);
            yield return Wait(1.6f);                                  // he remains silent
            yield return Car.DriverAnim.PlayAndWait("sit_stache", 0.3f);
            Car.DriverAnim.Play("sit_drive", 0.4f);
            yield return Wait(0.8f);
            var front = GameAssets.Rig("tester_front");
            Car.Driver.SetHidden(true, "brow", "stache");
            Car.Driver.SetSlotSprite("head", GameAssets.RigSprite(front, "head_neutral"));   // looks toward the camera
            Audio.Sfx("cloth_1", 0.3f);
            yield return Wait(1.5f);
            Car.Driver.SetSlotSprite("head", GameAssets.RigSprite(front, "head_brow_one"));
            yield return Wait(1.1f);
            Car.Driver.SetSlotSprite("head", GameAssets.RigSprite(front, "head_smile"));   // reluctant approval
            Audio.Sfx("stache", 0.4f);
            yield return Wait(1.3f);
            Audio.PlayMusic("sting_complete", 0.2f, 0.7f, false);
            Progress.CompleteTest(TestId.Drive);
            GameManager.I.Save();
            yield return UI.TitleCard(Lines.TestsCompleted, null, 2.2f, 76);
            GameManager.I.GoTo(GameScene.ZenithStudio);
        }
    }
}

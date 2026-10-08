using System;
using System.Collections.Generic;
using System.IO;
using NUnit.Framework;
using TheTester.Core;

namespace TheTester.Tests
{
    /// <summary>Locates the Unity project root both inside the Unity Test Runner and in the dotnet harness.</summary>
    internal static class ProjectFiles
    {
        private static string _root;

        public static string Root
        {
            get
            {
                if (_root != null) return _root;
                foreach (var start in new[] { Directory.GetCurrentDirectory(), AppContext.BaseDirectory })
                {
                    var d = new DirectoryInfo(start);
                    while (d != null)
                    {
                        if (Directory.Exists(Path.Combine(d.FullName, "Assets", "TheTesterGame"))) return _root = d.FullName;
                        d = d.Parent;
                    }
                }
                throw new DirectoryNotFoundException("Could not find the Unity project root (Assets/TheTesterGame)");
            }
        }

        public static string Game(string rel) => Path.Combine(Root, "Assets", "TheTesterGame", rel);
        public static JsonNode Json(string rel) => JsonNode.Parse(File.ReadAllText(Game(rel)));
        public static JsonNode Data(string name) => Json(Path.Combine("Data", "Resources", "Data", name + ".json"));
    }

    public class JsonTests
    {
        [Test]
        public void ParsesNestedStructures()
        {
            var j = JsonNode.Parse("{\"a\": [1, 2.5, -3e2], \"b\": {\"c\": \"x\\u00e9\\n\"}, \"t\": true, \"n\": null}");
            Assert.AreEqual(3, j["a"].Count);
            Assert.AreEqual(2.5f, j["a"][1].AsFloat(), 1e-6f);
            Assert.AreEqual(-300f, j["a"][2].AsFloat(), 1e-6f);
            Assert.AreEqual("xé\n", j["b"]["c"].AsString());
            Assert.IsTrue(j["t"].AsBool());
            Assert.IsTrue(j["n"].IsNull);
            Assert.IsTrue(j["missing"].IsNull);
            Assert.AreEqual(7f, j.GetFloat("missing", 7f));
        }

        [Test]
        public void RoundTripsThroughToString()
        {
            var src = "{\"name\":\"Tester\",\"list\":[1,2,3],\"nested\":{\"ok\":false}}";
            var again = JsonNode.Parse(JsonNode.Parse(src).ToString());
            Assert.AreEqual("Tester", again.GetString("name"));
            Assert.AreEqual(3, again["list"].Count);
            Assert.IsFalse(again["nested"].GetBool("ok", true));
        }

        [Test]
        public void RejectsMalformedJson()
        {
            Assert.Throws<FormatException>(() => JsonNode.Parse("{\"a\": }"));
            Assert.Throws<FormatException>(() => JsonNode.Parse("[1, 2"));
            Assert.Throws<FormatException>(() => JsonNode.Parse("{} trailing"));
        }
    }

    public class RigAndClipTests
    {
        private static RigData Rig() => RigData.FromJson(ProjectFiles.Data("Rigs/tester_side"));
        private static Dictionary<string, RigClip> Clips() =>
            RigClip.LibraryFromJson(ProjectFiles.Json(Path.Combine("Animations", "Resources", "Animations", "tester_clips.json")));

        [Test]
        public void SideRigIsWellFormed()
        {
            var rig = Rig();
            Assert.Greater(rig.Bones.Count, 15);
            Assert.Greater(rig.Slots.Count, 15);
            Assert.AreEqual(-1, rig.Bones[0].ParentIndex);
            foreach (var s in rig.Slots)
            {
                Assert.GreaterOrEqual(s.BoneIndex, 0, s.Name);
                if (!string.IsNullOrEmpty(s.Sprite)) Assert.IsTrue(rig.Sprites.ContainsKey(s.Sprite), s.Name + " -> " + s.Sprite);
            }
            Assert.IsTrue(rig.Sprites.ContainsKey("magnifier"));
            Assert.IsTrue(rig.Sprites.ContainsKey("magnifier_big"));
            Assert.IsTrue(rig.Slots[rig.SlotIndex("prop_f")].HiddenByDefault);
        }

        [Test]
        public void FrontRigHasAllExpressions()
        {
            var rig = RigData.FromJson(ProjectFiles.Data("Rigs/tester_front"));
            foreach (var e in new[] { "neutral", "brow_one", "brows_up", "smile", "smile_brow", "look_l", "look_r", "look_dl", "look_dr", "frown", "blink" })
                Assert.IsTrue(rig.Sprites.ContainsKey("head_" + e), e);
            Assert.IsTrue(rig.Sprites.ContainsKey("body"));
        }

        [Test]
        public void EveryClipTargetsExistingBonesOrSlots()
        {
            var rig = Rig();
            var clips = Clips();
            foreach (var name in new[] { "walk", "idle", "magnifier_raise", "examine", "magnifier_lower", "look_around", "skeptical",
                                         "mustache_adjust", "disappointed", "impressed", "receive", "hold" })
                Assert.IsTrue(clips.ContainsKey(name), "missing clip " + name);
            foreach (var clip in clips.Values)
            {
                foreach (var c in clip.Curves)
                {
                    if (c.IsSlot) Assert.GreaterOrEqual(rig.SlotIndex(c.SlotName), 0, clip.Name + ": " + c.Target);
                    else Assert.GreaterOrEqual(rig.BoneIndex(c.Target), 0, clip.Name + ": " + c.Target);
                    for (int i = 1; i < c.Times.Length; i++) Assert.GreaterOrEqual(c.Times[i], c.Times[i - 1], clip.Name + " keys sorted");
                }
            }
            Assert.Greater(clips["walk"].Speed, 0.5f);
            Assert.IsTrue(clips["walk"].Loop);
        }

        // Reference values computed by Tools/ArtPipeline/rigtools.py (the art-side preview implementation).
        private static readonly object[] Parity =
        {
            new object[] { "walk", "thigh_f", "rot", 0.137f, 15.215623f },
            new object[] { "walk", "knee_b", "rot", 0.9f, -4.310293f },
            new object[] { "walk", "hip", "y", 0.33f, 0.038840f },
            new object[] { "walk", "shoulder_b", "rot", 1.05f, 9.510894f },
            new object[] { "mustache_adjust", "wrist_f", "rot", 1.23f, 14.303074f },
            new object[] { "magnifier_raise", "shoulder_f", "rot", 0.5f, 3.480604f },
            new object[] { "idle", "torso", "sy", 3.9f, 1.000443f },
            new object[] { "idle", "stache", "rot", 3.55f, 2.437499f },
            new object[] { "skeptical", "brow", "y", 2.0f, 0.007556f },
            new object[] { "examine", "elbow_f", "rot", 0.05f, 103.068940f },
        };

        [TestCaseSource(nameof(Parity))]
        public void CurveEvaluationMatchesArtPipeline(string clipName, string target, string prop, float t, float expected)
        {
            var clip = Clips()[clipName];
            var p = RigCurve.ParseProp(prop);
            var curve = clip.Curves.Find(c => c.Target == target && c.Prop == p);
            Assert.IsNotNull(curve);
            Assert.AreEqual(expected, curve.Evaluate(t, clip.Loop, clip.Length), 2e-3f);
        }

        [Test]
        public void LoopingCurvesAreContinuousAtTheSeam()
        {
            foreach (var clip in Clips().Values)
            {
                if (!clip.Loop) continue;
                foreach (var c in clip.Curves)
                {
                    float a = c.Evaluate(clip.Length - 1e-4f, true, clip.Length);
                    float b = c.Evaluate(1e-4f, true, clip.Length);
                    Assert.AreEqual(a, b, c.Prop == PoseProp.Rot ? 0.2f : 0.01f, clip.Name + "/" + c.Target + "/" + c.Prop);
                }
            }
        }

        [Test]
        public void BoundClipWritesPoseAndBlendingIsLinear()
        {
            var rig = Rig();
            var clips = Clips();
            var a = new PoseBuffer(rig.Bones.Count, rig.Slots.Count);
            var b = new PoseBuffer(rig.Bones.Count, rig.Slots.Count);
            a.Reset(rig); b.Reset(rig);
            new BoundClip(clips["magnifier_raise"], rig).Evaluate(0.9f, b);
            int prop = rig.SlotIndex("prop_f");
            Assert.AreEqual(0f, a.Visible[prop]);
            Assert.AreEqual(1f, b.Visible[prop]);
            int sh = rig.BoneIndex("shoulder_f");
            float target = b.Rot[sh];
            a.BlendTowards(b, 0.5f);
            Assert.AreEqual(target * 0.5f, a.Rot[sh], 1e-4f);
        }
    }

    public class LevelDataTests
    {
        [TestCase("showroom", new[] { "spawn", "station1", "station2", "exit", "coffee", "reception", "brochure", "bronze_car" })]
        [TestCase("drive", new[] { "start", "stop_line", "traffic_light", "obstacle", "school_start", "school_end", "parking", "far_lane", "near_lane" })]
        [TestCase("zenith", new[] { "spawn", "entry", "reveal", "awards", "award_lux", "award_effie", "storyboard", "sign", "desk", "reels" })]
        public void LevelsLoadWithRequiredMarkers(string id, string[] markers)
        {
            var level = LevelData.FromJson(ProjectFiles.Data("Levels/" + id));
            Assert.AreEqual(id, level.Id);
            Assert.Less(level.XMin, level.XMax);
            Assert.GreaterOrEqual(level.Layers.Count, 3);
            foreach (var m in markers) Assert.IsNotNull(level.FindMarker(m), id + " missing marker " + m);
        }

        [TestCase("showroom")]
        [TestCase("drive")]
        [TestCase("zenith")]
        public void EveryReferencedSpriteExistsOnDisk(string id)
        {
            var level = LevelData.FromJson(ProjectFiles.Data("Levels/" + id));
            foreach (var layer in level.Layers)
                foreach (var it in layer.Items)
                {
                    Assert.IsTrue(it.Sprite.StartsWith("Art/"), it.Sprite);
                    var file = ProjectFiles.Game(Path.Combine("Art", "Resources", it.Sprite + ".png"));
                    Assert.IsTrue(File.Exists(file), "missing " + file);
                    Assert.Greater(it.Ppu, 0f);
                }
        }

        [Test]
        public void InspectionDataIsConsistent()
        {
            var car = ProjectFiles.Data("Vehicles/ioniq5");
            foreach (var id in Lines.ExteriorOrder)
            {
                Assert.IsTrue(car["inspectionHotspots"].Has(id), id);
                Assert.IsTrue(Lines.ExteriorLabels.ContainsKey(id) && Lines.ExteriorNotes.ContainsKey(id), id);
            }
            var interior = ProjectFiles.Data("Inspection/interior");
            foreach (var id in Lines.InteriorOrder)
            {
                Assert.IsTrue(interior["targets"].Has(id), id);
                Assert.IsTrue(Lines.InteriorClues.ContainsKey(id) && Lines.InteriorFound.ContainsKey(id), id);
                Assert.IsTrue(File.Exists(ProjectFiles.Game("Art/Resources/Art/Inspection/clue_" + id + ".png")), id);
            }
            foreach (var key in interior["decoys"].Keys)
                Assert.IsTrue(Lines.InteriorDecoys.ContainsKey(key), "no line for decoy " + key);
        }
    }

    public class ProgressTests
    {
        [Test]
        public void TestsMustBeCompletedInOrder()
        {
            var p = new GameProgress();
            Assert.IsFalse(p.CompleteTest(TestId.Exterior), "story not started");
            p.BeginShowroom();
            Assert.AreEqual(Chapter.ExteriorTest, p.Chapter);
            Assert.IsFalse(p.CompleteTest(TestId.Interior));
            Assert.IsFalse(p.CompleteTest(TestId.Drive));
            Assert.IsTrue(p.CompleteTest(TestId.Exterior));
            Assert.AreEqual(Chapter.InteriorTest, p.Chapter);
            Assert.IsTrue(p.CompleteTest(TestId.Interior));
            Assert.AreEqual(Chapter.DriveReady, p.Chapter);
            p.EnterDrive();
            Assert.AreEqual(Chapter.TestDrive, p.Chapter);
            Assert.IsTrue(p.CompleteTest(TestId.Drive));
            Assert.AreEqual(Chapter.ZenithStudio, p.Chapter);
            Assert.IsTrue(p.AllTestsDone);
        }

        [Test]
        public void AwardsAreGivenLuxThenEffieOnlyAfterAllTests()
        {
            var p = new GameProgress();
            Assert.IsFalse(p.ReceiveNextAward(out _));
            p.BeginShowroom();
            p.CompleteTest(TestId.Exterior); p.CompleteTest(TestId.Interior); p.EnterDrive(); p.CompleteTest(TestId.Drive);
            Assert.IsTrue(p.ReceiveNextAward(out var first));
            Assert.AreEqual("lux", first);
            Assert.IsTrue(p.ReceiveNextAward(out var second));
            Assert.AreEqual("effie", second);
            Assert.IsFalse(p.ReceiveNextAward(out _));
            p.Finish();
            Assert.AreEqual(Chapter.Completed, p.Chapter);
            Assert.AreEqual(1, p.Playthroughs);
        }

        [Test]
        public void SerializationRoundTripsAndRepairs()
        {
            var p = new GameProgress();
            p.BeginShowroom(); p.CompleteTest(TestId.Exterior);
            p.SeenObservations.Add("coffee");
            p.RecordDrive(9.4f, 12);
            var q = GameProgress.Deserialize(p.Serialize());
            Assert.AreEqual(Chapter.InteriorTest, q.Chapter);
            Assert.IsTrue(q.IsDone(TestId.Exterior));
            Assert.IsFalse(q.IsDone(TestId.Interior));
            Assert.IsTrue(q.SeenObservations.Contains("coffee"));
            Assert.AreEqual(9.4f, q.DriveScore, 1e-4f);
            Assert.AreEqual(12, q.ParkingCm);

            var repaired = GameProgress.Deserialize("ch=5;t=000;");
            Assert.IsTrue(repaired.AllTestsDone);
            Assert.AreEqual(Chapter.NewGame, GameProgress.Deserialize("garbage;ch=xx;").Chapter);
            Assert.AreEqual(Chapter.NewGame, GameProgress.Deserialize(null).Chapter);
        }

        [Test]
        public void ResetStoryKeepsPlaythroughCount()
        {
            var p = new GameProgress();
            p.BeginShowroom(); p.CompleteTest(TestId.Exterior); p.CompleteTest(TestId.Interior); p.EnterDrive(); p.CompleteTest(TestId.Drive);
            p.ReceiveNextAward(out _); p.ReceiveNextAward(out _); p.Finish();
            p.ResetStory();
            Assert.AreEqual(Chapter.NewGame, p.Chapter);
            Assert.AreEqual(0, p.TestsCompleted);
            Assert.AreEqual(1, p.Playthroughs);
        }
    }

    public class InspectionTests
    {
        [Test]
        public void DwellCompletesTargetsAndDecaysWhenLeaving()
        {
            var s = new InspectionSession { DwellTime = 1f, Decay = 0.5f };
            s.Add("a", new Vec2(0, 0), 0.5f);
            s.Add("b", new Vec2(5, 0), 0.5f);
            var completed = new List<string>();
            bool all = false;
            s.TargetCompleted += t => completed.Add(t.Id);
            s.AllCompleted += () => all = true;

            for (int i = 0; i < 6; i++) s.Update(0.1f, new Vec2(0.1f, 0f));
            Assert.AreEqual(0.6f, s.Find("a").Progress, 1e-4f);
            for (int i = 0; i < 4; i++) s.Update(0.1f, new Vec2(20f, 0f));
            Assert.AreEqual(0.4f, s.Find("a").Progress, 1e-4f, "decays when the lens leaves");
            for (int i = 0; i < 7; i++) s.Update(0.1f, new Vec2(0f, 0f));
            CollectionAssert.AreEqual(new[] { "a" }, completed);
            for (int i = 0; i < 12; i++) s.Update(0.1f, new Vec2(5f, 0.2f));
            CollectionAssert.AreEqual(new[] { "a", "b" }, completed);
            Assert.IsTrue(all);
            Assert.IsTrue(s.IsComplete);
        }

        [Test]
        public void InactiveLensDoesNotInspect()
        {
            var s = new InspectionSession { DwellTime = 0.5f };
            s.Add("a", new Vec2(0, 0), 1f);
            for (int i = 0; i < 20; i++) s.Update(0.1f, new Vec2(0, 0), lensActive: false);
            Assert.IsFalse(s.Find("a").Done);
        }

        [Test]
        public void PuzzleDistinguishesTargetsDecoysAndMisses()
        {
            var p = new DetailPuzzle { ClickCooldown = 0f };
            p.AddTarget("dots", new Vec2(0, 0), 0.5f);
            p.AddTarget("clock", new Vec2(4, 0), 0.5f);
            p.AddDecoy("cupholder", new Vec2(0.6f, 0), 0.8f);
            Assert.AreEqual(DetailPuzzle.ResultKind.Nothing, p.Click(new Vec2(10, 10)).Kind);
            Assert.AreEqual(DetailPuzzle.ResultKind.Decoy, p.Click(new Vec2(1.2f, 0)).Kind);
            var r = p.Click(new Vec2(0.2f, 0));
            Assert.AreEqual(DetailPuzzle.ResultKind.Found, r.Kind, "targets win when overlapping a decoy");
            Assert.AreEqual("dots", r.Id);
            Assert.AreEqual(DetailPuzzle.ResultKind.AlreadyFound, p.Click(new Vec2(0, 0)).Kind);
            Assert.IsFalse(p.IsComplete);
            Assert.AreEqual(DetailPuzzle.ResultKind.Found, p.Click(new Vec2(4, 0.1f)).Kind);
            Assert.IsTrue(p.IsComplete);
            Assert.AreEqual(2, p.Misses);
        }

        [Test]
        public void PuzzleCooldownPreventsSpamClicking()
        {
            var p = new DetailPuzzle { ClickCooldown = 0.3f };
            p.AddTarget("dots", new Vec2(0, 0), 0.5f);
            p.Click(new Vec2(9, 9));
            Assert.AreEqual(DetailPuzzle.ResultKind.Cooldown, p.Click(new Vec2(0, 0)).Kind);
            p.Tick(0.31f);
            Assert.AreEqual(DetailPuzzle.ResultKind.Found, p.Click(new Vec2(0, 0)).Kind);
        }
    }

    public class DrivingTests
    {
        private const float Dt = 1f / 60f;

        [Test]
        public void AcceleratesToTopSpeedAndBrakesToStop()
        {
            var car = new VehicleModel();
            for (int i = 0; i < 60 * 20; i++) car.Step(Dt, true, false);
            Assert.AreEqual(car.MaxSpeed, car.Speed, 0.05f);
            for (int i = 0; i < 60 * 6; i++) car.Step(Dt, false, true);
            Assert.AreEqual(0f, car.Speed, 1e-3f, "holding the brake after stopping must not reverse");
            Assert.IsFalse(car.Reversing);
        }

        [Test]
        public void NeverPassesTheStopLimitEvenAtFullThrottle()
        {
            var car = new VehicleModel();
            car.Teleport(0f, 0);
            for (int i = 0; i < 60 * 30; i++)
            {
                car.Step(Dt, true, false, 120f);
                Assert.LessOrEqual(car.Front, 120f + 1e-3f);
            }
            Assert.AreEqual(0f, car.Speed, 1e-3f);
            Assert.AreEqual(120f, car.Front, 0.5f);
        }

        [Test]
        public void PressingBrakeAgainAtStandstillReverses()
        {
            var car = new VehicleModel();
            car.Teleport(10f, 0);
            car.Step(Dt, false, false);
            for (int i = 0; i < 60 * 2; i++) car.Step(Dt, false, true);
            Assert.IsTrue(car.Reversing);
            Assert.Less(car.Speed, -1f);
            Assert.Less(car.X, 10f);
            for (int i = 0; i < 60 * 2; i++) car.Step(Dt, false, false);
            Assert.AreEqual(0f, car.Speed, 1e-3f);
        }

        [Test]
        public void LaneChangeNeedsMotionAndCompletes()
        {
            var car = new VehicleModel();
            Assert.IsFalse(car.RequestLane(1), "cannot strafe while stopped");
            for (int i = 0; i < 60; i++) car.Step(Dt, true, false);
            Assert.IsTrue(car.RequestLane(1));
            for (int i = 0; i < 90; i++) car.Step(Dt, true, false);
            Assert.AreEqual(1f, car.LaneT, 1e-3f);
            Assert.IsTrue(car.InFarLane);
        }

        [Test]
        public void ObstacleForcesStopUnlessTheLaneIsChanged()
        {
            var course = new DriveCourse();
            var car = new VehicleModel();
            car.Teleport(course.ObstacleStart - 60f, 0);
            for (int i = 0; i < 60 * 20; i++)
            {
                car.Step(Dt, true, false, course.StopLimit(car));
                course.Update(Dt, car);
            }
            Assert.LessOrEqual(car.Front, course.ObstacleStart);
            Assert.IsTrue(course.UsedAutoBrake);
            car.RequestLane(1);   // speed is ~0 so this is refused
            Assert.AreEqual(0, car.Lane);
        }

        [Test]
        public void CarefulDriverCompletesTheCourseInAboutAMinute()
        {
            var level = LevelData.FromJson(ProjectFiles.Data("Levels/drive"));
            var course = new DriveCourse();
            course.Configure(level);
            var car = new VehicleModel();
            car.Teleport(level.MarkerX("start"), 0);
            var pilot = new DriveAutopilot();
            var seen = new HashSet<DriveEvent>();
            float t = 0f;
            while (!course.IsParked && t < 180f)
            {
                var c = pilot.Decide(car, course);
                if (c.RequestLane >= 0) car.RequestLane(c.RequestLane);
                car.Step(Dt, c.Throttle, c.Brake, course.StopLimit(car));
                foreach (var e in course.Update(Dt, car)) seen.Add(e);
                t += Dt;
            }
            TestContext.WriteLine("drive completed in " + t.ToString("0.0") + " s, score " + course.Score() + ", parking " + course.ParkingCentimetres + " cm");
            Assert.IsTrue(course.IsParked, "parked (t=" + t + ", x=" + car.X + ")");
            Assert.IsTrue(course.StoppedCorrectly, "stopped at the light");
            Assert.IsFalse(course.RanRed);
            Assert.IsFalse(course.UsedAutoBrake, "changed lane before the van");
            Assert.IsFalse(course.SpedInSchool);
            Assert.That(t, Is.InRange(40f, 80f), "drive duration " + t);
            Assert.GreaterOrEqual(course.Score(), 9f);
            foreach (var e in new[] { DriveEvent.LightAmber, DriveEvent.LightRed, DriveEvent.StoppedAtLight, DriveEvent.ObstacleAhead,
                                      DriveEvent.PassedObstacle, DriveEvent.EnteredSchoolZone, DriveEvent.LeftSchoolZone, DriveEvent.Parked })
                Assert.IsTrue(seen.Contains(e), "missing event " + e);
        }

        [Test]
        public void RecklessDriverStillCannotCrashAndIsPenalised()
        {
            var course = new DriveCourse();
            var car = new VehicleModel();
            float t = 0f;
            // full throttle, never changes lane: must end stopped behind the van without passing it
            while (t < 60f)
            {
                car.Step(Dt, true, false, course.StopLimit(car));
                course.Update(Dt, car);
                t += Dt;
            }
            Assert.IsTrue(course.RanRed);
            Assert.LessOrEqual(car.Front, course.ObstacleStart);
            Assert.Less(course.Score(), 9f);
        }
    }
}

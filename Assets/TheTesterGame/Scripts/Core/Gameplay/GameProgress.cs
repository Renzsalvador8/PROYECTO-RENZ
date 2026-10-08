using System;
using System.Collections.Generic;
using System.Text;

namespace TheTester.Core
{
    /// <summary>Checkpoints of the story, in order.</summary>
    public enum Chapter
    {
        NewGame = 0,          // opening (arrival) not seen yet
        ExteriorTest = 1,     // in the showroom, exterior inspection pending
        InteriorTest = 2,     // exterior done, interior pending
        DriveReady = 3,       // interior done, walk to the garage
        TestDrive = 4,        // driving sequence
        ZenithStudio = 5,     // awards finale
        Completed = 6,
    }

    public enum TestId { Exterior = 0, Interior = 1, Drive = 2 }

    /// <summary>
    /// The whole save state. Plain data + rules so it can be tested without Unity.
    /// Serialized as a compact "key=value;" string stored by SaveManager (PlayerPrefs).
    /// </summary>
    public sealed class GameProgress
    {
        public Chapter Chapter { get; private set; } = Chapter.NewGame;
        private readonly bool[] _tests = new bool[3];
        public bool LuxReceived { get; private set; }
        public bool EffieReceived { get; private set; }
        public float DriveScore { get; private set; } = -1f;
        public int ParkingCm { get; private set; } = -1;
        public int Playthroughs { get; private set; }
        public readonly HashSet<string> SeenObservations = new HashSet<string>();

        public event Action<Chapter> ChapterChanged;

        public bool IsDone(TestId t) => _tests[(int)t];
        public int TestsCompleted => (_tests[0] ? 1 : 0) + (_tests[1] ? 1 : 0) + (_tests[2] ? 1 : 0);
        public bool AllTestsDone => TestsCompleted == 3;
        public bool BothAwards => LuxReceived && EffieReceived;

        public void BeginShowroom()
        {
            if (Chapter < Chapter.ExteriorTest) SetChapter(Chapter.ExteriorTest);
        }

        public bool CompleteTest(TestId t)
        {
            switch (t)
            {
                case TestId.Exterior:
                    if (Chapter < Chapter.ExteriorTest) return false;
                    break;
                case TestId.Interior:
                    if (!_tests[(int)TestId.Exterior]) return false;
                    break;
                case TestId.Drive:
                    if (!_tests[(int)TestId.Interior]) return false;
                    break;
            }
            if (_tests[(int)t]) return true;
            _tests[(int)t] = true;
            switch (t)
            {
                case TestId.Exterior: SetChapter(Chapter.InteriorTest); break;
                case TestId.Interior: SetChapter(Chapter.DriveReady); break;
                case TestId.Drive: SetChapter(Chapter.ZenithStudio); break;
            }
            return true;
        }

        public void EnterDrive()
        {
            if (_tests[(int)TestId.Interior] && Chapter < Chapter.TestDrive) SetChapter(Chapter.TestDrive);
        }

        public void RecordDrive(float score, int parkingCm)
        {
            DriveScore = score;
            ParkingCm = parkingCm;
        }

        /// <summary>Awards are given in order: Lux Grand Prix first, then Effie Bronze.</summary>
        public bool ReceiveNextAward(out string awardId)
        {
            awardId = null;
            if (!AllTestsDone || Chapter < Chapter.ZenithStudio) return false;
            if (!LuxReceived) { LuxReceived = true; awardId = "lux"; return true; }
            if (!EffieReceived) { EffieReceived = true; awardId = "effie"; return true; }
            return false;
        }

        public void Finish()
        {
            if (BothAwards)
            {
                SetChapter(Chapter.Completed);
                Playthroughs++;
            }
        }

        /// <summary>Restart the story but keep the play counter (used by "Jugar de nuevo").</summary>
        public void ResetStory()
        {
            Array.Clear(_tests, 0, _tests.Length);
            LuxReceived = EffieReceived = false;
            DriveScore = -1f;
            ParkingCm = -1;
            SeenObservations.Clear();
            SetChapter(Chapter.NewGame);
        }

        /// <summary>Continue from a checkpoint: the awards are re-run if the game was quit mid-ceremony.</summary>
        public void NormalizeForContinue()
        {
            if (Chapter == Chapter.ZenithStudio && !BothAwards)
            {
                LuxReceived = EffieReceived = false;
            }
            if (Chapter == Chapter.Completed)
            {
                // finished games continue at the finale
                LuxReceived = EffieReceived = false;
                Chapter = Chapter.ZenithStudio;
            }
        }

        private void SetChapter(Chapter c)
        {
            if (Chapter == c) return;
            Chapter = c;
            ChapterChanged?.Invoke(c);
        }

        // ------------------------------------------------------------------ persistence
        public string Serialize()
        {
            var sb = new StringBuilder();
            sb.Append("v=1;");
            sb.Append("ch=").Append((int)Chapter).Append(';');
            sb.Append("t=").Append(_tests[0] ? 1 : 0).Append(_tests[1] ? 1 : 0).Append(_tests[2] ? 1 : 0).Append(';');
            sb.Append("aw=").Append(LuxReceived ? 1 : 0).Append(EffieReceived ? 1 : 0).Append(';');
            sb.Append("ds=").Append(DriveScore.ToString(System.Globalization.CultureInfo.InvariantCulture)).Append(';');
            sb.Append("pk=").Append(ParkingCm).Append(';');
            sb.Append("pl=").Append(Playthroughs).Append(';');
            sb.Append("seen=").Append(string.Join(",", SeenObservations)).Append(';');
            return sb.ToString();
        }

        public static GameProgress Deserialize(string s)
        {
            var p = new GameProgress();
            if (string.IsNullOrEmpty(s)) return p;
            try
            {
                foreach (var part in s.Split(new[] { ';' }, StringSplitOptions.RemoveEmptyEntries))
                {
                    int eq = part.IndexOf('=');
                    if (eq <= 0) continue;
                    string k = part.Substring(0, eq), v = part.Substring(eq + 1);
                    switch (k)
                    {
                        case "ch":
                            int ch = int.Parse(v);
                            if (ch >= (int)Chapter.NewGame && ch <= (int)Chapter.Completed) p.Chapter = (Chapter)ch;
                            break;
                        case "t":
                            for (int i = 0; i < 3 && i < v.Length; i++) p._tests[i] = v[i] == '1';
                            break;
                        case "aw":
                            if (v.Length >= 2) { p.LuxReceived = v[0] == '1'; p.EffieReceived = v[1] == '1'; }
                            break;
                        case "ds":
                            p.DriveScore = float.Parse(v, System.Globalization.CultureInfo.InvariantCulture);
                            break;
                        case "pk": p.ParkingCm = int.Parse(v); break;
                        case "pl": p.Playthroughs = int.Parse(v); break;
                        case "seen":
                            foreach (var id in v.Split(new[] { ',' }, StringSplitOptions.RemoveEmptyEntries)) p.SeenObservations.Add(id);
                            break;
                    }
                }
            }
            catch (FormatException)
            {
                return new GameProgress();
            }
            catch (OverflowException)
            {
                return new GameProgress();
            }
            // repair inconsistent saves: chapters imply completed tests
            if (p.Chapter >= Chapter.InteriorTest) p._tests[0] = true;
            if (p.Chapter >= Chapter.DriveReady) p._tests[1] = true;
            if (p.Chapter >= Chapter.ZenithStudio) p._tests[2] = true;
            return p;
        }
    }
}

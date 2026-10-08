using System;
using System.Collections.Generic;

namespace TheTester.Core
{
    public enum CurveInterp { Smooth, Linear, Step }

    public enum PoseProp { Rot, X, Y, ScaleX, ScaleY, Visible, Alpha }

    /// <summary>One animated channel. Matches Tools/ArtPipeline/rigtools.py eval_curve exactly.</summary>
    public sealed class RigCurve
    {
        public string Target;      // bone name, or "slot:<name>"
        public PoseProp Prop;
        public CurveInterp Interp;
        public float[] Times;
        public float[] Values;

        public bool IsSlot => Target.StartsWith("slot:", StringComparison.Ordinal);
        public string SlotName => IsSlot ? Target.Substring(5) : null;

        public float Evaluate(float t, bool loop, float length)
        {
            int n = Times.Length;
            if (n == 0) return 0f;
            if (n == 1) return Values[0];
            if (loop) t = Mod(t, length);
            if (!loop)
            {
                if (t <= Times[0]) return Values[0];
                if (t >= Times[n - 1]) return Values[n - 1];
            }
            int i = 0;
            while (i < n - 1 && Times[i + 1] <= t) i++;
            float t0, v0, t1, v1;
            bool wrapBefore = loop && t < Times[0];
            if (wrapBefore)
            {
                t0 = Times[n - 1] - length; v0 = Values[n - 1];
                t1 = Times[0]; v1 = Values[0];
                i = -1;
            }
            else if (i >= n - 1)
            {
                t0 = Times[n - 1]; v0 = Values[n - 1];
                t1 = Times[0] + length; v1 = Values[0];
            }
            else
            {
                t0 = Times[i]; v0 = Values[i];
                t1 = Times[i + 1]; v1 = Values[i + 1];
            }
            float dt = Math.Max(t1 - t0, 1e-6f);
            float u = (t - t0) / dt;
            if (Interp == CurveInterp.Step) return v0;
            if (Interp == CurveInterp.Linear) return v0 + (v1 - v0) * u;

            KeyAt(i < 0 ? -2 : i - 1, loop, length, out float km1t, out float km1v);
            KeyAt(i < 0 ? 1 : i + 2, loop, length, out float k2t, out float k2v);
            float m0 = (loop || i > 0) ? (v1 - km1v) / Math.Max(t1 - km1t, 1e-6f) : (v1 - v0) / dt;
            float m1 = (loop || i + 2 <= n - 1) ? (k2v - v0) / Math.Max(k2t - t0, 1e-6f) : (v1 - v0) / dt;
            float u2 = u * u, u3 = u2 * u;
            float h00 = 2 * u3 - 3 * u2 + 1;
            float h10 = u3 - 2 * u2 + u;
            float h01 = -2 * u3 + 3 * u2;
            float h11 = u3 - u2;
            return h00 * v0 + h10 * dt * m0 + h01 * v1 + h11 * dt * m1;
        }

        private void KeyAt(int j, bool loop, float length, out float t, out float v)
        {
            int n = Times.Length;
            if (loop)
            {
                int q = (int)Math.Floor((double)j / n);
                int r = j - q * n;
                t = Times[r] + q * length;
                v = Values[r];
                return;
            }
            j = Math.Min(Math.Max(j, 0), n - 1);
            t = Times[j];
            v = Values[j];
        }

        private static float Mod(float a, float m) => m <= 0 ? 0 : a - m * (float)Math.Floor(a / m);

        public static PoseProp ParseProp(string p)
        {
            switch (p)
            {
                case "rot": return PoseProp.Rot;
                case "x": return PoseProp.X;
                case "y": return PoseProp.Y;
                case "sx": return PoseProp.ScaleX;
                case "sy": return PoseProp.ScaleY;
                case "visible": return PoseProp.Visible;
                case "alpha": return PoseProp.Alpha;
                default: throw new FormatException("Unknown pose property '" + p + "'");
            }
        }
    }

    public sealed class RigClip
    {
        public struct ClipEvent
        {
            public float Time;
            public string Name;
        }

        public string Name;
        public float Length;
        public bool Loop;
        public float Speed;            // world units per second covered at 1x (walk cycles)
        public readonly List<RigCurve> Curves = new List<RigCurve>();
        public readonly List<ClipEvent> Events = new List<ClipEvent>();

        public static RigClip FromJson(JsonNode j)
        {
            var clip = new RigClip
            {
                Name = j.GetString("name"),
                Length = Math.Max(0.0001f, j.GetFloat("length", 1f)),
                Loop = j.GetBool("loop"),
                Speed = j.GetFloat("speed", 0f),
            };
            foreach (var c in j["curves"].Items)
            {
                var keys = c["keys"].Items;
                var curve = new RigCurve
                {
                    Target = c.GetString("target"),
                    Prop = RigCurve.ParseProp(c.GetString("prop")),
                    Interp = ParseInterp(c.GetString("interp", "smooth")),
                    Times = new float[keys.Count],
                    Values = new float[keys.Count],
                };
                for (int i = 0; i < keys.Count; i++)
                {
                    curve.Times[i] = keys[i][0].AsFloat();
                    curve.Values[i] = keys[i][1].AsFloat();
                }
                clip.Curves.Add(curve);
            }
            foreach (var e in j["events"].Items)
                clip.Events.Add(new ClipEvent { Time = e.GetFloat("t"), Name = e.GetString("name") });
            clip.Events.Sort((a, b) => a.Time.CompareTo(b.Time));
            return clip;
        }

        private static CurveInterp ParseInterp(string s)
        {
            switch (s)
            {
                case "linear": return CurveInterp.Linear;
                case "step": return CurveInterp.Step;
                default: return CurveInterp.Smooth;
            }
        }

        public static Dictionary<string, RigClip> LibraryFromJson(JsonNode root)
        {
            var lib = new Dictionary<string, RigClip>();
            foreach (var c in root["clips"].Items)
            {
                var clip = FromJson(c);
                lib[clip.Name] = clip;
            }
            return lib;
        }
    }

    /// <summary>Flat pose buffer: per-bone transform offsets and per-slot visibility/alpha.</summary>
    public sealed class PoseBuffer
    {
        public readonly float[] Rot, X, Y, SX, SY;
        public readonly float[] Visible, Alpha;

        public PoseBuffer(int bones, int slots)
        {
            Rot = new float[bones]; X = new float[bones]; Y = new float[bones];
            SX = new float[bones]; SY = new float[bones];
            Visible = new float[slots]; Alpha = new float[slots];
        }

        public void Reset(RigData rig)
        {
            for (int i = 0; i < Rot.Length; i++) { Rot[i] = 0; X[i] = 0; Y[i] = 0; SX[i] = 1; SY[i] = 1; }
            for (int i = 0; i < Visible.Length; i++)
            {
                Visible[i] = rig != null && rig.Slots[i].HiddenByDefault ? 0f : 1f;
                Alpha[i] = 1f;
            }
        }

        public void CopyFrom(PoseBuffer o)
        {
            Array.Copy(o.Rot, Rot, Rot.Length); Array.Copy(o.X, X, X.Length); Array.Copy(o.Y, Y, Y.Length);
            Array.Copy(o.SX, SX, SX.Length); Array.Copy(o.SY, SY, SY.Length);
            Array.Copy(o.Visible, Visible, Visible.Length); Array.Copy(o.Alpha, Alpha, Alpha.Length);
        }

        /// <summary>this = lerp(this, other, w)</summary>
        public void BlendTowards(PoseBuffer o, float w)
        {
            for (int i = 0; i < Rot.Length; i++)
            {
                Rot[i] += (o.Rot[i] - Rot[i]) * w;
                X[i] += (o.X[i] - X[i]) * w;
                Y[i] += (o.Y[i] - Y[i]) * w;
                SX[i] += (o.SX[i] - SX[i]) * w;
                SY[i] += (o.SY[i] - SY[i]) * w;
            }
            for (int i = 0; i < Visible.Length; i++)
            {
                Visible[i] += (o.Visible[i] - Visible[i]) * w;
                Alpha[i] += (o.Alpha[i] - Alpha[i]) * w;
            }
        }
    }

    /// <summary>Evaluates a clip into a pose buffer, with curve targets resolved once per rig.</summary>
    public sealed class BoundClip
    {
        public readonly RigClip Clip;
        private readonly int[] _targets;    // bone index or slot index
        private readonly bool[] _isSlot;

        public BoundClip(RigClip clip, RigData rig)
        {
            Clip = clip;
            _targets = new int[clip.Curves.Count];
            _isSlot = new bool[clip.Curves.Count];
            for (int i = 0; i < clip.Curves.Count; i++)
            {
                var c = clip.Curves[i];
                _isSlot[i] = c.IsSlot;
                _targets[i] = c.IsSlot ? rig.SlotIndex(c.SlotName) : rig.BoneIndex(c.Target);
            }
        }

        public void Evaluate(float t, PoseBuffer pose)
        {
            var curves = Clip.Curves;
            for (int i = 0; i < curves.Count; i++)
            {
                int idx = _targets[i];
                if (idx < 0) continue;
                var c = curves[i];
                float v = c.Evaluate(t, Clip.Loop, Clip.Length);
                if (_isSlot[i])
                {
                    if (c.Prop == PoseProp.Visible) pose.Visible[idx] = v;
                    else if (c.Prop == PoseProp.Alpha) pose.Alpha[idx] = v;
                    continue;
                }
                switch (c.Prop)
                {
                    case PoseProp.Rot: pose.Rot[idx] = v; break;
                    case PoseProp.X: pose.X[idx] = v; break;
                    case PoseProp.Y: pose.Y[idx] = v; break;
                    case PoseProp.ScaleX: pose.SX[idx] = v; break;
                    case PoseProp.ScaleY: pose.SY[idx] = v; break;
                }
            }
        }
    }
}

using System;
using System.Collections.Generic;

namespace TheTester.Core
{
    /// <summary>
    /// Exterior inspection rules: the lens must rest over each area for <see cref="DwellTime"/>
    /// seconds. Leaving an area lets its progress decay slowly so the player never loses much.
    /// </summary>
    public sealed class InspectionSession
    {
        public sealed class Target
        {
            public string Id;
            public Vec2 Center;
            public float Radius;
            public float Progress;   // 0..1
            public bool Done;
        }

        public float DwellTime = 1.4f;
        public float Decay = 0.6f;            // progress lost per second when not hovered
        public float LensRadius = 0.6f;       // the lens counts as "over" a target when overlapping it
        public readonly List<Target> Targets = new List<Target>();

        public event Action<Target> TargetCompleted;
        public event Action AllCompleted;

        public Target Hovered { get; private set; }
        public bool IsComplete { get; private set; }
        public int DoneCount { get; private set; }

        public Target Add(string id, Vec2 center, float radius)
        {
            var t = new Target { Id = id, Center = center, Radius = radius };
            Targets.Add(t);
            return t;
        }

        public Target Find(string id)
        {
            foreach (var t in Targets) if (t.Id == id) return t;
            return null;
        }

        /// <summary>Returns the target under the lens (closest centre within reach), or null.</summary>
        public Target Pick(Vec2 lens)
        {
            Target best = null;
            float bestD = float.MaxValue;
            foreach (var t in Targets)
            {
                float d = Vec2.Distance(lens, t.Center);
                float reach = t.Radius + LensRadius * 0.5f;
                if (d <= reach && d < bestD) { best = t; bestD = d; }
            }
            return best;
        }

        public void Update(float dt, Vec2 lens, bool lensActive = true)
        {
            if (IsComplete) return;
            Hovered = lensActive ? Pick(lens) : null;
            foreach (var t in Targets)
            {
                if (t.Done) continue;
                if (t == Hovered)
                {
                    t.Progress = Math.Min(1f, t.Progress + dt / Math.Max(0.01f, DwellTime));
                    if (t.Progress >= 1f)
                    {
                        t.Done = true;
                        DoneCount++;
                        TargetCompleted?.Invoke(t);
                    }
                }
                else
                {
                    t.Progress = Math.Max(0f, t.Progress - dt * Decay);
                }
            }
            if (DoneCount == Targets.Count && Targets.Count > 0)
            {
                IsComplete = true;
                AllCompleted?.Invoke();
            }
        }
    }
}

using System.Collections.Generic;

namespace TheTester.Core
{
    /// <summary>
    /// Interior "detail test": the notebook shows magnified crops of four details; the player has
    /// to find each one in the cabin and click it while the lens is over it. Clicking elsewhere
    /// costs nothing but earns a dry remark (decoys have their own lines).
    /// </summary>
    public sealed class DetailPuzzle
    {
        public enum ResultKind { Found, AlreadyFound, Decoy, Nothing, Cooldown }

        public struct Result
        {
            public ResultKind Kind;
            public string Id;
        }

        public sealed class Spot
        {
            public string Id;
            public Vec2 Center;
            public float Radius;
            public bool IsTarget;
            public bool Found;
        }

        public readonly List<Spot> Spots = new List<Spot>();
        public float ClickCooldown = 0.35f;
        public int Misses { get; private set; }
        public int FoundCount { get; private set; }
        public int TargetCount { get; private set; }
        public bool IsComplete => TargetCount > 0 && FoundCount == TargetCount;
        private float _cooldown;

        public void AddTarget(string id, Vec2 c, float r)
        {
            Spots.Add(new Spot { Id = id, Center = c, Radius = r, IsTarget = true });
            TargetCount++;
        }

        public void AddDecoy(string id, Vec2 c, float r) => Spots.Add(new Spot { Id = id, Center = c, Radius = r });

        public void Tick(float dt)
        {
            if (_cooldown > 0) _cooldown -= dt;
        }

        public Result Click(Vec2 p)
        {
            if (_cooldown > 0) return new Result { Kind = ResultKind.Cooldown };
            _cooldown = ClickCooldown;
            // targets win over decoys when both overlap
            Spot hit = null;
            float best = float.MaxValue;
            foreach (var s in Spots)
            {
                float d = Vec2.Distance(p, s.Center);
                if (d > s.Radius) continue;
                float score = d / s.Radius - (s.IsTarget ? 0.5f : 0f);
                if (score < best) { best = score; hit = s; }
            }
            if (hit == null)
            {
                Misses++;
                return new Result { Kind = ResultKind.Nothing };
            }
            if (!hit.IsTarget)
            {
                Misses++;
                return new Result { Kind = ResultKind.Decoy, Id = hit.Id };
            }
            if (hit.Found) return new Result { Kind = ResultKind.AlreadyFound, Id = hit.Id };
            hit.Found = true;
            FoundCount++;
            return new Result { Kind = ResultKind.Found, Id = hit.Id };
        }

        public Spot Find(string id)
        {
            foreach (var s in Spots) if (s.Id == id) return s;
            return null;
        }
    }
}

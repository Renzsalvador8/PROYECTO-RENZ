using System;

namespace TheTester.Core
{
    /// <summary>Tiny 2D vector so gameplay rules stay independent of UnityEngine.</summary>
    [Serializable]
    public struct Vec2 : IEquatable<Vec2>
    {
        public float X;
        public float Y;

        public Vec2(float x, float y) { X = x; Y = y; }

        public static Vec2 operator +(Vec2 a, Vec2 b) => new Vec2(a.X + b.X, a.Y + b.Y);
        public static Vec2 operator -(Vec2 a, Vec2 b) => new Vec2(a.X - b.X, a.Y - b.Y);
        public static Vec2 operator *(Vec2 a, float k) => new Vec2(a.X * k, a.Y * k);

        public float Length => (float)Math.Sqrt(X * X + Y * Y);
        public static float Distance(Vec2 a, Vec2 b) => (a - b).Length;

        public bool Equals(Vec2 o) => X == o.X && Y == o.Y;
        public override bool Equals(object obj) => obj is Vec2 v && Equals(v);
        public override int GetHashCode() => X.GetHashCode() * 397 ^ Y.GetHashCode();
        public override string ToString() => "(" + X + ", " + Y + ")";
    }

    public static class MathUtil
    {
        public static float Clamp(float v, float lo, float hi) => v < lo ? lo : v > hi ? hi : v;
        public static float Clamp01(float v) => Clamp(v, 0f, 1f);
        public static float Lerp(float a, float b, float t) => a + (b - a) * t;
        public static float MoveTowards(float v, float target, float maxDelta)
        {
            if (Math.Abs(target - v) <= maxDelta) return target;
            return v + Math.Sign(target - v) * maxDelta;
        }
        public static float SmoothStep(float t)
        {
            t = Clamp01(t);
            return t * t * (3f - 2f * t);
        }
        /// <summary>Frame-rate independent exponential approach.</summary>
        public static float Damp(float v, float target, float lambda, float dt) => Lerp(v, target, 1f - (float)Math.Exp(-lambda * dt));
    }
}

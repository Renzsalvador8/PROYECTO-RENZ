using System;
using System.Collections;
using UnityEngine;

namespace TheTester
{
    /// <summary>Easing curves used by every transition in the game (restrained, cinematic timings).</summary>
    public static class Ease
    {
        public static float Linear(float t) => t;
        public static float InOutSine(float t) => -(Mathf.Cos(Mathf.PI * Mathf.Clamp01(t)) - 1f) / 2f;
        public static float OutCubic(float t) { t = 1f - Mathf.Clamp01(t); return 1f - t * t * t; }
        public static float InCubic(float t) { t = Mathf.Clamp01(t); return t * t * t; }
        public static float InOutCubic(float t)
        {
            t = Mathf.Clamp01(t);
            return t < 0.5f ? 4f * t * t * t : 1f - Mathf.Pow(-2f * t + 2f, 3f) / 2f;
        }
        public static float OutBack(float t, float s = 1.4f)
        {
            t = Mathf.Clamp01(t) - 1f;
            return t * t * ((s + 1f) * t + s) + 1f;
        }
    }

    /// <summary>Coroutine helpers. "Unscaled" variants keep running while the game is paused.</summary>
    public static class Tween
    {
        public static IEnumerator Run(float duration, Action<float> step, Func<float, float> ease = null, bool unscaled = false)
        {
            ease = ease ?? Ease.InOutSine;
            float t = 0f;
            if (duration <= 0f)
            {
                step(1f);
                yield break;
            }
            while (t < duration)
            {
                step(ease(t / duration));
                yield return null;
                t += unscaled ? Time.unscaledDeltaTime : Time.deltaTime;
            }
            step(1f);
        }

        public static IEnumerator Wait(float seconds, bool unscaled = false)
        {
            if (unscaled)
            {
                float t = 0f;
                while (t < seconds)
                {
                    yield return null;
                    t += Time.unscaledDeltaTime;
                }
            }
            else
            {
                yield return new WaitForSeconds(seconds);
            }
        }

        public static IEnumerator WaitUntilOrTimeout(Func<bool> condition, float timeout)
        {
            float t = 0f;
            while (!condition() && t < timeout)
            {
                yield return null;
                t += Time.deltaTime;
            }
        }
    }
}

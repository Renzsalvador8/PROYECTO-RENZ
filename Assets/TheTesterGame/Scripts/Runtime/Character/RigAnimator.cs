using System;
using System.Collections;
using System.Collections.Generic;
using TheTester.Core;
using UnityEngine;

namespace TheTester
{
    /// <summary>
    /// Plays authored clips (Animations/tester_clips.json) on a TesterRig with cross-fades.
    /// Non-looping clips hold their last frame. Clip events (footstep, cloth, magnifier…) are raised via OnEvent.
    /// Mirrors (floor reflections) receive the same pose every frame.
    /// </summary>
    [DefaultExecutionOrder(20)]
    public sealed class RigAnimator : MonoBehaviour
    {
        public TesterRig Rig { get; private set; }
        public event Action<string> OnEvent;
        public float Speed = 1f;
        public readonly List<TesterRig> Mirrors = new List<TesterRig>();

        private readonly Dictionary<string, BoundClip> _clips = new Dictionary<string, BoundClip>();
        private BoundClip _cur, _prev;
        private float _curT, _prevT, _fade, _fadeDur;
        private PoseBuffer _a, _b;

        public string Current => _cur != null ? _cur.Clip.Name : "";
        public float CurrentTime => _curT;
        public bool CurrentFinished => _cur != null && !_cur.Clip.Loop && _curT >= _cur.Clip.Length;
        public RigClip CurrentClip => _cur?.Clip;

        public void Init(TesterRig rig)
        {
            Rig = rig;
            foreach (var kv in GameAssets.ClipLibrary) _clips[kv.Key] = new BoundClip(kv.Value, rig.Data);
            _a = new PoseBuffer(rig.Data.Bones.Count, rig.Data.Slots.Count);
            _b = new PoseBuffer(rig.Data.Bones.Count, rig.Data.Slots.Count);
        }

        public bool Has(string clip) => _clips.ContainsKey(clip);

        public float Length(string clip) => _clips.TryGetValue(clip, out var c) ? c.Clip.Length : 0f;

        public void Play(string clip, float fade = 0.2f, bool restart = false)
        {
            if (!_clips.TryGetValue(clip, out var bc))
            {
                Debug.LogWarning("[TheTester] Unknown clip " + clip);
                return;
            }
            if (_cur == bc && !restart) return;
            _prev = _cur;
            _prevT = _curT;
            _cur = bc;
            _curT = 0f;
            _fadeDur = Mathf.Max(0f, fade);
            _fade = _prev == null || _fadeDur <= 0f ? 1f : 0f;
        }

        /// <summary>Plays a one-shot clip and waits for it to finish (then holds its last pose).</summary>
        public IEnumerator PlayAndWait(string clip, float fade = 0.2f)
        {
            Play(clip, fade, true);
            float len = Length(clip);
            float t = 0f;
            while (t < len && Current == clip)
            {
                yield return null;
                t += Time.deltaTime * Speed;
            }
        }

        private void LateUpdate()
        {
            if (Rig == null || _cur == null) return;
            float dt = Time.deltaTime * Speed;
            float before = _curT;
            _curT += dt;
            FireEvents(_cur.Clip, before, _curT);
            if (_prev != null) _prevT += dt;
            if (_fade < 1f) _fade = Mathf.Min(1f, _fade + Time.deltaTime / Mathf.Max(0.0001f, _fadeDur));

            _a.Reset(Rig.Data);
            _cur.Evaluate(_cur.Clip.Loop ? _curT : Mathf.Min(_curT, _cur.Clip.Length), _a);
            if (_prev != null && _fade < 1f)
            {
                _b.Reset(Rig.Data);
                _prev.Evaluate(_prev.Clip.Loop ? _prevT : Mathf.Min(_prevT, _prev.Clip.Length), _b);
                _b.BlendTowards(_a, Ease.InOutSine(_fade));
                Output(_b);
            }
            else
            {
                _prev = null;
                Output(_a);
            }
        }

        private void Output(PoseBuffer p)
        {
            Rig.Pose.CopyFrom(p);
            Rig.Apply(p);
            foreach (var m in Mirrors) if (m != null) m.Apply(p);
        }

        private void FireEvents(RigClip clip, float from, float to)
        {
            if (clip.Events.Count == 0 || OnEvent == null) return;
            if (clip.Loop)
            {
                float L = clip.Length;
                float a = from % L, b = to % L;
                bool wrapped = Mathf.FloorToInt(to / L) != Mathf.FloorToInt(from / L);
                foreach (var e in clip.Events)
                {
                    bool hit = wrapped ? (e.Time > a || e.Time <= b) : (e.Time > a && e.Time <= b);
                    if (hit) OnEvent(e.Name);
                }
            }
            else
            {
                foreach (var e in clip.Events)
                    if (e.Time > from && e.Time <= to) OnEvent(e.Name);
            }
        }
    }
}

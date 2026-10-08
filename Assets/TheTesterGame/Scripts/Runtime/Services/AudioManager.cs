using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace TheTester
{
    /// <summary>Music (cross-faded), ambience (cross-faded), pooled one-shots and named loops (engine/road).</summary>
    public sealed class AudioManager : MonoBehaviour
    {
        public static AudioManager I { get; private set; }

        private AudioSource[] _music;
        private AudioSource[] _amb;
        private int _musicIdx, _ambIdx;
        private readonly List<AudioSource> _pool = new List<AudioSource>();
        private readonly Dictionary<string, AudioSource> _loops = new Dictionary<string, AudioSource>();
        private readonly Dictionary<AudioSource, float> _baseVolume = new Dictionary<AudioSource, float>();
        private float _duck = 1f;
        private Coroutine _duckRoutine;
        private int _step;

        public float MusicVolume { get; private set; }
        public float SfxVolume { get; private set; }
        public float AmbienceVolume { get; private set; }

        private void Awake()
        {
            I = this;
            _music = new[] { NewSource("music_a"), NewSource("music_b") };
            _amb = new[] { NewSource("amb_a"), NewSource("amb_b") };
            for (int i = 0; i < 10; i++) _pool.Add(NewSource("sfx_" + i));
            MusicVolume = SaveManager.MusicVolume;
            SfxVolume = SaveManager.SfxVolume;
            AmbienceVolume = SaveManager.AmbienceVolume;
        }

        private AudioSource NewSource(string n)
        {
            var go = new GameObject(n);
            go.transform.SetParent(transform, false);
            var s = go.AddComponent<AudioSource>();
            s.playOnAwake = false;
            s.spatialBlend = 0f;
            return s;
        }

        public void SetVolumes(float music, float sfx, float amb)
        {
            MusicVolume = Mathf.Clamp01(music);
            SfxVolume = Mathf.Clamp01(sfx);
            AmbienceVolume = Mathf.Clamp01(amb);
            SaveManager.MusicVolume = MusicVolume;
            SaveManager.SfxVolume = SfxVolume;
            SaveManager.AmbienceVolume = AmbienceVolume;
        }

        private void Update()
        {
            foreach (var s in _music) if (_baseVolume.TryGetValue(s, out float v)) s.volume = v * MusicVolume * _duck;
            foreach (var s in _amb) if (_baseVolume.TryGetValue(s, out float v)) s.volume = v * AmbienceVolume;
            foreach (var kv in _loops) if (_baseVolume.TryGetValue(kv.Value, out float v)) kv.Value.volume = v * SfxVolume;
        }

        // ------------------------------------------------------------------ music & ambience
        public void PlayMusic(string clip, float fade = 2f, float volume = 0.7f, bool loop = true)
            => CrossFade(_music, ref _musicIdx, "Music/" + clip, fade, volume, loop);

        public void StopMusic(float fade = 2f) => FadeOutAll(_music, fade);

        public void PlayAmbience(string clip, float fade = 2f, float volume = 0.6f)
            => CrossFade(_amb, ref _ambIdx, "Ambience/" + clip, fade, volume, true);

        public void StopAmbience(float fade = 2f) => FadeOutAll(_amb, fade);

        public bool IsMusicPlaying(string clip)
        {
            var s = _music[_musicIdx];
            return s.isPlaying && s.clip != null && s.clip.name == clip;
        }

        private void CrossFade(AudioSource[] pair, ref int idx, string path, float fade, float volume, bool loop)
        {
            var clip = GameAssets.Audio(path);
            if (clip == null) return;
            var cur = pair[idx];
            if (cur.isPlaying && cur.clip == clip)
            {
                StartCoroutine(FadeBase(cur, volume, fade));
                return;
            }
            idx = 1 - idx;
            var next = pair[idx];
            next.clip = clip;
            next.loop = loop;
            _baseVolume[next] = 0f;
            next.volume = 0f;
            next.Play();
            StartCoroutine(FadeBase(next, volume, fade));
            StartCoroutine(FadeBase(cur, 0f, fade, stopAtEnd: true));
        }

        private void FadeOutAll(AudioSource[] pair, float fade)
        {
            foreach (var s in pair) if (s.isPlaying) StartCoroutine(FadeBase(s, 0f, fade, true));
        }

        private IEnumerator FadeBase(AudioSource s, float target, float time, bool stopAtEnd = false)
        {
            float from = _baseVolume.TryGetValue(s, out float v) ? v : 0f;
            yield return Tween.Run(time, k => _baseVolume[s] = Mathf.Lerp(from, target, k), Ease.Linear, unscaled: true);
            if (stopAtEnd && target <= 0f) s.Stop();
        }

        /// <summary>Temporarily lowers music (deadpan silences, award moments).</summary>
        public void DuckMusic(float level, float time = 1f)
        {
            if (_duckRoutine != null) StopCoroutine(_duckRoutine);
            _duckRoutine = StartCoroutine(Tween.Run(time, k => _duck = Mathf.Lerp(_duck, level, k), Ease.Linear, true));
        }

        // ------------------------------------------------------------------ sfx
        public AudioSource Sfx(string clip, float volume = 1f, float pitch = 1f, float jitter = 0f)
        {
            var c = GameAssets.Audio("Sfx/" + clip);
            if (c == null) return null;
            AudioSource src = null;
            foreach (var s in _pool) if (!s.isPlaying) { src = s; break; }
            if (src == null) src = _pool[0];
            src.clip = c;
            src.loop = false;
            src.pitch = pitch * (1f + Random.Range(-jitter, jitter));
            src.volume = volume * SfxVolume;
            src.Play();
            return src;
        }

        public void Footstep(float volume = 0.55f)
        {
            _step = (_step + 1 + Random.Range(0, 2)) % 4;
            Sfx("footstep_" + (_step + 1), volume, 1f, 0.06f);
        }

        public AudioSource Loop(string key, string clip, float volume)
        {
            if (!_loops.TryGetValue(key, out var s))
            {
                s = NewSource("loop_" + key);
                _loops[key] = s;
            }
            var c = GameAssets.Audio("Sfx/" + clip);
            if (s.clip != c) s.clip = c;
            s.loop = true;
            _baseVolume[s] = volume;
            if (!s.isPlaying && c != null) s.Play();
            return s;
        }

        public void SetLoop(string key, float volume, float pitch)
        {
            if (!_loops.TryGetValue(key, out var s)) return;
            _baseVolume[s] = volume;
            s.pitch = pitch;
        }

        public void StopLoop(string key)
        {
            if (_loops.TryGetValue(key, out var s)) s.Stop();
        }

        public void StopAllLoops()
        {
            foreach (var s in _loops.Values) s.Stop();
        }
    }
}

using System.Collections;
using UnityEngine;

namespace TheTester
{
    /// <summary>
    /// Jean Paul Tester in the side-scrolling scenes: walking with collision (Physics2D box casts against the
    /// level colliders), deliberate turns, idle fidgets, footsteps, a floor reflection, and cutscene helpers.
    /// </summary>
    [DefaultExecutionOrder(10)]
    public sealed class PlayerController2D : MonoBehaviour
    {
        public TesterRig Rig { get; private set; }
        public RigAnimator Anim { get; private set; }
        public TesterRig Reflection { get; private set; }
        public float Facing { get; private set; } = 1f;
        public bool InputEnabled { get; set; }
        public bool Busy { get; private set; }
        public float Velocity => _vel;
        public float WalkSpeed { get; private set; } = 1.4f;
        public float SpeedMultiplier = 1f;

        private float _vel;
        private float? _autoTarget;
        private float _idleTime;
        private float _flipScale = 1f;
        private Coroutine _turn;
        private const float Accel = 7f;
        private static readonly Vector2 BodySize = new Vector2(0.55f, 2.0f);

        public static PlayerController2D Spawn(Vector3 position, bool reflection, float groundY)
        {
            var go = new GameObject("Jean Paul Tester");
            go.transform.position = new Vector3(position.x, groundY, 0f);
            var pc = go.AddComponent<PlayerController2D>();
            pc.Rig = TesterRig.Create("tester_side", go.transform, -50, "Rig");
            pc.Anim = go.AddComponent<RigAnimator>();
            pc.Anim.Init(pc.Rig);
            if (GameAssets.ClipLibrary.TryGetValue("walk", out var walk) && walk.Speed > 0.1f) pc.WalkSpeed = walk.Speed;
            if (reflection)
            {
                pc.Reflection = TesterRig.Create("tester_side", go.transform, -480, "Reflection");
                pc.Reflection.transform.localScale = new Vector3(1f, -0.62f, 1f);
                pc.Reflection.SetTint(new Color(0.55f, 0.65f, 0.75f, 1f));
                pc.Reflection.SetAlpha(0.22f);
                pc.Anim.Mirrors.Add(pc.Reflection);
            }
            pc.Anim.Play("idle", 0f);
            pc.Anim.OnEvent += pc.HandleEvent;
            return pc;
        }

        private void HandleEvent(string e)
        {
            var a = AudioManager.I;
            if (a == null) return;
            switch (e)
            {
                case "footstep": a.Footstep(); break;
                case "cloth": a.Sfx(Random.value < 0.5f ? "cloth_1" : "cloth_2", 0.35f, 1f, 0.08f); break;
                case "magnifier": a.Sfx("magnifier_up", 0.55f); break;
                case "stache": a.Sfx("stache", 0.6f, 1f, 0.1f); break;
                case "sigh": a.Sfx("sigh", 0.5f); break;
                case "flip": Turn(-Facing); break;
            }
        }

        private void Update()
        {
            float dt = Time.deltaTime;
            float input = 0f;
            if (InputEnabled && !Busy) input = GameInput.MoveX;
            else if (_autoTarget.HasValue)
            {
                float dx = _autoTarget.Value - transform.position.x;
                input = Mathf.Abs(dx) < 0.04f ? 0f : Mathf.Sign(dx) * Mathf.Clamp01(Mathf.Abs(dx) / 0.35f + 0.25f);
                if (input == 0f) _autoTarget = null;
            }

            float target = input * WalkSpeed * SpeedMultiplier;
            _vel = Mathf.MoveTowards(_vel, target, Accel * dt);
            if (Mathf.Abs(input) > 0.01f && Mathf.Sign(input) != Facing) Turn(Mathf.Sign(input));

            if (Mathf.Abs(_vel) > 0.001f)
            {
                float step = _vel * dt;
                var origin = new Vector2(transform.position.x, transform.position.y + BodySize.y * 0.5f + 0.1f);
                var hit = Physics2D.BoxCast(origin, BodySize, 0f, new Vector2(Mathf.Sign(step), 0f), Mathf.Abs(step) + 0.02f);
                if (hit.collider != null)
                {
                    step = Mathf.Sign(step) * Mathf.Max(0f, hit.distance - 0.02f);
                    _vel = 0f;
                }
                transform.position += new Vector3(step, 0f, 0f);
            }

            if (!Busy)
            {
                float speed = Mathf.Abs(_vel);
                if (speed > 0.06f)
                {
                    Anim.Play("walk", 0.18f);
                    Anim.Speed = Mathf.Clamp(speed / WalkSpeed, 0.45f, 1.4f);
                    _idleTime = 0f;
                }
                else
                {
                    Anim.Play("idle", 0.3f);
                    Anim.Speed = 1f;
                    if (InputEnabled)
                    {
                        _idleTime += dt;
                        if (_idleTime > 9f && Anim.Has("look_around")) { _idleTime = -6f; StartCoroutine(Act("look_around", 0.3f)); }
                        else if (_idleTime > 4f && _idleTime < 4f + dt && Random.value < 0.35f) StartCoroutine(Act("mustache_adjust", 0.3f));
                    }
                }
            }
        }

        /// <summary>Turns with a quick, deliberate squash (not an instant flip).</summary>
        public void Turn(float dir, bool instant = false)
        {
            dir = Mathf.Sign(dir);
            if (dir == 0f || dir == Facing) return;
            Facing = dir;
            if (_turn != null) StopCoroutine(_turn);
            if (instant)
            {
                _flipScale = dir;
                ApplyFlip();
                return;
            }
            _turn = StartCoroutine(TurnRoutine(dir));
        }

        private IEnumerator TurnRoutine(float dir)
        {
            float from = _flipScale;
            yield return Tween.Run(0.16f, k => { _flipScale = Mathf.Lerp(from, dir, k); ApplyFlip(); }, Ease.InOutSine);
            _turn = null;
        }

        private void ApplyFlip()
        {
            float s = Mathf.Abs(_flipScale) < 0.05f ? 0.05f * Mathf.Sign(_flipScale == 0 ? Facing : _flipScale) : _flipScale;
            Rig.transform.localScale = new Vector3(s, 1f, 1f);
            if (Reflection != null) Reflection.transform.localScale = new Vector3(s, -0.62f, 1f);
        }

        public void Face(float dir, bool instant = false) => Turn(dir, instant);

        /// <summary>Walk (scripted) to an x position; returns when arrived.</summary>
        public IEnumerator WalkTo(float x, float speedMul = 1f)
        {
            bool prevInput = InputEnabled;
            InputEnabled = false;
            SpeedMultiplier = speedMul;
            _autoTarget = x;
            float timeout = Mathf.Abs(x - transform.position.x) / Mathf.Max(0.2f, WalkSpeed * speedMul * 0.5f) + 2f;
            float t = 0f;
            while (_autoTarget.HasValue && t < timeout)
            {
                yield return null;
                t += Time.deltaTime;
            }
            _autoTarget = null;
            var p = transform.position;
            if (Mathf.Abs(p.x - x) < 0.3f) transform.position = new Vector3(x, p.y, p.z);
            SpeedMultiplier = 1f;
            InputEnabled = prevInput;
            while (Mathf.Abs(_vel) > 0.02f) { _vel = Mathf.MoveTowards(_vel, 0f, Accel * Time.deltaTime); yield return null; }
            _vel = 0f;
        }

        /// <summary>Plays a one-shot gesture, then returns to idle.</summary>
        public IEnumerator Act(string clip, float fade = 0.2f)
        {
            Busy = true;
            _vel = 0f;
            Anim.Speed = 1f;
            yield return Anim.PlayAndWait(clip, fade);
            Busy = false;
        }

        /// <summary>Holds a pose/loop (examine, hold trophies…) until Release().</summary>
        public void Hold(string clip, float fade = 0.25f)
        {
            Busy = true;
            _vel = 0f;
            Anim.Speed = 1f;
            Anim.Play(clip, fade, true);
        }

        public void Release() => Busy = false;

        public void Stop() { _vel = 0f; _autoTarget = null; }

        public void SetProp(string slot, Sprite sprite)
        {
            Rig.SetSlotSprite(slot, sprite);
            if (Reflection != null) Reflection.SetSlotSprite(slot, sprite);
        }

        public void SetProp(string slot, string rigSprite) => SetProp(slot, GameAssets.RigSprite(Rig.Data, rigSprite));

        /// <summary>World position of a bone (e.g. head for camera framing, hand for props).</summary>
        public Vector3 BonePosition(string bone)
        {
            var b = Rig.Bone(bone);
            return b != null ? b.position : transform.position;
        }
    }
}

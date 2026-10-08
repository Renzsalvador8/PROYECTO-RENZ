using System.Collections;
using UnityEngine;

namespace TheTester
{
    /// <summary>
    /// Cinematic orthographic camera: damped follow with look-ahead, level bounds, framed zooms and
    /// a fixed 16:9 composition (letterbox/pillarbox via a background camera) on every screen shape.
    /// </summary>
    [DefaultExecutionOrder(50)]
    public sealed class CameraController : MonoBehaviour
    {
        public const float Aspect = 16f / 9f;
        public Camera Cam { get; private set; }
        public Transform Target { get; private set; }

        public float LookAhead = 1.2f;
        public float FollowDamping = 3.2f;
        public float TargetOffsetX;
        public bool Following = true;
        public float BaseY;
        public float BaseSize = 5.4f;

        private float _xMin = -1000f, _xMax = 1000f;
        private float _lookX;
        private float _shakeAmp;
        private Vector3 _base;
        private Camera _bars;
        private int _lastW, _lastH;
        private Coroutine _move;
        private float _zoomSize;
        private float _yOffset;

        public static CameraController Create(Color background)
        {
            var go = new GameObject("Main Camera");
            go.tag = "MainCamera";
            var cam = go.AddComponent<Camera>();
            cam.orthographic = true;
            cam.orthographicSize = 5.4f;
            cam.clearFlags = CameraClearFlags.SolidColor;
            cam.backgroundColor = background;
            cam.nearClipPlane = 0.1f;
            cam.farClipPlane = 100f;
            cam.depth = 0;
            go.transform.position = new Vector3(0f, 0f, -20f);
            go.AddComponent<AudioListener>();
            var cc = go.AddComponent<CameraController>();
            cc.Cam = cam;
            cc._base = go.transform.position;
            cc._zoomSize = 5.4f;
            // background camera paints the letterbox bars
            var bars = new GameObject("Letterbox Camera");
            bars.transform.SetParent(go.transform, false);
            cc._bars = bars.AddComponent<Camera>();
            cc._bars.depth = -10;
            cc._bars.cullingMask = 0;
            cc._bars.clearFlags = CameraClearFlags.SolidColor;
            cc._bars.backgroundColor = new Color(0.02f, 0.04f, 0.07f);
            cc.UpdateViewport(true);
            return cc;
        }

        public void SetBackground(Color c) => Cam.backgroundColor = c;
        public void SetBounds(float xMin, float xMax) { _xMin = xMin; _xMax = xMax; }

        public void SetBaseView(float y, float size)
        {
            BaseY = y;
            BaseSize = size;
            _zoomSize = size;
            Cam.orthographicSize = size;
        }

        public void Follow(Transform t, bool snap = true)
        {
            Target = t;
            Following = t != null;
            if (snap && t != null)
            {
                _base.x = ClampX(t.position.x + TargetOffsetX, Cam.orthographicSize);
                _base.y = BaseY + _yOffset;
                transform.position = _base;
                _lookX = 0f;
            }
        }

        public float HalfWidth(float size) => size * Aspect;

        private float ClampX(float x, float size)
        {
            float hw = HalfWidth(size);
            float lo = _xMin + hw, hi = _xMax - hw;
            if (lo > hi) return (_xMin + _xMax) * 0.5f;
            return Mathf.Clamp(x, lo, hi);
        }

        /// <summary>Optional custom look-ahead source (e.g. the car's speed). Null = use the player's facing.</summary>
        public System.Func<float> LookAheadSource;

        private void LateUpdate()
        {
            UpdateViewport(false);
            float dt = Time.deltaTime;
            if (_move == null)
            {
                Cam.orthographicSize = Mathf.Lerp(Cam.orthographicSize, _zoomSize, 1f - Mathf.Exp(-3f * dt));
                if (Following && Target != null)
                {
                    float ahead;
                    if (LookAheadSource != null) ahead = LookAheadSource();
                    else
                    {
                        var pc = Target.GetComponent<PlayerController2D>();
                        ahead = (pc != null ? pc.Facing : 1f) * LookAhead;
                    }
                    _lookX = Mathf.Lerp(_lookX, ahead, 1f - Mathf.Exp(-1.5f * dt));
                    float desired = ClampX(Target.position.x + _lookX + TargetOffsetX, Cam.orthographicSize);
                    _base.x = Mathf.Lerp(_base.x, desired, 1f - Mathf.Exp(-FollowDamping * dt));
                    _base.y = Mathf.Lerp(_base.y, BaseY + _yOffset, 1f - Mathf.Exp(-3f * dt));
                }
            }
            _shakeAmp = Mathf.Lerp(_shakeAmp, 0f, 1f - Mathf.Exp(-10f * dt));
            var shake = _shakeAmp > 0.001f ? new Vector3(Random.Range(-1f, 1f), Random.Range(-1f, 1f), 0f) * _shakeAmp : Vector3.zero;
            transform.position = _base + shake;
        }

        /// <summary>Keeps a 16:9 viewport; extra screen space becomes bars painted by the background camera.</summary>
        private void UpdateViewport(bool force)
        {
            if (!force && Screen.width == _lastW && Screen.height == _lastH) return;
            _lastW = Screen.width;
            _lastH = Screen.height;
            float screen = (float)Screen.width / Mathf.Max(1, Screen.height);
            Rect r;
            if (screen > Aspect)
            {
                float w = Aspect / screen;
                r = new Rect((1f - w) * 0.5f, 0f, w, 1f);
            }
            else
            {
                float h = screen / Aspect;
                r = new Rect(0f, (1f - h) * 0.5f, 1f, h);
            }
            Cam.rect = r;
        }

        public void Zoom(float size) => _zoomSize = size;
        public void ZoomToBase() => _zoomSize = BaseSize;
        public void SetVerticalOffset(float y) => _yOffset = y;
        public void Shake(float amount) => _shakeAmp = Mathf.Max(_shakeAmp, amount);

        /// <summary>Framed camera move (cuts if duration is 0). Following resumes when 'resumeFollow' is true.</summary>
        public IEnumerator MoveTo(Vector2 center, float size, float duration, bool resumeFollow = false)
        {
            if (_move != null) StopCoroutine(_move);
            var routine = MoveRoutine(center, size, duration, resumeFollow);
            _move = StartCoroutine(routine);
            while (_move != null) yield return null;
        }

        private IEnumerator MoveRoutine(Vector2 center, float size, float duration, bool resumeFollow)
        {
            Following = false;
            var from = _base;
            float fromSize = Cam.orthographicSize;
            var to = new Vector3(center.x, center.y, from.z);
            yield return Tween.Run(duration, k =>
            {
                _base = Vector3.Lerp(from, to, k);
                Cam.orthographicSize = Mathf.Lerp(fromSize, size, k);
            }, Ease.InOutSine);
            _zoomSize = size;
            _move = null;
            if (resumeFollow && Target != null) Following = true;
        }

        public void Cut(Vector2 center, float size)
        {
            if (_move != null) { StopCoroutine(_move); _move = null; }
            Following = false;
            _base = new Vector3(center.x, center.y, _base.z);
            transform.position = _base;
            Cam.orthographicSize = size;
            _zoomSize = size;
        }

        public void ResumeFollow(bool snap = false)
        {
            Following = Target != null;
            _zoomSize = BaseSize;
            if (snap) Follow(Target, true);
        }

        public Vector2 Center => new Vector2(_base.x, _base.y);

        public Vector3 ScreenToWorld(Vector2 screen)
        {
            var w = Cam.ScreenToWorldPoint(new Vector3(screen.x, screen.y, -transform.position.z));
            w.z = 0f;
            return w;
        }

        public Vector2 WorldToScreen(Vector3 world) => Cam.WorldToScreenPoint(world);
    }
}

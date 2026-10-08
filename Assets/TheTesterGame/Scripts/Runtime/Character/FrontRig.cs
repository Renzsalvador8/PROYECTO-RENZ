using System.Collections;
using UnityEngine;

namespace TheTester
{
    /// <summary>
    /// Front-facing Jean Paul holding both awards (from the reference turnaround), with an expressive head:
    /// expression swaps (brow, smile, glances, blink), head tilt and lean, plus subtle breathing.
    /// </summary>
    public sealed class FrontRig : MonoBehaviour
    {
        public TesterRig Rig { get; private set; }
        public string Expression { get; private set; } = "neutral";
        public bool AutoBlink = true;
        private float _blinkTimer = 2.5f;
        private float _breath;
        private float _tilt, _tiltTarget;
        private Vector2 _lean, _leanTarget;

        public static FrontRig Create(Transform parent, Vector3 position, int order, float scale = 1f)
        {
            var go = new GameObject("Jean Paul · Front");
            go.transform.SetParent(parent, false);
            go.transform.position = position;
            go.transform.localScale = Vector3.one * scale;
            var fr = go.AddComponent<FrontRig>();
            fr.Rig = TesterRig.Create("tester_front", go.transform, order, "Rig");
            return fr;
        }

        public void SetExpression(string expr)
        {
            Expression = expr;
            Rig.SetSlotSprite("head", "head_" + expr);
        }

        public void Tilt(float degrees) => _tiltTarget = degrees;
        public void Lean(Vector2 offset) => _leanTarget = offset;

        public IEnumerator Blink()
        {
            string keep = Expression;
            Rig.SetSlotSprite("head", "head_blink");
            yield return new WaitForSeconds(0.11f);
            Rig.SetSlotSprite("head", "head_" + keep);
        }

        private void Update()
        {
            float dt = Time.deltaTime;
            _breath += dt;
            _tilt = Mathf.Lerp(_tilt, _tiltTarget, 1f - Mathf.Exp(-5f * dt));
            _lean = Vector2.Lerp(_lean, _leanTarget, 1f - Mathf.Exp(-4f * dt));
            var pose = Rig.Pose;
            int body = Rig.Data.BoneIndex("body"), head = Rig.Data.BoneIndex("head");
            pose.SY[body] = 1f + Mathf.Sin(_breath * 1.6f) * 0.004f;
            pose.Rot[head] = _tilt + Mathf.Sin(_breath * 0.8f) * 0.4f;
            pose.X[head] = _lean.x;
            pose.Y[head] = _lean.y + Mathf.Sin(_breath * 1.6f) * 0.003f;
            Rig.Apply(pose);
            if (AutoBlink && Expression != "blink")
            {
                _blinkTimer -= dt;
                if (_blinkTimer <= 0f)
                {
                    _blinkTimer = Random.Range(2.6f, 5.2f);
                    StartCoroutine(Blink());
                }
            }
        }
    }
}

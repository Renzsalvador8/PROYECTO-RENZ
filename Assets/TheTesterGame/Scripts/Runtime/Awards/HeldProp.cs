using UnityEngine;

namespace TheTester
{
    /// <summary>
    /// A prop carried in a hand (the awards). Follows a rig bone but stays upright and never mirrors,
    /// so lettering such as "GRAND PRIX" always reads correctly. Lives inside the rig's sorting group.
    /// </summary>
    [DefaultExecutionOrder(30)]
    public sealed class HeldProp : MonoBehaviour
    {
        public Transform Bone;
        public Vector2 Offset;
        public float Tilt;
        public float Scale = 1f;
        public SpriteRenderer Renderer { get; private set; }
        private Vector3? _flyFrom;
        private float _fly = 1f, _flyTime = 0.6f;

        public static HeldProp Create(TesterRig rig, string spritePath, float ppu, Vector2 pivot, int order)
        {
            var go = new GameObject("Held · " + spritePath);
            go.transform.SetParent(rig.transform, false);
            var hp = go.AddComponent<HeldProp>();
            hp.Renderer = go.AddComponent<SpriteRenderer>();
            hp.Renderer.sprite = GameAssets.Sprite(spritePath, ppu, pivot);
            hp.Renderer.sortingOrder = order;
            return hp;
        }

        public void Attach(Transform bone, Vector2 offset, float tilt, int order)
        {
            Bone = bone;
            Offset = offset;
            Tilt = tilt;
            Renderer.sortingOrder = order;
        }

        /// <summary>Animate from a world position into the hand (the award lifting off its pedestal).</summary>
        public void FlyFrom(Vector3 world, float time)
        {
            _flyFrom = world;
            _fly = 0f;
            _flyTime = time;
        }

        private void LateUpdate()
        {
            if (Bone == null) return;
            var parent = transform.parent;
            float sx = parent != null ? Mathf.Sign(parent.lossyScale.x) : 1f;
            var target = Bone.position + new Vector3(Offset.x * sx, Offset.y, 0f);
            if (_fly < 1f && _flyFrom.HasValue)
            {
                _fly = Mathf.Min(1f, _fly + Time.deltaTime / Mathf.Max(0.01f, _flyTime));
                float e = Ease.InOutCubic(_fly);
                var arc = Vector3.up * Mathf.Sin(e * Mathf.PI) * 0.25f;
                transform.position = Vector3.Lerp(_flyFrom.Value, target, e) + arc;
            }
            else
            {
                transform.position = target;
            }
            transform.rotation = Quaternion.Euler(0f, 0f, Tilt * sx);
            transform.localScale = new Vector3(sx * Scale, Scale, 1f);
        }
    }
}

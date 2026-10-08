using System.Collections.Generic;
using UnityEngine;

namespace TheTester
{
    /// <summary>
    /// A real magnifying lens: magnified copies of the scene sprites are revealed only inside a circular
    /// SpriteMask that follows the lens, framed by the brass magnifier artwork.
    /// </summary>
    public sealed class Magnifier : MonoBehaviour
    {
        public Vector2 Position;
        public float Radius = 1.2f;
        public float Zoom = 2f;
        public bool Visible = true;

        private SpriteMask _mask;
        private SpriteRenderer _rim, _glass, _shine, _shadow;
        private readonly List<KeyValuePair<SpriteRenderer, SpriteRenderer>> _copies = new List<KeyValuePair<SpriteRenderer, SpriteRenderer>>();
        private const float MaskSpriteUnits = 2.56f;      // UI/circle is 256 px at 100 ppu
        private const float RimInnerPx = 224f;            // inner radius of the brass rim in UI/magnifier_cursor

        public static Magnifier Create(Transform parent, float radius, float zoom, int baseOrder, params SpriteRenderer[] sources)
        {
            var go = new GameObject("Magnifier");
            go.transform.SetParent(parent, false);
            var m = go.AddComponent<Magnifier>();
            m.Radius = radius;
            m.Zoom = zoom;

            m._shadow = Child(go.transform, "Shadow", GameAssets.Sprite("UI/circle_soft", 100f), baseOrder - 1);
            m._shadow.color = new Color(0f, 0f, 0f, 0.35f);

            var maskGo = new GameObject("Lens Mask");
            maskGo.transform.SetParent(go.transform, false);
            m._mask = maskGo.AddComponent<SpriteMask>();
            m._mask.sprite = GameAssets.Sprite("UI/circle", 100f);

            int i = 0;
            foreach (var src in sources)
            {
                if (src == null) continue;
                var c = Child(go.transform, "Zoom · " + src.name, src.sprite, baseOrder + i++);
                c.maskInteraction = SpriteMaskInteraction.VisibleInsideMask;
                c.color = src.color;
                m._copies.Add(new KeyValuePair<SpriteRenderer, SpriteRenderer>(src, c));
            }
            m._glass = Child(go.transform, "Glass", GameAssets.Sprite("UI/circle_soft", 100f), baseOrder + 10);
            m._glass.color = new Color(0.75f, 0.88f, 0.95f, 0.10f);
            m._glass.maskInteraction = SpriteMaskInteraction.VisibleInsideMask;
            m._shine = Child(go.transform, "Shine", GameAssets.Sprite("UI/circle_soft", 100f), baseOrder + 11);
            m._shine.color = new Color(1f, 1f, 1f, 0.12f);
            m._shine.maskInteraction = SpriteMaskInteraction.VisibleInsideMask;
            m._rim = Child(go.transform, "Rim", GameAssets.Sprite("UI/magnifier_cursor", 100f, new Vector2(0.5f, 1f - 280f / 760f)), baseOrder + 12);
            m.LateUpdate();
            return m;
        }

        private static SpriteRenderer Child(Transform parent, string name, Sprite sprite, int order)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            var sr = go.AddComponent<SpriteRenderer>();
            sr.sprite = sprite;
            sr.sortingOrder = order;
            return sr;
        }

        private void LateUpdate()
        {
            var p = new Vector3(Position.x, Position.y, 0f);
            float d = 2f * Radius / MaskSpriteUnits;
            _mask.transform.position = p;
            _mask.transform.localScale = new Vector3(d, d, 1f);
            _mask.enabled = Visible;
            foreach (var kv in _copies)
            {
                var src = kv.Key;
                var c = kv.Value;
                if (src == null) continue;
                c.enabled = Visible && src.enabled;
                c.sprite = src.sprite;
                var sp = src.transform.position;
                c.transform.position = p + (sp - p) * Zoom;
                c.transform.localScale = src.transform.lossyScale * Zoom;
                c.transform.rotation = src.transform.rotation;
            }
            _glass.transform.position = p;
            _glass.transform.localScale = new Vector3(d, d, 1f);
            _shine.transform.position = p + new Vector3(-Radius * 0.35f, Radius * 0.38f, 0f);
            _shine.transform.localScale = new Vector3(d * 0.45f, d * 0.3f, 1f);
            float s = Radius * 100f / RimInnerPx;
            _rim.transform.position = p;
            _rim.transform.localScale = new Vector3(s, s, 1f);
            _rim.transform.localRotation = Quaternion.Euler(0f, 0f, 28f);
            _shadow.transform.position = p + new Vector3(0.12f, -0.2f, 0f);
            _shadow.transform.localScale = new Vector3(d * 1.25f, d * 1.25f, 1f);
            _rim.enabled = _glass.enabled = _shine.enabled = _shadow.enabled = Visible;
        }
    }
}

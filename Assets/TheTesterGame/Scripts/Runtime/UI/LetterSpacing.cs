using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;

namespace TheTester
{
    /// <summary>
    /// Tracking (letter spacing) for legacy UI Text — editorial uppercase labels need it.
    /// Spacing is in em/100 of the font size (e.g. 18 = 0.18 em). Works per line, respecting alignment.
    /// </summary>
    [RequireComponent(typeof(Text))]
    public sealed class LetterSpacing : BaseMeshEffect
    {
        [SerializeField] private float spacing = 12f;
        private static readonly List<UIVertex> Verts = new List<UIVertex>();

        public float Spacing
        {
            get => spacing;
            set
            {
                spacing = value;
                if (graphic != null) graphic.SetVerticesDirty();
            }
        }

        public override void ModifyMesh(VertexHelper vh)
        {
            if (!IsActive() || vh.currentVertCount == 0) return;
            var text = GetComponent<Text>();
            if (text == null) return;
            Verts.Clear();
            vh.GetUIVertexStream(Verts);
            float px = text.fontSize * spacing / 100f;
            int quads = Verts.Count / 6;
            if (quads == 0) return;

            // group quads into lines (new line when a quad starts left of the previous one)
            var lineStart = new List<int> { 0 };
            for (int q = 1; q < quads; q++)
            {
                float prevX = Verts[(q - 1) * 6].position.x;
                float curX = Verts[q * 6].position.x;
                float prevY = Verts[(q - 1) * 6].position.y;
                float curY = Verts[q * 6].position.y;
                if (curX < prevX - 0.5f || Mathf.Abs(curY - prevY) > text.fontSize * 0.6f) lineStart.Add(q);
            }
            lineStart.Add(quads);
            var align = text.alignment;
            bool center = align == TextAnchor.UpperCenter || align == TextAnchor.MiddleCenter || align == TextAnchor.LowerCenter;
            bool right = align == TextAnchor.UpperRight || align == TextAnchor.MiddleRight || align == TextAnchor.LowerRight;
            for (int l = 0; l < lineStart.Count - 1; l++)
            {
                int a = lineStart[l], b = lineStart[l + 1];
                int n = b - a;
                float total = px * (n - 1);
                float shift = center ? -total / 2f : right ? -total : 0f;
                for (int q = a; q < b; q++)
                {
                    float off = px * (q - a) + shift;
                    for (int v = 0; v < 6; v++)
                    {
                        var vert = Verts[q * 6 + v];
                        vert.position.x += off;
                        Verts[q * 6 + v] = vert;
                    }
                }
            }
            vh.Clear();
            vh.AddUIVertexTriangleStream(Verts);
        }
    }
}

using System;
using UnityEngine;
using UnityEngine.Events;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace TheTester
{
    /// <summary>Palette, typography and widget construction for the minimal editorial UI.</summary>
    public static class UIStyle
    {
        public static readonly Color Cream = new Color32(236, 228, 214, 255);
        public static readonly Color OffWhite = new Color32(214, 203, 192, 255);
        public static readonly Color Bronze = new Color32(182, 120, 84, 255);
        public static readonly Color Midnight = new Color32(9, 27, 45, 255);
        public static readonly Color Petrol = new Color32(27, 52, 71, 255);
        public static readonly Color DesatBlue = new Color32(86, 120, 137, 255);
        public static readonly Color Ink = new Color32(38, 30, 26, 255);
        public static readonly Color Dim = new Color32(150, 160, 168, 255);

        public const string Sans = "Jost-Medium";
        public const string SansRegular = "Jost-Regular";
        public const string SansLight = "Jost-Light";
        public const string Serif = "CormorantGaramond-SemiBold";
        public const string SerifMedium = "CormorantGaramond-Medium";
        public const string SerifItalic = "CormorantGaramond-Italic";
        public const string SerifMediumItalic = "CormorantGaramond-MediumItalic";
    }

    public static class UIFactory
    {
        public static RectTransform Rect(string name, Transform parent, Vector2 anchorMin, Vector2 anchorMax, Vector2 pivot, Vector2 pos, Vector2 size)
        {
            var go = new GameObject(name, typeof(RectTransform));
            go.transform.SetParent(parent, false);
            var rt = (RectTransform)go.transform;
            rt.anchorMin = anchorMin;
            rt.anchorMax = anchorMax;
            rt.pivot = pivot;
            rt.anchoredPosition = pos;
            rt.sizeDelta = size;
            return rt;
        }

        public static RectTransform Stretch(string name, Transform parent)
        {
            var rt = Rect(name, parent, Vector2.zero, Vector2.one, new Vector2(0.5f, 0.5f), Vector2.zero, Vector2.zero);
            return rt;
        }

        public static Text Text(Transform parent, string name, string content, string font, int size, Color color, TextAnchor align,
            float spacing = 0f, Vector2? anchor = null, Vector2? pos = null, Vector2? box = null)
        {
            var a = anchor ?? new Vector2(0.5f, 0.5f);
            var rt = Rect(name, parent, a, a, a, pos ?? Vector2.zero, box ?? new Vector2(1200, 100));
            var t = rt.gameObject.AddComponent<Text>();
            t.font = GameAssets.Font(font);
            t.fontSize = size;
            t.color = color;
            t.alignment = align;
            t.text = content;
            t.horizontalOverflow = HorizontalWrapMode.Wrap;
            t.verticalOverflow = VerticalWrapMode.Overflow;
            t.raycastTarget = false;
            t.supportRichText = false;
            if (spacing > 0f) rt.gameObject.AddComponent<LetterSpacing>().Spacing = spacing;
            return t;
        }

        public static Image Image(Transform parent, string name, Sprite sprite, Color color, Vector2 anchor, Vector2 pos, Vector2 size, bool raycast = false)
        {
            var rt = Rect(name, parent, anchor, anchor, new Vector2(0.5f, 0.5f), pos, size);
            var img = rt.gameObject.AddComponent<Image>();
            img.sprite = sprite;
            img.color = color;
            img.raycastTarget = raycast;
            return img;
        }

        public static Image FullImage(Transform parent, string name, Color color, bool raycast = false)
        {
            var rt = Stretch(name, parent);
            var img = rt.gameObject.AddComponent<Image>();
            img.color = color;
            img.raycastTarget = raycast;
            return img;
        }

        /// <summary>Editorial text button: letterspaced caps, bronze underline that grows on focus.</summary>
        public static Button MenuButton(Transform parent, string label, Vector2 anchor, Vector2 pos, UnityAction onClick, int size = 30, float width = 520f)
        {
            var rt = Rect("Button · " + label, parent, anchor, anchor, new Vector2(0.5f, 0.5f), pos, new Vector2(width, size * 2.1f));
            var hit = rt.gameObject.AddComponent<Image>();
            hit.color = new Color(0, 0, 0, 0);
            var btn = rt.gameObject.AddComponent<Button>();
            btn.transition = Selectable.Transition.None;
            var nav = btn.navigation;
            nav.mode = Navigation.Mode.Vertical;
            btn.navigation = nav;
            var txt = Text(rt, "Label", label, UIStyle.Sans, size, UIStyle.OffWhite, TextAnchor.MiddleCenter, 22f, null, Vector2.zero, new Vector2(width, size * 1.6f));
            var line = Image(rt, "Underline", null, UIStyle.Bronze, new Vector2(0.5f, 0.5f), new Vector2(0, -size * 0.85f), new Vector2(0, 2));
            var fx = rt.gameObject.AddComponent<MenuButtonFx>();
            fx.Init(txt, line.rectTransform, width * 0.36f);
            btn.onClick.AddListener(() => { if (AudioManager.I != null) AudioManager.I.Sfx("ui_confirm", 0.45f); });
            if (onClick != null) btn.onClick.AddListener(onClick);
            return btn;
        }

        public static Slider Slider(Transform parent, string label, Vector2 anchor, Vector2 pos, float value, UnityAction<float> onChange)
        {
            var row = Rect("Slider · " + label, parent, anchor, anchor, new Vector2(0.5f, 0.5f), pos, new Vector2(760, 60));
            Text(row, "Label", label, UIStyle.Sans, 22, UIStyle.OffWhite, TextAnchor.MiddleLeft, 18f, new Vector2(0f, 0.5f), new Vector2(150, 0), new Vector2(300, 50));
            var area = Rect("Track", row, new Vector2(1f, 0.5f), new Vector2(1f, 0.5f), new Vector2(1f, 0.5f), new Vector2(-10, 0), new Vector2(380, 30));
            var bg = Image(area, "Line", null, new Color(1, 1, 1, 0.25f), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(380, 2));
            var fillArea = Rect("Fill Area", area, new Vector2(0, 0.5f), new Vector2(1, 0.5f), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(0, 4));
            var fill = Image(fillArea, "Fill", null, UIStyle.Bronze, new Vector2(0, 0.5f), Vector2.zero, Vector2.zero);
            fill.rectTransform.anchorMin = new Vector2(0, 0);
            fill.rectTransform.anchorMax = new Vector2(1, 1);
            fill.rectTransform.sizeDelta = Vector2.zero;
            var handleArea = Rect("Handle Area", area, new Vector2(0, 0), new Vector2(1, 1), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(-20, 0));
            var handle = Image(handleArea, "Handle", GameAssets.UISprite("circle"), UIStyle.Cream, new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(22, 22), true);
            var s = area.gameObject.AddComponent<Slider>();
            s.fillRect = fill.rectTransform;
            s.handleRect = handle.rectTransform;
            s.targetGraphic = handle;
            s.direction = UnityEngine.UI.Slider.Direction.LeftToRight;
            s.minValue = 0f;
            s.maxValue = 1f;
            s.value = value;
            var nav = s.navigation;
            nav.mode = Navigation.Mode.Vertical;
            s.navigation = nav;
            var hitBg = area.gameObject.AddComponent<Image>();
            hitBg.color = new Color(0, 0, 0, 0);
            if (onChange != null) s.onValueChanged.AddListener(onChange);
            return s;
        }

        public static void SetAlpha(Graphic g, float a)
        {
            var c = g.color;
            c.a = a;
            g.color = c;
        }
    }
}

using System.Collections.Generic;
using TheTester.Core;
using UnityEngine;

namespace TheTester
{
    /// <summary>
    /// Loads and caches every runtime asset from the Resources folders:
    /// Art/... (Art/Resources), UI/... (UI/Resources), Audio/... (Audio/Resources),
    /// Data/... (Data/Resources) and Animations/... (Animations/Resources).
    /// Sprites are created at runtime from the textures so pivots and pixels-per-unit are data driven.
    /// </summary>
    public static class GameAssets
    {
        private static readonly Dictionary<string, Texture2D> Textures = new Dictionary<string, Texture2D>();
        private static readonly Dictionary<string, Sprite> Sprites = new Dictionary<string, Sprite>();
        private static readonly Dictionary<string, JsonNode> JsonCache = new Dictionary<string, JsonNode>();
        private static readonly Dictionary<string, AudioClip> Clips = new Dictionary<string, AudioClip>();
        private static readonly Dictionary<string, Font> Fonts = new Dictionary<string, Font>();
        private static readonly Dictionary<string, RigData> Rigs = new Dictionary<string, RigData>();
        private static readonly Dictionary<string, LevelData> Levels = new Dictionary<string, LevelData>();
        private static Dictionary<string, RigClip> _clipLibrary;
        private static Texture2D _white;

        public static Texture2D Texture(string path)
        {
            if (Textures.TryGetValue(path, out var tex) && tex != null) return tex;
            tex = Resources.Load<Texture2D>(path);
            if (tex == null)
            {
                Debug.LogWarning("[TheTester] Missing texture: " + path);
                tex = White;
            }
            else
            {
                tex.wrapMode = TextureWrapMode.Clamp;
            }
            Textures[path] = tex;
            return tex;
        }

        public static Texture2D White
        {
            get
            {
                if (_white != null) return _white;
                _white = new Texture2D(4, 4, TextureFormat.RGBA32, false) { name = "tt_white" };
                var px = new Color32[16];
                for (int i = 0; i < px.Length; i++) px[i] = new Color32(255, 255, 255, 255);
                _white.SetPixels32(px);
                _white.Apply();
                return _white;
            }
        }

        /// <summary>Whole texture as a sprite. pivot is normalised (0,0 = bottom-left).</summary>
        public static Sprite Sprite(string path, float ppu = 100f, Vector2? pivot = null)
        {
            var pv = pivot ?? new Vector2(0.5f, 0.5f);
            string key = path + "|" + ppu + "|" + pv.x + "," + pv.y;
            if (Sprites.TryGetValue(key, out var s) && s != null) return s;
            var tex = Texture(path);
            s = UnityEngine.Sprite.Create(tex, new Rect(0, 0, tex.width, tex.height), pv, ppu, 0, SpriteMeshType.FullRect);
            s.name = path;
            Sprites[key] = s;
            return s;
        }

        /// <summary>A rect inside an atlas texture (rect in pixels, bottom-left origin).</summary>
        public static Sprite SubSprite(string atlasPath, Rect rect, Vector2 pivot, float ppu)
        {
            string key = atlasPath + "#" + rect + "|" + ppu + "|" + pivot;
            if (Sprites.TryGetValue(key, out var s) && s != null) return s;
            var tex = Texture(atlasPath);
            rect.width = Mathf.Min(rect.width, tex.width - rect.x);
            rect.height = Mathf.Min(rect.height, tex.height - rect.y);
            s = UnityEngine.Sprite.Create(tex, rect, pivot, ppu, 0, SpriteMeshType.FullRect);
            s.name = atlasPath + "#" + rect;
            Sprites[key] = s;
            return s;
        }

        /// <summary>UI sprite with optional 9-slice border (pixels).</summary>
        public static Sprite UISprite(string name, float border = 0f)
        {
            string path = "UI/" + name;
            string key = path + "|ui|" + border;
            if (Sprites.TryGetValue(key, out var s) && s != null) return s;
            var tex = Texture(path);
            s = UnityEngine.Sprite.Create(tex, new Rect(0, 0, tex.width, tex.height), new Vector2(0.5f, 0.5f), 100f, 0,
                SpriteMeshType.FullRect, new Vector4(border, border, border, border));
            s.name = path;
            Sprites[key] = s;
            return s;
        }

        public static JsonNode Json(string path)
        {
            if (JsonCache.TryGetValue(path, out var j)) return j;
            var ta = Resources.Load<TextAsset>(path);
            if (ta == null)
            {
                Debug.LogError("[TheTester] Missing data file: " + path);
                return JsonNode.Null;
            }
            j = JsonNode.Parse(ta.text);
            JsonCache[path] = j;
            return j;
        }

        public static AudioClip Audio(string path)
        {
            if (Clips.TryGetValue(path, out var c)) return c;
            c = Resources.Load<AudioClip>("Audio/" + path);
            if (c == null) Debug.LogWarning("[TheTester] Missing audio: " + path);
            Clips[path] = c;
            return c;
        }

        public static Font Font(string name)
        {
            if (Fonts.TryGetValue(name, out var f) && f != null) return f;
            f = Resources.Load<Font>("UI/Fonts/" + name);
            if (f == null)
            {
                Debug.LogWarning("[TheTester] Missing font " + name + ", using the built-in font.");
                f = Resources.GetBuiltinResource<Font>("LegacyRuntime.ttf");
            }
            Fonts[name] = f;
            return f;
        }

        public static RigData Rig(string name)
        {
            if (Rigs.TryGetValue(name, out var r)) return r;
            r = RigData.FromJson(Json("Data/Rigs/" + name));
            Rigs[name] = r;
            return r;
        }

        public static Dictionary<string, RigClip> ClipLibrary
        {
            get
            {
                if (_clipLibrary == null) _clipLibrary = RigClip.LibraryFromJson(Json("Animations/tester_clips"));
                return _clipLibrary;
            }
        }

        public static LevelData Level(string id)
        {
            if (Levels.TryGetValue(id, out var l)) return l;
            l = LevelData.FromJson(Json("Data/Levels/" + id));
            Levels[id] = l;
            return l;
        }

        /// <summary>Sprite for a named part of a rig atlas (used for props such as the magnifier).</summary>
        public static Sprite RigSprite(RigData rig, string spriteName)
        {
            if (rig == null || string.IsNullOrEmpty(spriteName) || !rig.Sprites.TryGetValue(spriteName, out var d)) return null;
            return SubSprite(rig.Atlas, new Rect(d.X, d.Y, d.W, d.H), new Vector2(d.PivotX, d.PivotY), rig.Ppu);
        }
    }
}

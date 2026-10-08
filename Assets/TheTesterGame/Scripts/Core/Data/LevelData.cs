using System.Collections.Generic;

namespace TheTester.Core
{
    /// <summary>Level layout exported by Tools/ArtPipeline/levels.py (Data/Levels/*.json).</summary>
    public sealed class LevelData
    {
        public sealed class Item
        {
            public string Sprite;
            public string Id;
            public float X, Y, Ppu = 100f;
            public float PivotX = 0.5f, PivotY = 0f;
            public float ScaleX = 1f, ScaleY = 1f, Rot;
            public float Alpha = 1f;
            public float R = 1f, G = 1f, B = 1f;
            public int Order;
        }

        public sealed class Layer
        {
            public string Name;
            public float Parallax = 1f, ParallaxY = 1f;
            public int Order;
            public readonly List<Item> Items = new List<Item>();
        }

        public sealed class Marker
        {
            public string Id;
            public float X, Y;
            public JsonNode Extra;
            public string Prompt => Extra.GetString("prompt");
            public float Radius => Extra.GetFloat("radius", 1.5f);
        }

        public sealed class Box
        {
            public string Id;
            public float X, Y, W, H;
        }

        public string Id;
        public float XMin, XMax;
        public float GroundY;
        public float CameraY, CameraSize = 5.4f;
        public float BgR, BgG, BgB;
        public readonly List<Layer> Layers = new List<Layer>();
        public readonly List<Marker> Markers = new List<Marker>();
        public readonly List<Box> Colliders = new List<Box>();

        public Marker FindMarker(string id)
        {
            foreach (var m in Markers) if (m.Id == id) return m;
            return null;
        }

        public float MarkerX(string id, float fallback = 0f)
        {
            var m = FindMarker(id);
            return m != null ? m.X : fallback;
        }

        public static LevelData FromJson(JsonNode j)
        {
            var d = new LevelData { Id = j.GetString("id"), GroundY = j.GetFloat("groundY", -3.5f) };
            var b = j["bounds"].AsFloats(-10, 10);
            d.XMin = b[0]; d.XMax = b[1];
            d.CameraY = j["camera"].GetFloat("y", 0f);
            d.CameraSize = j["camera"].GetFloat("size", 5.4f);
            var bg = j["background"].AsFloats(9, 27, 45);
            d.BgR = bg[0] / 255f; d.BgG = bg[1] / 255f; d.BgB = bg[2] / 255f;
            foreach (var l in j["layers"].Items)
            {
                var layer = new Layer
                {
                    Name = l.GetString("name"), Parallax = l.GetFloat("parallax", 1f),
                    ParallaxY = l.GetFloat("parallaxY", l.GetFloat("parallax", 1f)), Order = l.GetInt("order")
                };
                foreach (var it in l["items"].Items)
                {
                    var piv = it["pivot"].AsFloats(0.5f, 0f);
                    var tint = it["tint"].AsFloats(1, 1, 1);
                    layer.Items.Add(new Item
                    {
                        Sprite = it.GetString("sprite"), Id = it.GetString("id"),
                        X = it.GetFloat("x"), Y = it.GetFloat("y"), Ppu = it.GetFloat("ppu", 100f),
                        PivotX = piv[0], PivotY = piv[1], ScaleX = it.GetFloat("sx", 1f), ScaleY = it.GetFloat("sy", 1f),
                        Rot = it.GetFloat("rot"), Alpha = it.GetFloat("alpha", 1f), R = tint[0], G = tint[1], B = tint[2],
                        Order = it.GetInt("order"),
                    });
                }
                d.Layers.Add(layer);
            }
            foreach (var m in j["markers"].Items)
                d.Markers.Add(new Marker { Id = m.GetString("id"), X = m.GetFloat("x"), Y = m.GetFloat("y"), Extra = m });
            foreach (var c in j["colliders"].Items)
                d.Colliders.Add(new Box { Id = c.GetString("id"), X = c.GetFloat("x"), Y = c.GetFloat("y"), W = c.GetFloat("w"), H = c.GetFloat("h") });
            return d;
        }
    }
}

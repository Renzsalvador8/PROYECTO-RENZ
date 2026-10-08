using System.Collections.Generic;
using TheTester.Core;
using UnityEngine;

namespace TheTester
{
    /// <summary>Instantiates a data-driven level layout (Data/Levels/*.json) as parallax layers of sprites.</summary>
    public sealed class LevelInstance : MonoBehaviour
    {
        public LevelData Data { get; private set; }
        private readonly Dictionary<string, SpriteRenderer> _byId = new Dictionary<string, SpriteRenderer>();
        private readonly Dictionary<string, Transform> _layers = new Dictionary<string, Transform>();

        public static LevelInstance Build(LevelData data, Transform parent, CameraController cam)
        {
            var root = new GameObject("Level · " + data.Id);
            if (parent != null) root.transform.SetParent(parent, false);
            var li = root.AddComponent<LevelInstance>();
            li.Data = data;
            foreach (var layer in data.Layers)
            {
                var lgo = new GameObject("Layer · " + layer.Name);
                lgo.transform.SetParent(root.transform, false);
                var px = lgo.AddComponent<ParallaxLayer>();
                px.FactorX = layer.Parallax;
                px.FactorY = layer.ParallaxY;
                px.CameraTransform = cam != null ? cam.transform : null;
                li._layers[layer.Name] = lgo.transform;
                int n = 0;
                foreach (var it in layer.Items)
                {
                    var sr = CreateItem(it, lgo.transform, layer.Order + it.Order, n++);
                    if (!string.IsNullOrEmpty(it.Id) && !li._byId.ContainsKey(it.Id)) li._byId[it.Id] = sr;
                }
                px.Apply();
            }
            var cols = new GameObject("Colliders");
            cols.transform.SetParent(root.transform, false);
            foreach (var b in data.Colliders)
            {
                var c = new GameObject("Wall · " + b.Id);
                c.transform.SetParent(cols.transform, false);
                c.transform.position = new Vector3(b.X, b.Y, 0f);
                var bc = c.AddComponent<BoxCollider2D>();
                bc.size = new Vector2(b.W, b.H);
            }
            return li;
        }

        private static SpriteRenderer CreateItem(LevelData.Item it, Transform parent, int order, int index)
        {
            var go = new GameObject(string.IsNullOrEmpty(it.Id) ? it.Sprite.Substring(it.Sprite.LastIndexOf('/') + 1) : it.Id);
            go.transform.SetParent(parent, false);
            go.transform.localPosition = new Vector3(it.X, it.Y, 0f);
            go.transform.localScale = new Vector3(it.ScaleX, it.ScaleY, 1f);
            if (it.Rot != 0f) go.transform.localRotation = Quaternion.Euler(0f, 0f, it.Rot);
            var sr = go.AddComponent<SpriteRenderer>();
            sr.sprite = GameAssets.Sprite(it.Sprite, it.Ppu, new Vector2(it.PivotX, it.PivotY));
            sr.color = new Color(it.R, it.G, it.B, it.Alpha);
            sr.sortingOrder = order;
            return sr;
        }

        public SpriteRenderer Get(string id) => _byId.TryGetValue(id, out var sr) ? sr : null;
        public Transform Layer(string name) => _layers.TryGetValue(name, out var t) ? t : null;
        public LevelData.Marker Marker(string id) => Data.FindMarker(id);
        public float MarkerX(string id) => Data.MarkerX(id);

        /// <summary>World position of an item placed on a parallax layer, as currently rendered.</summary>
        public Vector3 WorldOf(string id)
        {
            var sr = Get(id);
            return sr != null ? sr.transform.position : Vector3.zero;
        }

        /// <summary>Adds a sprite to a layer at runtime (e.g. traffic-light lamps, props).</summary>
        public SpriteRenderer AddSprite(string layer, string sprite, Vector3 localPos, float ppu, Vector2 pivot, int order, string name = null)
        {
            var lt = Layer(layer) ?? transform;
            var go = new GameObject(name ?? sprite);
            go.transform.SetParent(lt, false);
            go.transform.localPosition = localPos;
            var sr = go.AddComponent<SpriteRenderer>();
            sr.sprite = GameAssets.Sprite(sprite, ppu, pivot);
            sr.sortingOrder = order;
            return sr;
        }
    }
}

using System.Collections.Generic;
using TheTester.Core;
using UnityEngine;
using UnityEngine.Rendering;

namespace TheTester
{
    /// <summary>
    /// Runtime cut-out puppet built from a rig description (Data/Rigs/*.json): one Transform per bone,
    /// one SpriteRenderer per slot, sorted inside a SortingGroup so the character sorts as a single unit.
    /// </summary>
    public sealed class TesterRig : MonoBehaviour
    {
        public RigData Data { get; private set; }
        public SortingGroup Group { get; private set; }
        public PoseBuffer Pose { get; private set; }
        public Transform Root => _bones.Length > 0 ? _bones[0] : transform;

        private Transform[] _bones;
        private SpriteRenderer[] _slots;
        private Sprite[] _defaultSprites;
        private Color[] _baseColor;
        private bool[] _forceHidden;
        private Color _tint = Color.white;
        private float _alpha = 1f;

        public static TesterRig Create(string rigName, Transform parent, int sortingOrder, string name = null)
        {
            var go = new GameObject(name ?? ("Rig · " + rigName));
            go.transform.SetParent(parent, false);
            var rig = go.AddComponent<TesterRig>();
            rig.Build(GameAssets.Rig(rigName), sortingOrder);
            return rig;
        }

        private void Build(RigData data, int sortingOrder)
        {
            Data = data;
            Group = gameObject.AddComponent<SortingGroup>();
            Group.sortingOrder = sortingOrder;
            _bones = new Transform[data.Bones.Count];
            for (int i = 0; i < data.Bones.Count; i++)
            {
                var b = data.Bones[i];
                var t = new GameObject(b.Name).transform;
                t.SetParent(b.ParentIndex >= 0 ? _bones[b.ParentIndex] : transform, false);
                t.localPosition = new Vector3(b.X, b.Y, 0f);
                t.localRotation = Quaternion.Euler(0f, 0f, b.Rot);
                _bones[i] = t;
            }
            _slots = new SpriteRenderer[data.Slots.Count];
            _defaultSprites = new Sprite[data.Slots.Count];
            _baseColor = new Color[data.Slots.Count];
            _forceHidden = new bool[data.Slots.Count];
            for (int i = 0; i < data.Slots.Count; i++)
            {
                var s = data.Slots[i];
                var go = new GameObject("slot · " + s.Name);
                go.transform.SetParent(_bones[s.BoneIndex], false);
                var sr = go.AddComponent<SpriteRenderer>();
                sr.sortingOrder = s.Order;
                _defaultSprites[i] = GameAssets.RigSprite(data, s.Sprite);
                sr.sprite = _defaultSprites[i];
                _baseColor[i] = new Color(s.R, s.G, s.B, s.A);
                sr.color = _baseColor[i];
                sr.enabled = !s.HiddenByDefault;
                _slots[i] = sr;
            }
            Pose = new PoseBuffer(data.Bones.Count, data.Slots.Count);
            Pose.Reset(data);
            Apply(Pose);
        }

        public Transform Bone(string name)
        {
            int i = Data.BoneIndex(name);
            return i >= 0 ? _bones[i] : null;
        }

        public SpriteRenderer Slot(string name)
        {
            int i = Data.SlotIndex(name);
            return i >= 0 ? _slots[i] : null;
        }

        public void Apply(PoseBuffer p)
        {
            for (int i = 0; i < _bones.Length; i++)
            {
                var b = Data.Bones[i];
                var t = _bones[i];
                t.localPosition = new Vector3(b.X + p.X[i], b.Y + p.Y[i], 0f);
                t.localRotation = Quaternion.Euler(0f, 0f, b.Rot + p.Rot[i]);
                t.localScale = new Vector3(p.SX[i], p.SY[i], 1f);
            }
            for (int i = 0; i < _slots.Length; i++)
            {
                var sr = _slots[i];
                bool vis = p.Visible[i] >= 0.5f && !_forceHidden[i] && sr.sprite != null;
                if (sr.enabled != vis) sr.enabled = vis;
                if (!vis) continue;
                var c = _baseColor[i] * _tint;
                c.a = _baseColor[i].a * Mathf.Clamp01(p.Alpha[i]) * _alpha;
                sr.color = c;
            }
        }

        /// <summary>Replace the sprite drawn by a slot (props in hands, alternative heads). Null restores the default.</summary>
        public void SetSlotSprite(string slot, Sprite sprite)
        {
            int i = Data.SlotIndex(slot);
            if (i < 0) return;
            _slots[i].sprite = sprite != null ? sprite : _defaultSprites[i];
        }

        public void SetSlotSprite(string slot, string rigSpriteName) => SetSlotSprite(slot, GameAssets.RigSprite(Data, rigSpriteName));

        /// <summary>Hide slots regardless of the animation (e.g. legs while seated in the car).</summary>
        public void SetHidden(bool hidden, params string[] slots)
        {
            foreach (var s in slots)
            {
                int i = Data.SlotIndex(s);
                if (i >= 0) _forceHidden[i] = hidden;
            }
        }

        /// <summary>Overall colour grade (e.g. cooler in the studio).</summary>
        public void SetTint(Color tint) { _tint = tint; Apply(Pose); }
        public void SetAlpha(float a) { _alpha = a; }
        public void SetSortingOrder(int order) => Group.sortingOrder = order;
    }
}

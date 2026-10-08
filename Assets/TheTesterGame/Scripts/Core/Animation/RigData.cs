using System;
using System.Collections.Generic;

namespace TheTester.Core
{
    /// <summary>Cut-out rig description (bones + slots + atlas sprite rects), loaded from Data/Rigs/*.json.</summary>
    public sealed class RigData
    {
        public sealed class SpriteDef
        {
            public string Name;
            public float X, Y, W, H;        // atlas rect, bottom-left origin (Unity convention)
            public float PivotX, PivotY;    // normalised pivot
        }

        public sealed class Bone
        {
            public string Name;
            public string Parent;
            public int ParentIndex = -1;
            public float X, Y;              // rest position relative to parent (world units)
            public float Rot;               // rest rotation (degrees)
        }

        public sealed class Slot
        {
            public string Name;
            public string Bone;
            public int BoneIndex;
            public string Sprite;
            public int Order;
            public float R = 1, G = 1, B = 1, A = 1;
            public bool HiddenByDefault;
        }

        public string Name;
        public float Ppu;
        public string Atlas;
        public int AtlasWidth, AtlasHeight;
        public readonly Dictionary<string, SpriteDef> Sprites = new Dictionary<string, SpriteDef>();
        public readonly List<Bone> Bones = new List<Bone>();
        public readonly List<Slot> Slots = new List<Slot>();
        private readonly Dictionary<string, int> _boneIndex = new Dictionary<string, int>();
        private readonly Dictionary<string, int> _slotIndex = new Dictionary<string, int>();

        public int BoneIndex(string name) => _boneIndex.TryGetValue(name, out int i) ? i : -1;
        public int SlotIndex(string name) => _slotIndex.TryGetValue(name, out int i) ? i : -1;

        public static RigData FromJson(JsonNode j)
        {
            var rig = new RigData
            {
                Name = j.GetString("name"),
                Ppu = j.GetFloat("ppu", 100f),
                Atlas = j.GetString("atlas"),
            };
            var size = j["atlasSize"].AsFloats(0, 0);
            rig.AtlasWidth = (int)size[0];
            rig.AtlasHeight = (int)size[1];
            var sprites = j["sprites"];
            foreach (var key in sprites.Keys)
            {
                var s = sprites[key];
                var r = s["rect"].AsFloats(0, 0, 0, 0);
                var p = s["pivot"].AsFloats(0.5f, 0.5f);
                rig.Sprites[key] = new SpriteDef { Name = key, X = r[0], Y = r[1], W = r[2], H = r[3], PivotX = p[0], PivotY = p[1] };
            }
            foreach (var b in j["bones"].Items)
            {
                var pos = b["pos"].AsFloats(0, 0);
                var bone = new Bone { Name = b.GetString("name"), Parent = b.GetString("parent"), X = pos[0], Y = pos[1], Rot = b.GetFloat("rot") };
                bone.ParentIndex = string.IsNullOrEmpty(bone.Parent) ? -1 : rig.BoneIndex(bone.Parent);
                if (!string.IsNullOrEmpty(bone.Parent) && bone.ParentIndex < 0)
                    throw new FormatException("Bone '" + bone.Name + "' references unknown parent '" + bone.Parent + "' (parents must come first)");
                rig._boneIndex[bone.Name] = rig.Bones.Count;
                rig.Bones.Add(bone);
            }
            foreach (var s in j["slots"].Items)
            {
                var tint = s["tint"].AsFloats(1, 1, 1, 1);
                var slot = new Slot
                {
                    Name = s.GetString("name"), Bone = s.GetString("bone"), Sprite = s.GetString("sprite"), Order = s.GetInt("order"),
                    R = tint[0], G = tint[1], B = tint[2], A = tint[3], HiddenByDefault = s.GetInt("hidden") != 0
                };
                slot.BoneIndex = rig.BoneIndex(slot.Bone);
                if (slot.BoneIndex < 0) throw new FormatException("Slot '" + slot.Name + "' references unknown bone '" + slot.Bone + "'");
                rig._slotIndex[slot.Name] = rig.Slots.Count;
                rig.Slots.Add(slot);
            }
            return rig;
        }
    }
}

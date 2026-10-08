using NUnit.Framework;
using TheTester.Core;
using UnityEngine;

namespace TheTester.Tests
{
    /// <summary>Unity-side checks: every asset the game loads through Resources resolves in the editor.</summary>
    public class UnityContentTests
    {
        [Test]
        public void AllLevelSpritesLoadThroughResources()
        {
            foreach (var id in new[] { "showroom", "drive", "zenith" })
            {
                var level = GameAssets.Level(id);
                foreach (var layer in level.Layers)
                    foreach (var it in layer.Items)
                        Assert.IsNotNull(Resources.Load<Texture2D>(it.Sprite), id + ": " + it.Sprite);
            }
        }

        [Test]
        public void RigAtlasesFontsAndAudioLoad()
        {
            Assert.IsNotNull(Resources.Load<Texture2D>(GameAssets.Rig("tester_side").Atlas));
            Assert.IsNotNull(Resources.Load<Texture2D>(GameAssets.Rig("tester_front").Atlas));
            Assert.Greater(GameAssets.ClipLibrary.Count, 10);
            foreach (var f in new[] { UIStyle.Sans, UIStyle.SansRegular, UIStyle.SansLight, UIStyle.Serif, UIStyle.SerifItalic, UIStyle.SerifMediumItalic })
                Assert.IsNotNull(Resources.Load<Font>("UI/Fonts/" + f), f);
            foreach (var a in new[] { "Music/music_title", "Music/music_drive", "Music/music_finale", "Ambience/amb_showroom", "Sfx/footstep_1", "Sfx/ev_motor" })
                Assert.IsNotNull(Resources.Load<AudioClip>("Audio/" + a), a);
        }

        [Test]
        public void SpritesAreCreatedWithRequestedPixelsPerUnit()
        {
            var s = GameAssets.Sprite("Art/Showroom/floor", 100f, new Vector2(0f, 1f));
            Assert.AreEqual(100f, s.pixelsPerUnit, 1e-3f);
            Assert.AreEqual(s.texture.width / 100f, s.bounds.size.x, 1e-3f);
        }

        [Test]
        public void ValidatorReportsNoProblems()
        {
            var problems = TheTester.EditorTools.TheTesterValidator.Validate();
            Assert.IsEmpty(problems, string.Join("\n", problems));
        }
    }
}

using UnityEditor;
using UnityEngine;

namespace TheTester.EditorTools
{
    /// <summary>
    /// Import settings for the game's art and audio (applied automatically on import).
    /// Character atlases keep mipmaps (they are drawn smaller than authored); everything else is a crisp
    /// single sprite without mipmaps. Audio is Vorbis, tuned for small Web downloads.
    /// </summary>
    public sealed class TheTesterImportRules : AssetPostprocessor
    {
        private const string Root = "Assets/TheTesterGame/";

        private void OnPreprocessTexture()
        {
            if (!assetPath.StartsWith(Root)) return;
            var ti = (TextureImporter)assetImporter;
            ti.textureType = TextureImporterType.Sprite;
            ti.spriteImportMode = SpriteImportMode.Single;
            ti.alphaIsTransparency = true;
            ti.npotScale = TextureImporterNPOTScale.None;
            ti.isReadable = false;
            ti.wrapMode = assetPath.EndsWith("/grain.png") ? TextureWrapMode.Repeat : TextureWrapMode.Clamp;
            bool character = assetPath.Contains("/Art/Character/");
            ti.mipmapEnabled = character;
            ti.filterMode = character ? FilterMode.Trilinear : FilterMode.Bilinear;
            ti.maxTextureSize = 2048;
            ti.textureCompression = TextureImporterCompression.Compressed;
            ti.compressionQuality = 70;
            ti.spritePixelsPerUnit = 100;
        }

        private void OnPreprocessAudio()
        {
            if (!assetPath.StartsWith(Root)) return;
            var ai = (AudioImporter)assetImporter;
            var s = ai.defaultSampleSettings;
            bool longClip = assetPath.Contains("/Music/") || assetPath.Contains("/Ambience/");
            s.loadType = longClip ? AudioClipLoadType.CompressedInMemory : AudioClipLoadType.DecompressOnLoad;
            s.compressionFormat = AudioCompressionFormat.Vorbis;
            s.quality = longClip ? 0.55f : 0.7f;
            ai.defaultSampleSettings = s;
        }
    }
}

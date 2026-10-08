"""Writes Unity .meta files with deterministic GUIDs (so references stay stable across clones) and the
four scene files. Run from the repo root:  python3 Tools/UnityMeta/generate_meta.py
Existing .meta files are kept unless --force is given (Unity's own edits are preserved).
"""
import hashlib, os, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ASSETS = os.path.join(ROOT, 'Assets')
FORCE = '--force' in sys.argv


def guid(rel):
    return hashlib.md5(('thetester:' + rel.replace(os.sep, '/')).encode()).hexdigest()


FOLDER = """fileFormatVersion: 2
guid: {guid}
folderAsset: yes
DefaultImporter:
  externalObjects: {{}}
  userData: 
  assetBundleName: 
  assetBundleVariant: 
"""

SCRIPT = """fileFormatVersion: 2
guid: {guid}
MonoImporter:
  externalObjects: {{}}
  serializedVersion: 2
  defaultReferences: []
  executionOrder: 0
  icon: {{instanceID: 0}}
  userData: 
  assetBundleName: 
  assetBundleVariant: 
"""

ASMDEF = """fileFormatVersion: 2
guid: {guid}
AssemblyDefinitionImporter:
  externalObjects: {{}}
  userData: 
  assetBundleName: 
  assetBundleVariant: 
"""

TEXT = """fileFormatVersion: 2
guid: {guid}
TextScriptImporter:
  externalObjects: {{}}
  userData: 
  assetBundleName: 
  assetBundleVariant: 
"""

DEFAULT = """fileFormatVersion: 2
guid: {guid}
DefaultImporter:
  externalObjects: {{}}
  userData: 
  assetBundleName: 
  assetBundleVariant: 
"""

FONT = """fileFormatVersion: 2
guid: {guid}
TrueTypeFontImporter:
  externalObjects: {{}}
  serializedVersion: 4
  fontSize: 16
  forceTextureCase: -2
  characterSpacing: 0
  characterPadding: 1
  includeFontData: 1
  fontNames:
  - {name}
  fallbackFontReferences: []
  customCharacters: 
  fontRenderingMode: 0
  ascentCalculationMode: 1
  useLegacyBoundsCalculation: 0
  shouldRoundAdvanceValue: 1
  userData: 
  assetBundleName: 
  assetBundleVariant: 
"""

AUDIO = """fileFormatVersion: 2
guid: {guid}
AudioImporter:
  externalObjects: {{}}
  serializedVersion: 7
  defaultSettings:
    serializedVersion: 2
    loadType: {load}
    sampleRateSetting: 0
    sampleRateOverride: 44100
    compressionFormat: 1
    quality: {quality}
    conversionMode: 0
    preloadAudioData: 1
  platformSettingOverrides: {{}}
  forceToMono: 0
  normalize: 0
  loadInBackground: 0
  ambisonic: 0
  3D: 0
  userData: 
  assetBundleName: 
  assetBundleVariant: 
"""

TEXTURE = """fileFormatVersion: 2
guid: {guid}
TextureImporter:
  internalIDToNameTable: []
  externalObjects: {{}}
  serializedVersion: 13
  mipmaps:
    mipMapMode: 0
    enableMipMap: {mips}
    sRGBTexture: 1
    linearTexture: 0
    fadeOut: 0
    borderMipMap: 0
    mipMapsPreserveCoverage: 0
    alphaTestReferenceValue: 0.5
    mipMapFadeDistanceStart: 1
    mipMapFadeDistanceEnd: 3
  bumpmap:
    convertToNormalMap: 0
    externalNormalMap: 0
    heightScale: 0.25
    normalMapFilter: 0
    flipGreenChannel: 0
  isReadable: 0
  streamingMipmaps: 0
  streamingMipmapsPriority: 0
  vTOnly: 0
  ignoreMipmapLimit: 0
  grayScaleToAlpha: 0
  generateCubemap: 6
  cubemapConvolution: 0
  seamlessCubemap: 0
  textureFormat: 1
  maxTextureSize: 2048
  textureSettings:
    serializedVersion: 2
    filterMode: {filter}
    aniso: 1
    mipBias: 0
    wrapU: {wrap}
    wrapV: {wrap}
    wrapW: {wrap}
  nPOTScale: 0
  lightmap: 0
  compressionQuality: 70
  spriteMode: 1
  spriteExtrude: 1
  spriteMeshType: 0
  alignment: 0
  spritePivot: {{x: 0.5, y: 0.5}}
  spritePixelsToUnits: 100
  spriteBorder: {{x: 0, y: 0, z: 0, w: 0}}
  spriteGenerateFallbackPhysicsShape: 0
  alphaUsage: 1
  alphaIsTransparency: 1
  spriteTessellationDetail: -1
  textureType: 8
  textureShape: 1
  singleChannelComponent: 0
  flipbookRows: 1
  flipbookColumns: 1
  maxTextureSizeSet: 0
  compressionQualitySet: 0
  textureFormatSet: 0
  ignorePngGamma: 0
  applyGammaDecoding: 0
  swizzle: 50462976
  cookieLightType: 0
  platformSettings:
  - serializedVersion: 3
    buildTarget: DefaultTexturePlatform
    maxTextureSize: 2048
    resizeAlgorithm: 0
    textureFormat: -1
    textureCompression: 1
    compressionQuality: 70
    crunchedCompression: 0
    allowsAlphaSplitting: 0
    overridden: 0
    ignorePlatformSupport: 0
    androidETC2FallbackOverride: 0
    forceMaximumCompressionQuality_BC6H_BC7: 0
  spriteSheet:
    serializedVersion: 2
    sprites: []
    outline: []
    physicsShape: []
    bones: []
    spriteID: {sprite_id}
    internalID: 0
    vertices: []
    indices: 
    edges: []
    weights: []
    secondaryTextures: []
    nameFileIdTable: {{}}
  mipmapLimitGroupName: 
  pSDRemoveMatte: 0
  userData: 
  assetBundleName: 
  assetBundleVariant: 
"""

SCENES = [('00_MainMenu', 0), ('01_Showroom', 1), ('02_TestDrive', 2), ('03_ZenithStudio', 3)]

SCENE = """%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!1 &1000000001
GameObject:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  serializedVersion: 6
  m_Component:
  - component: {{fileID: 1000000002}}
  - component: {{fileID: 1000000003}}
  m_Layer: 0
  m_Name: SceneBootstrap
  m_TagString: Untagged
  m_Icon: {{fileID: 0}}
  m_NavMeshLayer: 0
  m_StaticEditorFlags: 0
  m_IsActive: 1
--- !u!4 &1000000002
Transform:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: 1000000001}}
  serializedVersion: 2
  m_LocalRotation: {{x: 0, y: 0, z: 0, w: 1}}
  m_LocalPosition: {{x: 0, y: 0, z: 0}}
  m_LocalScale: {{x: 1, y: 1, z: 1}}
  m_ConstrainProportionsScale: 0
  m_Children: []
  m_Father: {{fileID: 0}}
  m_LocalEulerAnglesHint: {{x: 0, y: 0, z: 0}}
--- !u!114 &1000000003
MonoBehaviour:
  m_ObjectHideFlags: 0
  m_CorrespondingSourceObject: {{fileID: 0}}
  m_PrefabInstance: {{fileID: 0}}
  m_PrefabAsset: {{fileID: 0}}
  m_GameObject: {{fileID: 1000000001}}
  m_Enabled: 1
  m_EditorHideFlags: 0
  m_Script: {{fileID: 11500000, guid: {script_guid}, type: 3}}
  m_Name: 
  m_EditorClassIdentifier: 
  scene: {scene_index}
--- !u!1660057539 &9223372036854775807
SceneRoots:
  m_ObjectHideFlags: 0
  m_Roots:
  - {{fileID: 1000000002}}
"""

BUILD_SETTINGS = """%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!1045 &1
EditorBuildSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 2
  m_Scenes:
{scenes}  m_configObjects: {{}}
"""


def write(path, content):
    if os.path.exists(path) and not FORCE:
        return False
    with open(path, 'w', newline='\n') as f:
        f.write(content)
    return True


def meta_for(rel, is_dir):
    g = guid(rel)
    if is_dir:
        return FOLDER.format(guid=g)
    ext = os.path.splitext(rel)[1].lower()
    name = os.path.splitext(os.path.basename(rel))[0]
    if ext == '.cs':
        return SCRIPT.format(guid=g)
    if ext == '.asmdef':
        return ASMDEF.format(guid=g)
    if ext in ('.json', '.txt', '.md', '.html', '.css'):
        return TEXT.format(guid=g) if ext != '.html' else DEFAULT.format(guid=g)
    if ext == '.ttf':
        family = name.split('-')[0]
        family = {'CormorantGaramond': 'Cormorant Garamond'}.get(family, family)
        return FONT.format(guid=g, name=family)
    if ext in ('.ogg', '.wav'):
        long_clip = '/Music/' in rel or '/Ambience/' in rel
        return AUDIO.format(guid=g, load=1 if long_clip else 0, quality=0.55 if long_clip else 0.7)
    if ext in ('.png', '.jpg', '.jpeg'):
        character = '/Art/Resources/Art/Character/' in rel
        wrap = 0 if rel.endswith('/grain.png') else 1
        return TEXTURE.format(guid=g, mips=1 if character else 0, filter=2 if character else 1, wrap=wrap,
                              sprite_id=hashlib.md5(('sprite:' + rel).encode()).hexdigest())
    return DEFAULT.format(guid=g)


def main():
    scripts_guid = guid('Assets/TheTesterGame/Scripts/Runtime/Bootstrap/SceneBootstrap.cs')
    scenes_dir = os.path.join(ASSETS, 'TheTesterGame', 'Scenes')
    os.makedirs(scenes_dir, exist_ok=True)
    for name, idx in SCENES:
        write(os.path.join(scenes_dir, name + '.unity'), SCENE.format(script_guid=scripts_guid, scene_index=idx))
    count = 0
    for dirpath, dirnames, filenames in os.walk(ASSETS):
        dirnames[:] = [d for d in dirnames if not d.startswith('.')]
        for d in dirnames:
            full = os.path.join(dirpath, d)
            rel = os.path.relpath(full, ROOT)
            if write(full + '.meta', meta_for(rel, True)):
                count += 1
        for f in filenames:
            if f.endswith('.meta') or f.startswith('.'):
                continue
            full = os.path.join(dirpath, f)
            rel = os.path.relpath(full, ROOT).replace(os.sep, '/')
            if write(full + '.meta', meta_for(rel, False)):
                count += 1
    entries = ''
    for name, _ in SCENES:
        rel = 'Assets/TheTesterGame/Scenes/' + name + '.unity'
        entries += '  - enabled: 1\n    path: {}\n    guid: {}\n'.format(rel, guid(rel))
    os.makedirs(os.path.join(ROOT, 'ProjectSettings'), exist_ok=True)
    write(os.path.join(ROOT, 'ProjectSettings', 'EditorBuildSettings.asset'), BUILD_SETTINGS.format(scenes=entries))
    print('meta files written:', count)


if __name__ == '__main__':
    main()

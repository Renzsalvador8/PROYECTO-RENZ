using System.Collections.Generic;
using System.Text;
using TheTester.Core;
using UnityEditor;
using UnityEngine;

namespace TheTester.EditorTools
{
    /// <summary>The Tester ▸ Validar contenido: checks that every sprite, clip and data file the game references exists.</summary>
    public static class TheTesterValidator
    {
        [MenuItem("The Tester/Validar contenido", priority = 30)]
        public static void ValidateMenu()
        {
            var problems = Validate();
            if (problems.Count == 0)
            {
                Debug.Log("[The Tester] Contenido válido: niveles, rigs, animaciones, audio y fuentes encontrados.");
                EditorUtility.DisplayDialog("The Tester", "Todo el contenido referenciado existe.", "OK");
            }
            else
            {
                var sb = new StringBuilder();
                foreach (var p in problems) sb.AppendLine(p);
                Debug.LogError("[The Tester] Problemas de contenido:\n" + sb);
                EditorUtility.DisplayDialog("The Tester", problems.Count + " problema(s). Revisa la consola.", "OK");
            }
        }

        public static List<string> Validate()
        {
            var problems = new List<string>();
            void Need<T>(string path) where T : Object
            {
                if (Resources.Load<T>(path) == null) problems.Add("Falta " + typeof(T).Name + ": " + path);
            }
            foreach (var id in new[] { "showroom", "drive", "zenith" })
            {
                var ta = Resources.Load<TextAsset>("Data/Levels/" + id);
                if (ta == null) { problems.Add("Falta nivel " + id); continue; }
                var level = LevelData.FromJson(JsonNode.Parse(ta.text));
                foreach (var l in level.Layers)
                    foreach (var it in l.Items) Need<Texture2D>(it.Sprite);
            }
            foreach (var rig in new[] { "tester_side", "tester_front" })
            {
                var ta = Resources.Load<TextAsset>("Data/Rigs/" + rig);
                if (ta == null) { problems.Add("Falta rig " + rig); continue; }
                Need<Texture2D>(RigData.FromJson(JsonNode.Parse(ta.text)).Atlas);
            }
            Need<TextAsset>("Animations/tester_clips");
            Need<TextAsset>("Data/Vehicles/ioniq5");
            Need<TextAsset>("Data/Inspection/interior");
            foreach (var s in new[] { "Art/Inspection/bg_exterior", "Art/Inspection/ioniq5_34_teal", "Art/Inspection/ioniq5_interior",
                                      "Art/Showroom/exterior_day", "Art/Menu/title_dusk", "Art/Drive/cabin_interior", "Art/Drive/lamp_red",
                                      "Art/Props/award_lux_grand_prix", "Art/Props/award_effie_bronze", "Art/Zenith/lobby", "Art/Zenith/lobby_fg", "Art/Zenith/finale_backdrop", "UI/title_lockup",
                                      "UI/end_lockup", "UI/magnifier_cursor", "UI/grain", "UI/vignette" })
                Need<Texture2D>(s);
            foreach (var f in new[] { "Jost-Medium", "Jost-Regular", "Jost-Light", "CormorantGaramond-SemiBold", "CormorantGaramond-Italic", "CormorantGaramond-MediumItalic", "CormorantGaramond-Medium" })
                Need<Font>("UI/Fonts/" + f);
            foreach (var a in new[] { "Music/music_title", "Music/music_drive", "Music/music_finale", "Music/sting_complete", "Ambience/amb_showroom",
                                      "Ambience/amb_studio", "Ambience/amb_city", "Sfx/footstep_1", "Sfx/magnifier_up", "Sfx/inspect_found", "Sfx/ev_motor",
                                      "Sfx/road_noise", "Sfx/trophy_lux", "Sfx/trophy_effie", "Sfx/applause", "Sfx/big_magnifier" })
                Need<AudioClip>("Audio/" + a);
            return problems;
        }
    }
}

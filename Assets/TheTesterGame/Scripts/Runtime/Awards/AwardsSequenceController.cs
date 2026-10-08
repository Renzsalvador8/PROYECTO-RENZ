using System.Collections;
using TheTester.Core;
using UnityEngine;

namespace TheTester
{
    /// <summary>
    /// The awards at Zenith Studio: two pedestals (LUX Grand Prix, EFFIE Ecuador Bronze). Each press of E hands
    /// one award to Jean Paul; then the front-facing close-up (inspired by the reference of him holding both),
    /// a careful inspection of each, a raised eyebrow, a long awkward pause and, finally, a tiny smile.
    /// </summary>
    public sealed class AwardsSequenceController : MonoBehaviour
    {
        private DirectorBase _d;
        private LevelInstance _level;
        private PlayerController2D _player;
        private HeldProp _lux, _effie;
        public bool Running { get; private set; }
        public int Received { get; private set; }

        public void Init(DirectorBase d)
        {
            _d = d;
            _level = d.Level;
            _player = d.Player;
        }

        public IEnumerator ReceiveNext()
        {
            if (Running) yield break;
            if (!GameManager.I.Progress.ReceiveNextAward(out var id)) yield break;
            Running = true;
            if (id == "lux") yield return ReceiveLux();
            else yield return ReceiveEffie();
            GameManager.I.Save();
            Received++;
            Running = false;
        }

        private IEnumerator ReceiveLux()
        {
            var ui = UIManager.I;
            float px = _level.MarkerX("award_lux");
            yield return _player.WalkTo(px + 1.05f);
            _player.Face(-1f);
            yield return Tween.Wait(0.35f);
            var trophy = _level.Get("award_lux");
            _player.Hold("receive", 0.2f);
            yield return Tween.Wait(0.75f);
            _lux = HeldProp.Create(_player.Rig, "Art/Props/award_lux_grand_prix", 340f, new Vector2(0.5f, 0.02f), 119);
            _lux.Attach(_player.Rig.Bone("wrist_f"), new Vector2(0.03f, -0.12f), 0f, 119);
            _lux.FlyFrom(trophy != null ? trophy.transform.position : _player.transform.position, 0.55f);
            if (trophy != null) trophy.enabled = false;
            AudioManager.I.Sfx("trophy_lux", 0.7f);
            yield return Tween.Wait(0.85f);
            _player.Hold("hold", 0.4f);
            AudioManager.I.Sfx("applause", 0.45f);
            _d.Cam.Shake(0.01f);
            yield return ui.TitleCard(Lines.AwardLuxTitle, Lines.AwardLuxSub, 2.0f, 70);
            _player.Release();   // free to walk to the second pedestal, award in hand
        }

        private IEnumerator ReceiveEffie()
        {
            var ui = UIManager.I;
            float px = _level.MarkerX("award_effie");
            _player.Release();
            yield return _player.WalkTo(px - 1.05f);
            _player.Face(1f);
            // the Lux moves to the far hand so the near hand is free
            if (_lux != null) _lux.Attach(_player.Rig.Bone("wrist_b"), new Vector2(0.02f, -0.12f), 0f, 9);
            var trophy = _level.Get("award_effie");
            _player.Hold("receive", 0.2f);
            yield return Tween.Wait(0.75f);
            _effie = HeldProp.Create(_player.Rig, "Art/Props/award_effie_bronze", 420f, new Vector2(0.5f, 0.02f), 119);
            _effie.Attach(_player.Rig.Bone("wrist_f"), new Vector2(0.03f, -0.1f), 0f, 119);
            _effie.FlyFrom(trophy != null ? trophy.transform.position : _player.transform.position, 0.55f);
            if (trophy != null) trophy.enabled = false;
            AudioManager.I.Sfx("trophy_effie", 0.7f);
            yield return Tween.Wait(0.85f);
            _player.Hold("hold", 0.4f);
            AudioManager.I.Sfx("applause", 0.5f);
            yield return ui.TitleCard(Lines.AwardEffieTitle, Lines.AwardEffieSub, 2.0f, 70);
        }

        /// <summary>The front-facing close-up and the deadpan ending.</summary>
        public IEnumerator Finale(Vector2 stage)
        {
            var ui = UIManager.I;
            var audio = AudioManager.I;
            Running = true;
            ui.SetHudVisible(false);
            ui.SetTouchMode(TouchLayout.None);
            ui.SetLetterbox(1f, 1.2f);
            audio.PlayMusic("music_finale", 2.5f, 0.55f, false);
            yield return Tween.Wait(1.4f);
            yield return ui.FadeOut(1.2f);

            var root = new GameObject("Finale").transform;
            root.position = stage;
            var back = new GameObject("Backdrop").AddComponent<SpriteRenderer>();
            back.transform.SetParent(root, false);
            back.transform.localPosition = new Vector3(0f, -4.2f, 0f);
            back.sprite = GameAssets.Sprite("Art/Zenith/stage", 100f, new Vector2(0.5f, 0f));
            back.sortingOrder = 3000;
            var floor = new GameObject("Floor").AddComponent<SpriteRenderer>();
            floor.transform.SetParent(root, false);
            floor.transform.localPosition = new Vector3(0f, -4.2f, 0f);
            floor.transform.localScale = new Vector3(4.5f, 1f, 1f);
            floor.sprite = GameAssets.Sprite("Art/Zenith/floor", 100f, new Vector2(0.5f, 1f));
            floor.sortingOrder = 3001;
            var cone = new GameObject("Spot").AddComponent<SpriteRenderer>();
            cone.transform.SetParent(root, false);
            cone.transform.localPosition = new Vector3(0f, -4.9f, 0f);
            cone.transform.localScale = new Vector3(1.0f, 1.1f, 1f);
            cone.sprite = GameAssets.Sprite("Art/Showroom/spot_cone", 100f, new Vector2(0.5f, 0f));
            cone.color = new Color(1f, 0.95f, 0.88f, 0.9f);
            cone.sortingOrder = 3002;
            var fr = FrontRig.Create(root, (Vector3)stage + new Vector3(0f, -4.35f, 0f), 3010, 1.0f);
            fr.AutoBlink = true;
            var cam = _d.Cam;
            var head = fr.Rig.Bone("head").position;
            var wide = new Vector2(stage.x, head.y - 0.95f);
            cam.Cut(wide, 1.55f);
            yield return ui.FadeIn(1.4f);
            yield return Tween.Wait(1.2f);

            // he looks at the trophies — one, then the other
            fr.SetExpression("look_dl");
            fr.Tilt(5f);
            fr.Lean(new Vector2(-0.03f, -0.02f));
            StartCoroutine(cam.MoveTo(wide + new Vector2(-0.18f, -0.05f), 1.42f, 1.4f));
            audio.Sfx("cloth_1", 0.25f);
            yield return Tween.Wait(2.0f);
            fr.SetExpression("look_dr");
            fr.Tilt(-5f);
            fr.Lean(new Vector2(0.03f, -0.02f));
            StartCoroutine(cam.MoveTo(wide + new Vector2(0.18f, -0.05f), 1.42f, 1.4f));
            yield return Tween.Wait(2.0f);
            // back to centre, an eyebrow
            fr.SetExpression("neutral");
            fr.Tilt(0f);
            fr.Lean(Vector2.zero);
            yield return cam.MoveTo(new Vector2(stage.x, head.y - 0.55f), 1.15f, 1.6f);
            fr.SetExpression("brow_one");
            audio.Sfx("stache", 0.2f, 1.3f);
            yield return Tween.Wait(1.3f);
            // a long, awkward pause
            fr.AutoBlink = false;
            audio.DuckMusic(0.04f, 1.0f);
            yield return Tween.Wait(2.2f);
            yield return fr.Blink();
            yield return Tween.Wait(2.3f);
            // finally: the tiniest approving smile
            fr.SetExpression("smile");
            audio.Sfx("stache", 0.45f);
            audio.DuckMusic(1f, 2.5f);
            yield return Tween.Wait(2.6f);
            yield return ui.FadeOut(1.6f);
            GameManager.I.Progress.Finish();
            GameManager.I.Save();
            Destroy(root.gameObject);
            ui.SetLetterbox(0f, 0f);
            ui.SetFadeInstant(0f);
            yield return ui.ShowEnd(Lines.FinalVerdict);
            Running = false;
        }
    }
}

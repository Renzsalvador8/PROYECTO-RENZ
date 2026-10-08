using System.Collections;
using UnityEngine;

namespace TheTester
{
    /// <summary>Title screen: the dealership at blue hour, Jean Paul waiting under a street lamp, minimal menu.</summary>
    public sealed class MainMenuDirector : DirectorBase
    {
        public override bool AllowPause => false;
        private PlayerController2D _tester;

        protected override IEnumerator Run()
        {
            UI.SetFadeInstant(1f);
            BuildCamera(new Color(0.04f, 0.09f, 0.16f));
            var bg = new GameObject("Title · Dusk").AddComponent<SpriteRenderer>();
            bg.sprite = GameAssets.Sprite("Art/Menu/title_dusk", 100f, new Vector2(0.5f, 0.5f));
            bg.sortingOrder = -100;
            Cam.SetBounds(-10.24f, 10.24f);
            Cam.Cut(new Vector2(0.4f, 0f), 5.4f);
            _tester = PlayerController2D.Spawn(new Vector3(-3.4f, -4.2f, 0f), false, -4.2f);   // painting ground line (y = 960 px)
            _tester.transform.localScale = Vector3.one * 0.78f;
            _tester.Rig.SetTint(new Color(0.72f, 0.74f, 0.86f));
            _tester.Face(1f, true);

            UI.SetFinish(0.85f, 0.08f);
            UI.OnMenuPlay -= HandlePlay;
            UI.OnMenuContinue -= HandleContinue;
            UI.OnMenuPlay += HandlePlay;
            UI.OnMenuContinue += HandleContinue;
            UI.ShowMainMenu(SaveManager.HasSave);
            Audio.PlayMusic("music_title", 2.5f, 0.6f);
            Audio.PlayAmbience("amb_city", 2.5f, 0.25f);
            yield return UI.FadeIn(1.6f);

            float t = 0f;
            float nextGesture = 6f;
            while (true)
            {
                t += Time.deltaTime;
                Cam.Cut(new Vector2(0.4f + Mathf.Sin(t * 0.05f) * 0.35f, Mathf.Sin(t * 0.07f) * 0.08f), 5.4f - Mathf.Sin(t * 0.04f) * 0.06f);
                if (t > nextGesture && !_tester.Busy)
                {
                    nextGesture = t + Random.Range(7f, 11f);
                    StartCoroutine(_tester.Act(Random.value < 0.5f ? "mustache_adjust" : "look_around", 0.3f));
                }
                yield return null;
            }
        }

        private void HandlePlay()
        {
            UI.HideMainMenu();
            Audio.StopMusic(1.2f);
            GameManager.I.NewGame();
        }

        private void HandleContinue()
        {
            UI.HideMainMenu();
            Audio.StopMusic(1.2f);
            GameManager.I.Continue();
        }

        private void OnDestroy()
        {
            if (UI == null) return;
            UI.OnMenuPlay -= HandlePlay;
            UI.OnMenuContinue -= HandleContinue;
            UI.SetFinish(0.62f, 0.075f);
        }
    }
}

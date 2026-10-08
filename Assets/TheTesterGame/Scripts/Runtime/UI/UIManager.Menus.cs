using System;
using System.Collections;
using TheTester.Core;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace TheTester
{
    /// <summary>Main menu, instructions, settings, credits, pause and end screen panels.</summary>
    public sealed partial class UIManager
    {
        private CanvasGroup _mainMenu, _instructions, _settings, _credits, _pause, _end;
        private Button _btnContinue;
        private Button _firstMain, _firstPause, _firstEnd;
        private Text _fullscreenLabel, _endVerdict;
        private Image _titleLockup;
        private CanvasGroup _returnPanel;
        public event Action OnMenuPlay, OnMenuContinue, OnEndPlayAgain, OnEndMenu;

        private void BuildMenus()
        {
            // ---------------- main menu
            _mainMenu = Panel("Main Menu", false);
            var mm = _mainMenu.transform;
            UIFactory.Image(mm, "Backing", GameAssets.UISprite("circle_soft"), new Color(0.02f, 0.05f, 0.09f, 0.62f), new Vector2(0.5f, 0.5f), new Vector2(0, -160), new Vector2(1250, 760));
            _titleLockup = UIFactory.Image(mm, "Title Lockup", GameAssets.UISprite("title_lockup"), Color.white, new Vector2(0.5f, 1f), new Vector2(0, -260), new Vector2(1200, 390));
            _titleLockup.preserveAspect = true;
            float y = -10f;
            _firstMain = UIFactory.MenuButton(mm, Lines.MenuPlay, new Vector2(0.5f, 0.5f), new Vector2(0, y), () => OnMenuPlay?.Invoke());
            _btnContinue = UIFactory.MenuButton(mm, Lines.MenuContinue, new Vector2(0.5f, 0.5f), new Vector2(0, y - 70), () => OnMenuContinue?.Invoke());
            UIFactory.MenuButton(mm, Lines.MenuInstructions, new Vector2(0.5f, 0.5f), new Vector2(0, y - 140), () => Open(_instructions, null, _mainMenu));
            UIFactory.MenuButton(mm, Lines.MenuSettings, new Vector2(0.5f, 0.5f), new Vector2(0, y - 210), () => OpenSettings(_mainMenu));
            UIFactory.MenuButton(mm, Lines.MenuCredits, new Vector2(0.5f, 0.5f), new Vector2(0, y - 280), () => Open(_credits, null, _mainMenu));
            if (Application.platform != RuntimePlatform.WebGLPlayer)
                UIFactory.MenuButton(mm, Lines.MenuQuit, new Vector2(0.5f, 0.5f), new Vector2(0, y - 350), Application.Quit);
            UIFactory.Text(mm, "Footer", Lines.Footer, UIStyle.SansRegular, 15, UIStyle.Dim, TextAnchor.LowerCenter, 16f, new Vector2(0.5f, 0f), new Vector2(0, 40), new Vector2(1200, 30));

            // ---------------- instructions
            _instructions = Panel("Instructions", true);
            var ins = _instructions.transform;
            UIFactory.Text(ins, "Title", Lines.InstructionsTitle, UIStyle.Sans, 26, UIStyle.Bronze, TextAnchor.MiddleCenter, 36f, new Vector2(0.5f, 1f), new Vector2(0, -150), new Vector2(1200, 60));
            UIFactory.Text(ins, "Goal", Lines.InstructionsGoal, UIStyle.SerifItalic, 40, UIStyle.Cream, TextAnchor.MiddleCenter, 0f, new Vector2(0.5f, 1f), new Vector2(0, -230), new Vector2(1400, 70));
            var keys = UIFactory.Text(ins, "Keys", Lines.InstructionsKeyboard, UIStyle.SansRegular, 27, UIStyle.OffWhite, TextAnchor.UpperCenter, 4f, new Vector2(0.5f, 1f), new Vector2(0, -470), new Vector2(1200, 380));
            keys.lineSpacing = 1.25f;
            UIFactory.Text(ins, "Touch", Lines.InstructionsTouch, UIStyle.SerifItalic, 27, UIStyle.Dim, TextAnchor.UpperCenter, 0f, new Vector2(0.5f, 0f), new Vector2(0, 260), new Vector2(1300, 90));
            UIFactory.MenuButton(ins, Lines.MenuBack, new Vector2(0.5f, 0f), new Vector2(0, 150), () => Back(_instructions));

            // ---------------- credits
            _credits = Panel("Credits", true);
            var cr = _credits.transform;
            UIFactory.Text(cr, "Title", Lines.CreditsTitle, UIStyle.Sans, 26, UIStyle.Bronze, TextAnchor.MiddleCenter, 36f, new Vector2(0.5f, 1f), new Vector2(0, -170), new Vector2(1200, 60));
            var body = UIFactory.Text(cr, "Body", Lines.CreditsBody, UIStyle.SerifMedium, 33, UIStyle.Cream, TextAnchor.UpperCenter, 0f, new Vector2(0.5f, 1f), new Vector2(0, -430), new Vector2(1400, 440));
            body.lineSpacing = 1.15f;
            UIFactory.MenuButton(cr, Lines.MenuBack, new Vector2(0.5f, 0f), new Vector2(0, 150), () => Back(_credits));

            // ---------------- settings
            _settings = Panel("Settings", true);
            var st = _settings.transform;
            UIFactory.Text(st, "Title", Lines.SettingsTitle, UIStyle.Sans, 26, UIStyle.Bronze, TextAnchor.MiddleCenter, 36f, new Vector2(0.5f, 1f), new Vector2(0, -220), new Vector2(1200, 60));
            var a = AudioManager.I;
            UIFactory.Slider(st, Lines.SettingsMusic, new Vector2(0.5f, 0.5f), new Vector2(0, 120), a != null ? a.MusicVolume : 0.8f,
                v => AudioManager.I.SetVolumes(v, AudioManager.I.SfxVolume, AudioManager.I.AmbienceVolume));
            UIFactory.Slider(st, Lines.SettingsAmbience, new Vector2(0.5f, 0.5f), new Vector2(0, 40), a != null ? a.AmbienceVolume : 0.8f,
                v => AudioManager.I.SetVolumes(AudioManager.I.MusicVolume, AudioManager.I.SfxVolume, v));
            UIFactory.Slider(st, Lines.SettingsSfx, new Vector2(0.5f, 0.5f), new Vector2(0, -40), a != null ? a.SfxVolume : 0.9f,
                v => { AudioManager.I.SetVolumes(AudioManager.I.MusicVolume, v, AudioManager.I.AmbienceVolume); AudioManager.I.Sfx("ui_tick", 0.6f); });
            var fs = UIFactory.MenuButton(st, FullscreenLabel(), new Vector2(0.5f, 0.5f), new Vector2(0, -150), null, 24, 640f);
            _fullscreenLabel = fs.GetComponentInChildren<Text>();
            fs.onClick.AddListener(() =>
            {
                Screen.fullScreen = !Screen.fullScreen;
                StartCoroutine(RefreshFullscreenLabel());
            });
            UIFactory.MenuButton(st, Lines.MenuBack, new Vector2(0.5f, 0f), new Vector2(0, 150), () => Back(_settings));

            // ---------------- pause
            _pause = Panel("Pause", true);
            var pz = _pause.transform;
            UIFactory.Text(pz, "Title", Lines.PauseTitle, UIStyle.Serif, 76, UIStyle.Cream, TextAnchor.MiddleCenter, 30f, new Vector2(0.5f, 0.5f), new Vector2(0, 230), new Vector2(1200, 120));
            UIFactory.Image(pz, "Rule", null, UIStyle.Bronze, new Vector2(0.5f, 0.5f), new Vector2(0, 168), new Vector2(120, 2));
            _firstPause = UIFactory.MenuButton(pz, Lines.PauseResume, new Vector2(0.5f, 0.5f), new Vector2(0, 70), () => GameManager.I.SetPaused(false));
            UIFactory.MenuButton(pz, Lines.PauseRestart, new Vector2(0.5f, 0.5f), new Vector2(0, 0), () => { GameManager.I.SetPaused(false); GameManager.I.RestartLevel(); });
            UIFactory.MenuButton(pz, Lines.MenuSettings, new Vector2(0.5f, 0.5f), new Vector2(0, -70), () => OpenSettings(_pause));
            UIFactory.MenuButton(pz, Lines.MenuInstructions, new Vector2(0.5f, 0.5f), new Vector2(0, -140), () => Open(_instructions, null, _pause));
            UIFactory.MenuButton(pz, Lines.PauseMenu, new Vector2(0.5f, 0.5f), new Vector2(0, -210), () => { GameManager.I.SetPaused(false); GameManager.I.ToMenu(); });

            // ---------------- end screen
            _end = Panel("End", false);
            var en = _end.transform;
            var bgEnd = UIFactory.FullImage(en, "Background", UIStyle.Midnight);
            bgEnd.transform.SetAsFirstSibling();
            var lock_ = UIFactory.Image(en, "End Lockup", GameAssets.UISprite("end_lockup"), Color.white, new Vector2(0.5f, 0.5f), new Vector2(0, 150), new Vector2(1300, 422));
            lock_.preserveAspect = true;
            _endVerdict = UIFactory.Text(en, "Verdict", Lines.FinalVerdict, UIStyle.SerifItalic, 34, UIStyle.OffWhite, TextAnchor.MiddleCenter, 0f, new Vector2(0.5f, 0.5f), new Vector2(0, -130), new Vector2(1400, 60));
            _firstEnd = UIFactory.MenuButton(en, Lines.EndPlayAgain, new Vector2(0.5f, 0.5f), new Vector2(-260, -270), () => OnEndPlayAgain?.Invoke(), 28, 460f);
            UIFactory.MenuButton(en, Lines.EndMenu, new Vector2(0.5f, 0.5f), new Vector2(260, -270), () => OnEndMenu?.Invoke(), 28, 460f);
            var nav = _firstEnd.navigation;
            nav.mode = Navigation.Mode.Horizontal;
            _firstEnd.navigation = nav;
            HideAllPanels();
        }

        private static string FullscreenLabel() => Lines.SettingsFullscreen + ":  " + (Screen.fullScreen ? Lines.On : Lines.Off);

        private IEnumerator RefreshFullscreenLabel()
        {
            yield return Tween.Wait(0.2f, true);
            if (_fullscreenLabel != null) _fullscreenLabel.text = FullscreenLabel();
        }

        private CanvasGroup Panel(string name, bool dim)
        {
            var rt = UIFactory.Stretch(name, Safe);
            var g = rt.gameObject.AddComponent<CanvasGroup>();
            if (dim)
            {
                var bg = rt.gameObject.AddComponent<Image>();
                bg.color = new Color(0.02f, 0.06f, 0.1f, 0.86f);
                bg.raycastTarget = true;
            }
            rt.gameObject.SetActive(false);
            return g;
        }

        private void Open(CanvasGroup panel, Selectable first, CanvasGroup from)
        {
            _returnPanel = from;
            if (from != null) from.gameObject.SetActive(false);
            Show(panel, true);
            SelectFirst(panel, first);
        }

        private void OpenSettings(CanvasGroup from)
        {
            if (_fullscreenLabel != null) _fullscreenLabel.text = FullscreenLabel();
            Open(_settings, null, from);
        }

        private void Back(CanvasGroup current)
        {
            Show(current, false);
            var back = _returnPanel != null ? _returnPanel : _mainMenu;
            if (back == _pause && !(GameManager.I != null && GameManager.I.Paused)) back = _mainMenu;
            Show(back, true);
            SelectFirst(back, back == _pause ? _firstPause : back == _mainMenu ? _firstMain : null);
        }

        private void Show(CanvasGroup g, bool on)
        {
            g.gameObject.SetActive(on);
            if (on) StartCoroutine(FadeGroupUnscaled(g, 0f, 1f, 0.35f));
        }

        private static IEnumerator FadeGroupUnscaled(CanvasGroup g, float from, float to, float time)
        {
            g.alpha = from;
            yield return Tween.Run(time, k => g.alpha = Mathf.Lerp(from, to, k), Ease.InOutSine, true);
        }

        private static void SelectFirst(CanvasGroup panel, Selectable preferred)
        {
            if (EventSystem.current == null) return;
            var target = preferred != null ? preferred : panel.GetComponentInChildren<Selectable>();
            EventSystem.current.SetSelectedGameObject(null);
            if (target != null) EventSystem.current.SetSelectedGameObject(target.gameObject);
        }

        public void HideAllPanels()
        {
            foreach (var g in new[] { _mainMenu, _instructions, _settings, _credits, _pause, _end })
                if (g != null) g.gameObject.SetActive(false);
        }

        public void ShowMainMenu(bool canContinue)
        {
            HideAllPanels();
            _btnContinue.gameObject.SetActive(canContinue);
            Show(_mainMenu, true);
            SelectFirst(_mainMenu, canContinue ? _btnContinue : _firstMain);
        }

        public void HideMainMenu() => _mainMenu.gameObject.SetActive(false);

        public void ShowPause(bool on)
        {
            if (on)
            {
                Show(_pause, true);
                SelectFirst(_pause, _firstPause);
            }
            else
            {
                foreach (var g in new[] { _pause, _settings, _instructions })
                    if (g.gameObject.activeSelf && (g == _pause || _returnPanel == _pause)) g.gameObject.SetActive(false);
            }
        }

        public IEnumerator ShowEnd(string verdict)
        {
            HideAllPanels();
            _endVerdict.text = verdict;
            _end.gameObject.SetActive(true);
            yield return FadeGroupUnscaled(_end, 0f, 1f, 1.6f);
            SelectFirst(_end, _firstEnd);
        }

        public bool EndVisible => _end != null && _end.gameObject.activeSelf;
    }
}

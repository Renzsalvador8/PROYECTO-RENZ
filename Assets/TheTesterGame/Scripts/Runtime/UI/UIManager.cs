using System.Collections;
using System.Collections.Generic;
using TheTester.Core;
using UnityEngine;
using UnityEngine.UI;

namespace TheTester
{
    /// <summary>
    /// Persistent screen-space UI: HUD (objective + test progress), contextual prompt, captions, title cards,
    /// notebook panel, dwell ring, letterbox, fades and the film-grain/vignette finish. Menus live in UIManager.Menus.cs.
    /// Everything game-related sits inside a 16:9 "safe" rect matching the camera viewport.
    /// </summary>
    public sealed partial class UIManager : MonoBehaviour
    {
        public static UIManager I { get; private set; }
        public RectTransform Safe { get; private set; }
        public RectTransform ScreenRoot { get; private set; }
        public Canvas Canvas { get; private set; }

        private CanvasScaler _scaler;
        private Image _fade;
        private RectTransform _barTop, _barBottom;
        private CanvasGroup _hud;
        private Text _objLabel, _objText;
        private CanvasGroup _objGroup;
        private CanvasGroup _testsGroup;
        private Image[] _testDots;
        private RectTransform _prompt;
        private Text _promptText;
        private CanvasGroup _promptGroup;
        private Vector3 _promptWorld;
        private Text _caption;
        private CanvasGroup _captionGroup;
        private Coroutine _captionRoutine;
        private CanvasGroup _titleGroup;
        private Text _titleText, _titleSub;
        private Image _titleRule;
        private RawImage _grain;
        private RawImage _vignette;
        private Image _dwell;
        private RectTransform _speedRoot;
        private Text _speedText;
        private RectTransform _routeRoot;
        private Image _routeDot;
        private CanvasGroup _notebook;
        private Image _notebookBg;
        private RectTransform _notebookContent;
        private Text _nbTitle, _nbHint;
        private readonly Dictionary<string, Image> _nbChecks = new Dictionary<string, Image>();
        private readonly Dictionary<string, Text> _nbLabels = new Dictionary<string, Text>();
        private float _letterbox;
        private Coroutine _letterboxRoutine;
        private bool _promptVisible;
        private Coroutine _promptFade;

        private void Awake()
        {
            I = this;
            Canvas = gameObject.AddComponent<Canvas>();
            Canvas.renderMode = RenderMode.ScreenSpaceOverlay;
            Canvas.sortingOrder = 100;
            _scaler = gameObject.AddComponent<CanvasScaler>();
            _scaler.uiScaleMode = CanvasScaler.ScaleMode.ScaleWithScreenSize;
            _scaler.referenceResolution = new Vector2(1920, 1080);
            _scaler.screenMatchMode = CanvasScaler.ScreenMatchMode.MatchWidthOrHeight;
            gameObject.AddComponent<GraphicRaycaster>();
            ScreenRoot = (RectTransform)transform;

            Safe = UIFactory.Stretch("Safe 16:9", transform);
            var fit = Safe.gameObject.AddComponent<AspectRatioFitter>();
            fit.aspectMode = AspectRatioFitter.AspectMode.FitInParent;
            fit.aspectRatio = 16f / 9f;

            BuildFinish();
            BuildLetterbox();
            BuildPrompt();
            BuildHud();
            BuildCaption();
            BuildTitle();
            BuildNotebook();
            BuildDwell();
            BuildMenus();
            BuildTouch();
            _fade = UIFactory.FullImage(transform, "Fade", UIStyle.Midnight);
            _fade.raycastTarget = false;
            UpdateScaler();
        }

        private void UpdateScaler()
        {
            float aspect = (float)Screen.width / Mathf.Max(1, Screen.height);
            _scaler.matchWidthOrHeight = aspect > 16f / 9f ? 1f : 0f;
        }

        private void Update()
        {
            UpdateScaler();
            if (_grain != null)
            {
                var r = _grain.uvRect;
                r.x = Random.value;
                r.y = Random.value;
                _grain.uvRect = r;
            }
            if (_promptVisible) PositionPrompt();
            UpdateTouch();
        }

        /// <summary>Called when a scene starts: hide transient UI.</summary>
        public void ResetForScene()
        {
            HidePrompt();
            HideCaption();
            SetHudVisible(false);
            SetSpeedVisible(false);
            SetRouteVisible(false);
            CloseNotebook(true);
            SetDwell(false, Vector2.zero, 0f, 0f);
            SetLetterbox(0f, 0f);
            HideAllPanels();
            _titleGroup.alpha = 0f;
            SetTouchMode(TouchLayout.None);
        }

        // ------------------------------------------------------------------ finish (grain + vignette)
        private void BuildFinish()
        {
            _vignette = Stretched<RawImage>("Vignette");
            _vignette.texture = GameAssets.Texture("UI/vignette");
            _vignette.color = new Color(1, 1, 1, 0.62f);
            _grain = Stretched<RawImage>("Grain");
            var gt = GameAssets.Texture("UI/grain");
            gt.wrapMode = TextureWrapMode.Repeat;
            _grain.texture = gt;
            _grain.uvRect = new Rect(0, 0, 1920f / 256f, 1080f / 256f);
            _grain.color = new Color(1, 1, 1, 0.075f);
        }

        private T Stretched<T>(string name) where T : Graphic
        {
            var rt = UIFactory.Stretch(name, Safe);
            var g = rt.gameObject.AddComponent<T>();
            g.raycastTarget = false;
            return g;
        }

        public void SetFinish(float vignette, float grain)
        {
            UIFactory.SetAlpha(_vignette, vignette);
            UIFactory.SetAlpha(_grain, grain);
        }

        // ------------------------------------------------------------------ fades & letterbox
        public IEnumerator FadeOut(float time = 0.8f)
        {
            _fade.raycastTarget = true;
            float from = _fade.color.a;
            yield return Tween.Run(time, k => UIFactory.SetAlpha(_fade, Mathf.Lerp(from, 1f, k)), Ease.InOutSine, true);
        }

        public IEnumerator FadeIn(float time = 1.0f)
        {
            float from = _fade.color.a;
            yield return Tween.Run(time, k => UIFactory.SetAlpha(_fade, Mathf.Lerp(from, 0f, k)), Ease.InOutSine, true);
            _fade.raycastTarget = false;
        }

        public void SetFadeInstant(float a)
        {
            UIFactory.SetAlpha(_fade, a);
            _fade.raycastTarget = a > 0.5f;
        }

        private void BuildLetterbox()
        {
            _barTop = UIFactory.Rect("Bar Top", Safe, new Vector2(0, 1), new Vector2(1, 1), new Vector2(0.5f, 1f), Vector2.zero, new Vector2(0, 0));
            _barTop.gameObject.AddComponent<Image>().color = new Color(0.02f, 0.04f, 0.07f, 1f);
            _barBottom = UIFactory.Rect("Bar Bottom", Safe, new Vector2(0, 0), new Vector2(1, 0), new Vector2(0.5f, 0f), Vector2.zero, new Vector2(0, 0));
            _barBottom.gameObject.AddComponent<Image>().color = new Color(0.02f, 0.04f, 0.07f, 1f);
            _barTop.GetComponent<Image>().raycastTarget = false;
            _barBottom.GetComponent<Image>().raycastTarget = false;
        }

        /// <summary>Cinematic bars (0 = none, 1 = full 2.39:1 framing).</summary>
        public void SetLetterbox(float amount, float time = 0.8f)
        {
            if (_letterboxRoutine != null) StopCoroutine(_letterboxRoutine);
            if (time <= 0f) { ApplyLetterbox(amount); return; }
            float from = _letterbox;
            _letterboxRoutine = StartCoroutine(Tween.Run(time, k => ApplyLetterbox(Mathf.Lerp(from, amount, k)), Ease.InOutSine));
        }

        private void ApplyLetterbox(float a)
        {
            _letterbox = a;
            float h = 128f * a;
            _barTop.sizeDelta = new Vector2(0, h);
            _barBottom.sizeDelta = new Vector2(0, h);
        }

        // ------------------------------------------------------------------ prompt
        private void BuildPrompt()
        {
            _prompt = UIFactory.Rect("Prompt", Safe, new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0.5f), new Vector2(0.5f, 0f), Vector2.zero, new Vector2(700, 70));
            _promptGroup = _prompt.gameObject.AddComponent<CanvasGroup>();
            _promptGroup.alpha = 0f;
            _promptGroup.blocksRaycasts = false;
            _promptText = UIFactory.Text(_prompt, "Text", "", UIStyle.Sans, 20, UIStyle.Cream, TextAnchor.MiddleCenter, 22f, null, new Vector2(0, 18), new Vector2(700, 40));
            var shadow = _promptText.gameObject.AddComponent<Shadow>();
            shadow.effectColor = new Color(0, 0, 0, 0.6f);
            shadow.effectDistance = new Vector2(1, -2);
            UIFactory.Image(_prompt, "Rule", null, UIStyle.Bronze, new Vector2(0.5f, 0.5f), new Vector2(0, -4), new Vector2(90, 2));
            UIFactory.Image(_prompt, "Pin", GameAssets.UISprite("circle"), UIStyle.Cream, new Vector2(0.5f, 0.5f), new Vector2(0, -22), new Vector2(7, 7));
        }

        public void ShowPrompt(string text, Vector3 worldAnchor)
        {
            _promptText.text = GameInput.TouchMode ? Lines.TouchPrompt(text) : text;
            _promptWorld = worldAnchor;
            _promptVisible = true;
            PositionPrompt();
            if (_promptFade != null) StopCoroutine(_promptFade);
            _promptFade = StartCoroutine(PromptFade(1f));
            if (AudioManager.I != null) AudioManager.I.Sfx("ui_tick", 0.15f);
        }

        public void MovePrompt(Vector3 worldAnchor) => _promptWorld = worldAnchor;

        public void HidePrompt()
        {
            if (!_promptVisible) return;
            _promptVisible = false;
            if (_promptFade != null) StopCoroutine(_promptFade);
            _promptFade = StartCoroutine(PromptFade(0f));
        }

        public bool PromptVisible => _promptVisible;

        private IEnumerator PromptFade(float to)
        {
            float from = _promptGroup.alpha;
            yield return Tween.Run(0.25f, k => _promptGroup.alpha = Mathf.Lerp(from, to, k), Ease.Linear, true);
        }

        private void PositionPrompt()
        {
            var cam = GameManager.I != null && GameManager.I.Director != null ? GameManager.I.Director.Cam : null;
            if (cam == null) return;
            Vector2 sp = cam.WorldToScreen(_promptWorld);
            if (RectTransformUtility.ScreenPointToLocalPointInRectangle(Safe, sp, null, out var local))
            {
                local.x = Mathf.Clamp(local.x, -Safe.rect.width / 2 + 360, Safe.rect.width / 2 - 360);
                _prompt.anchoredPosition = local + new Vector2(0, 8f + Mathf.Sin(Time.unscaledTime * 2f) * 3f);
            }
        }

        /// <summary>Converts a world point to a position in the safe rect (for world-anchored UI).</summary>
        public Vector2 WorldToSafe(Vector3 world)
        {
            var cam = GameManager.I != null && GameManager.I.Director != null ? GameManager.I.Director.Cam : null;
            if (cam == null) return Vector2.zero;
            RectTransformUtility.ScreenPointToLocalPointInRectangle(Safe, cam.WorldToScreen(world), null, out var local);
            return local;
        }

        public float WorldUnitsToSafePixels(float units)
        {
            var cam = GameManager.I != null && GameManager.I.Director != null ? GameManager.I.Director.Cam : null;
            if (cam == null) return units * 100f;
            return units * Safe.rect.height / (2f * cam.Cam.orthographicSize);
        }

        // ------------------------------------------------------------------ HUD
        private void BuildHud()
        {
            var root = UIFactory.Stretch("HUD", Safe);
            _hud = root.gameObject.AddComponent<CanvasGroup>();
            _hud.blocksRaycasts = false;
            var obj = UIFactory.Rect("Objective", root, new Vector2(0, 1), new Vector2(0, 1), new Vector2(0, 1), new Vector2(72, -58), new Vector2(900, 110));
            _objGroup = obj.gameObject.AddComponent<CanvasGroup>();
            _objLabel = UIFactory.Text(obj, "Label", Lines.ObjectiveLabel, UIStyle.Sans, 16, UIStyle.Bronze, TextAnchor.UpperLeft, 30f,
                new Vector2(0, 1), new Vector2(450, -14), new Vector2(900, 30));
            _objText = UIFactory.Text(obj, "Text", "", UIStyle.SerifMediumItalic, 32, UIStyle.Cream, TextAnchor.UpperLeft, 0f,
                new Vector2(0, 1), new Vector2(450, -62), new Vector2(900, 60));
            var sh = _objText.gameObject.AddComponent<Shadow>();
            sh.effectColor = new Color(0, 0, 0, 0.5f);
            sh.effectDistance = new Vector2(1, -2);

            var tests = UIFactory.Rect("Tests", root, new Vector2(1, 1), new Vector2(1, 1), new Vector2(1, 1), new Vector2(-72, -58), new Vector2(260, 90));
            _testsGroup = tests.gameObject.AddComponent<CanvasGroup>();
            UIFactory.Text(tests, "Label", Lines.TestsLabel, UIStyle.Sans, 16, UIStyle.Bronze, TextAnchor.UpperRight, 30f,
                new Vector2(1, 1), new Vector2(-130, -14), new Vector2(260, 30));
            _testDots = new Image[3];
            for (int i = 0; i < 3; i++)
            {
                float x = -200 + i * 70;
                UIFactory.Image(tests, "Ring " + i, GameAssets.UISprite("ring"), UIStyle.Cream, new Vector2(1, 1), new Vector2(x, -56), new Vector2(26, 26));
                _testDots[i] = UIFactory.Image(tests, "Dot " + i, GameAssets.UISprite("circle"), UIStyle.Bronze, new Vector2(1, 1), new Vector2(x, -56), new Vector2(14, 14));
                UIFactory.Text(tests, "Num " + i, "0" + (i + 1), UIStyle.SansRegular, 13, UIStyle.Dim, TextAnchor.MiddleCenter, 10f,
                    new Vector2(1, 1), new Vector2(x, -84), new Vector2(60, 20));
            }
            // speedometer (drive)
            _speedRoot = UIFactory.Rect("Speed", root, new Vector2(0.5f, 0), new Vector2(0.5f, 0), new Vector2(0.5f, 0), new Vector2(0, 54), new Vector2(300, 110));
            _speedText = UIFactory.Text(_speedRoot, "Value", "0", UIStyle.SansLight, 64, UIStyle.Cream, TextAnchor.LowerCenter, 0f, new Vector2(0.5f, 0), new Vector2(0, 52), new Vector2(300, 80));
            UIFactory.Text(_speedRoot, "Unit", "KM/H", UIStyle.Sans, 15, UIStyle.Bronze, TextAnchor.LowerCenter, 30f, new Vector2(0.5f, 0), new Vector2(0, 18), new Vector2(300, 30));
            // route progress (drive)
            _routeRoot = UIFactory.Rect("Route", root, new Vector2(0.5f, 1), new Vector2(0.5f, 1), new Vector2(0.5f, 1), new Vector2(0, -64), new Vector2(520, 20));
            UIFactory.Image(_routeRoot, "Line", null, new Color(1, 1, 1, 0.3f), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(520, 2));
            _routeDot = UIFactory.Image(_routeRoot, "Dot", GameAssets.UISprite("circle"), UIStyle.Bronze, new Vector2(0.5f, 0.5f), new Vector2(-260, 0), new Vector2(14, 14));
            UIFactory.Image(_routeRoot, "End", GameAssets.UISprite("ring"), UIStyle.Cream, new Vector2(0.5f, 0.5f), new Vector2(260, 0), new Vector2(18, 18));
            SetHudVisible(false);
        }

        public void SetHudVisible(bool visible, bool showTests = true)
        {
            StartCoroutine(FadeGroup(_hud, visible ? 1f : 0f, 0.6f));
            _testsGroup.alpha = showTests ? 1f : 0f;
        }

        public void SetObjective(string text)
        {
            if (_objText.text == text) return;
            StartCoroutine(ObjectiveSwap(text));
        }

        private IEnumerator ObjectiveSwap(string text)
        {
            yield return FadeGroup(_objGroup, 0f, 0.3f);
            _objText.text = text;
            _objLabel.enabled = !string.IsNullOrEmpty(text);
            yield return FadeGroup(_objGroup, 1f, 0.6f);
        }

        public void SetTests(GameProgress p)
        {
            for (int i = 0; i < 3; i++) _testDots[i].enabled = p.IsDone((TestId)i);
        }

        public void PulseTest(int index)
        {
            if (index < 0 || index > 2) return;
            _testDots[index].enabled = true;
            StartCoroutine(Tween.Run(0.9f, k => _testDots[index].rectTransform.localScale = Vector3.one * (1f + 0.8f * Mathf.Sin(k * Mathf.PI)), Ease.Linear));
        }

        public void SetSpeedVisible(bool v) => _speedRoot.gameObject.SetActive(v);
        public void SetSpeed(float kmh) => _speedText.text = Mathf.RoundToInt(kmh).ToString();
        public void SetRouteVisible(bool v) => _routeRoot.gameObject.SetActive(v);
        public void SetRoute(float t) => _routeDot.rectTransform.anchoredPosition = new Vector2(Mathf.Lerp(-260f, 260f, Mathf.Clamp01(t)), 0f);

        private static IEnumerator FadeGroup(CanvasGroup g, float to, float time)
        {
            float from = g.alpha;
            yield return Tween.Run(time, k => g.alpha = Mathf.Lerp(from, to, k), Ease.InOutSine, true);
        }

        // ------------------------------------------------------------------ captions
        private void BuildCaption()
        {
            var root = UIFactory.Rect("Caption", Safe, new Vector2(0.5f, 0), new Vector2(0.5f, 0), new Vector2(0.5f, 0), new Vector2(0, 150), new Vector2(1500, 140));
            _captionGroup = root.gameObject.AddComponent<CanvasGroup>();
            _captionGroup.alpha = 0f;
            _captionGroup.blocksRaycasts = false;
            var band = UIFactory.Image(root, "Band", GameAssets.UISprite("circle_soft"), new Color(0.02f, 0.05f, 0.09f, 0.55f), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(1500, 170));
            band.type = Image.Type.Simple;
            _caption = UIFactory.Text(root, "Text", "", UIStyle.SerifMediumItalic, 40, UIStyle.Cream, TextAnchor.MiddleCenter, 0f, null, Vector2.zero, new Vector2(1300, 130));
            var sh = _caption.gameObject.AddComponent<Shadow>();
            sh.effectColor = new Color(0, 0, 0, 0.7f);
            sh.effectDistance = new Vector2(1, -2);
        }

        public static float ReadingTime(string line) => Mathf.Clamp(1.4f + line.Length * 0.055f, 1.8f, 6.5f);

        public void Caption(string text, float duration = -1f)
        {
            if (duration < 0f) duration = ReadingTime(text);
            if (_captionRoutine != null) StopCoroutine(_captionRoutine);
            _captionRoutine = StartCoroutine(CaptionRoutine(text, duration));
        }

        public void HideCaption()
        {
            if (_captionRoutine != null) StopCoroutine(_captionRoutine);
            _captionGroup.alpha = 0f;
        }

        public string CurrentCaption => _captionGroup.alpha > 0.05f ? _caption.text : "";

        private IEnumerator CaptionRoutine(string text, float duration)
        {
            if (_captionGroup.alpha > 0.01f) yield return FadeGroup(_captionGroup, 0f, 0.15f);
            _caption.text = text;
            yield return FadeGroup(_captionGroup, 1f, 0.35f);
            yield return Tween.Wait(duration);
            yield return FadeGroup(_captionGroup, 0f, 0.5f);
            _captionRoutine = null;
        }

        // ------------------------------------------------------------------ title cards
        private void BuildTitle()
        {
            var root = UIFactory.Stretch("Title Card", Safe);
            _titleGroup = root.gameObject.AddComponent<CanvasGroup>();
            _titleGroup.alpha = 0f;
            _titleGroup.blocksRaycasts = false;
            _titleText = UIFactory.Text(root, "Title", "", UIStyle.Serif, 84, UIStyle.Cream, TextAnchor.MiddleCenter, 16f, null, new Vector2(0, 30), new Vector2(1700, 140));
            _titleRule = UIFactory.Image(root, "Rule", null, UIStyle.Bronze, new Vector2(0.5f, 0.5f), new Vector2(0, -42), new Vector2(160, 2));
            _titleSub = UIFactory.Text(root, "Sub", "", UIStyle.SerifItalic, 34, UIStyle.OffWhite, TextAnchor.MiddleCenter, 0f, null, new Vector2(0, -92), new Vector2(1500, 80));
        }

        /// <summary>Elegant centred title card (fade in, hold, fade out).</summary>
        public IEnumerator TitleCard(string title, string sub, float hold, int size = 84, bool small = false)
        {
            _titleText.text = title;
            _titleText.fontSize = size;
            _titleText.font = GameAssets.Font(small ? UIStyle.Sans : UIStyle.Serif);
            _titleText.GetComponent<LetterSpacing>().Spacing = small ? 36f : 16f;
            _titleSub.text = sub ?? "";
            _titleRule.enabled = !string.IsNullOrEmpty(sub) || !small;
            var rt = _titleText.rectTransform;
            yield return Tween.Run(0.9f, k => { _titleGroup.alpha = k; rt.localScale = Vector3.one * Mathf.Lerp(1.04f, 1f, k); }, Ease.OutCubic);
            yield return Tween.Wait(hold);
            yield return Tween.Run(0.8f, k => _titleGroup.alpha = 1f - k, Ease.InOutSine);
        }

        // ------------------------------------------------------------------ notebook
        private void BuildNotebook()
        {
            // left side: none of the inspection targets sit under it
            var root = UIFactory.Rect("Notebook", Safe, new Vector2(0, 0.5f), new Vector2(0, 0.5f), new Vector2(0, 0.5f), new Vector2(40, 0), new Vector2(470, 860));
            _notebook = root.gameObject.AddComponent<CanvasGroup>();
            _notebook.alpha = 0f;
            _notebook.blocksRaycasts = false;
            var bg = root.gameObject.AddComponent<Image>();
            bg.sprite = GameAssets.UISprite("paper_card", 40f);
            bg.type = Image.Type.Sliced;
            bg.color = new Color(1f, 1f, 1f, 0.96f);
            bg.raycastTarget = true;
            root.gameObject.AddComponent<UIBlocker>();
            _notebookBg = bg;
            _nbTitle = UIFactory.Text(root, "Title", "", UIStyle.Sans, 20, UIStyle.Ink, TextAnchor.UpperLeft, 20f, new Vector2(0, 1), new Vector2(235, -44), new Vector2(400, 40));
            _nbHint = UIFactory.Text(root, "Hint", "", UIStyle.SerifItalic, 23, new Color32(80, 70, 62, 255), TextAnchor.UpperLeft, 0f, new Vector2(0, 1), new Vector2(235, -112), new Vector2(400, 90));
            _notebookContent = UIFactory.Rect("Entries", root, new Vector2(0, 1), new Vector2(0, 1), new Vector2(0, 1), new Vector2(34, -200), new Vector2(400, 640));
        }

        public struct NotebookEntry
        {
            public string Id;
            public string Label;
            public string Detail;
            public Sprite Image;
        }

        public void OpenNotebook(string title, string hint, IList<NotebookEntry> entries)
        {
            foreach (Transform c in _notebookContent) Destroy(c.gameObject);
            _nbChecks.Clear();
            _nbLabels.Clear();
            _nbTitle.text = title;
            _nbHint.text = hint;
            float y = 0f;
            foreach (var e in entries)
            {
                bool big = e.Image != null;
                float rowH = big ? 152f : 64f;
                var row = UIFactory.Rect("Entry · " + e.Id, _notebookContent, new Vector2(0, 1), new Vector2(0, 1), new Vector2(0, 1), new Vector2(0, -y), new Vector2(400, rowH));
                UIFactory.Image(row, "Box", GameAssets.UISprite("ring"), UIStyle.Ink, new Vector2(0, 1), new Vector2(14, -22), new Vector2(24, 24));
                var check = UIFactory.Image(row, "Check", GameAssets.UISprite("check"), UIStyle.Bronze, new Vector2(0, 1), new Vector2(17, -20), new Vector2(34, 34));
                check.enabled = false;
                _nbChecks[e.Id] = check;
                if (big)
                {
                    var img = UIFactory.Image(row, "Clue", e.Image, Color.white, new Vector2(0, 1), new Vector2(128, -70), new Vector2(176, 126));
                    img.preserveAspect = true;
                    var lbl = UIFactory.Text(row, "Label", e.Label, UIStyle.SerifItalic, 22, UIStyle.Ink, TextAnchor.UpperLeft, 0f, new Vector2(0, 1), new Vector2(310, -64), new Vector2(160, 120));
                    _nbLabels[e.Id] = lbl;
                }
                else
                {
                    var lbl = UIFactory.Text(row, "Label", e.Label, UIStyle.Sans, 19, UIStyle.Ink, TextAnchor.MiddleLeft, 14f, new Vector2(0, 1), new Vector2(232, -22), new Vector2(360, 40));
                    _nbLabels[e.Id] = lbl;
                }
                y += rowH;
            }
            _notebookBg.raycastTarget = true;
            StartCoroutine(FadeGroup(_notebook, 1f, 0.6f));
            if (AudioManager.I != null) AudioManager.I.Sfx("cloth_2", 0.35f);
        }

        public void CheckNotebook(string id)
        {
            if (!_nbChecks.TryGetValue(id, out var check)) return;
            check.enabled = true;
            var rt = check.rectTransform;
            StartCoroutine(Tween.Run(0.35f, k => rt.localScale = Vector3.one * Ease.OutBack(k), Ease.Linear));
            if (_nbLabels.TryGetValue(id, out var lbl)) lbl.color = new Color32(110, 96, 86, 255);
            if (AudioManager.I != null) AudioManager.I.Sfx("scribble", 0.5f);
        }

        public void CloseNotebook(bool instant = false)
        {
            _notebookBg.raycastTarget = false;
            if (instant) { _notebook.alpha = 0f; return; }
            StartCoroutine(FadeGroup(_notebook, 0f, 0.5f));
        }

        // ------------------------------------------------------------------ dwell ring (inspection)
        private void BuildDwell()
        {
            _dwell = UIFactory.Image(Safe, "Dwell Ring", GameAssets.UISprite("ring"), UIStyle.Bronze, new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(200, 200));
            _dwell.type = Image.Type.Filled;
            _dwell.fillMethod = Image.FillMethod.Radial360;
            _dwell.fillOrigin = (int)Image.Origin360.Top;
            _dwell.fillClockwise = true;
            _dwell.enabled = false;
        }

        public void SetDwell(bool visible, Vector2 safePos, float radiusPx, float fill)
        {
            _dwell.enabled = visible && fill > 0.001f;
            if (!_dwell.enabled) return;
            _dwell.rectTransform.anchoredPosition = safePos;
            _dwell.rectTransform.sizeDelta = Vector2.one * (radiusPx * 2f + 26f);
            _dwell.fillAmount = fill;
        }
    }
}

using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace TheTester
{
    public enum TouchLayout { None, Walk, Inspect, Drive }

    public sealed partial class UIManager
    {
        private RectTransform _touchRoot;
        private GameObject _tWalk, _tInspect, _tDrive, _tPause;
        private TouchLayout _touchLayout = TouchLayout.None;

        private void BuildTouch()
        {
            _touchRoot = UIFactory.Stretch("Touch Controls", transform);
            _tPause = TouchBtn(_touchRoot, "Pause", "pause", VirtualButton.Pause, new Vector2(1, 1), new Vector2(-70, -70), 96, null).gameObject;

            _tWalk = new GameObject("Walk", typeof(RectTransform));
            _tWalk.transform.SetParent(_touchRoot, false);
            Fill(_tWalk);
            TouchBtn(_tWalk.transform, "Left", "arrow_left", VirtualButton.Left, new Vector2(0, 0), new Vector2(130, 130), 170, null);
            TouchBtn(_tWalk.transform, "Right", "arrow_right", VirtualButton.Right, new Vector2(0, 0), new Vector2(330, 130), 170, null);
            TouchBtn(_tWalk.transform, "Action", "circle", VirtualButton.Interact, new Vector2(1, 0), new Vector2(-150, 140), 180, "E");

            _tInspect = new GameObject("Inspect", typeof(RectTransform));
            _tInspect.transform.SetParent(_touchRoot, false);
            Fill(_tInspect);
            TouchBtn(_tInspect.transform, "Action", "circle", VirtualButton.Interact, new Vector2(1, 0), new Vector2(-150, 140), 160, "E");

            _tDrive = new GameObject("Drive", typeof(RectTransform));
            _tDrive.transform.SetParent(_touchRoot, false);
            Fill(_tDrive);
            TouchBtn(_tDrive.transform, "Brake", "circle", VirtualButton.Brake, new Vector2(0, 0), new Vector2(150, 150), 200, "FRENO");
            TouchBtn(_tDrive.transform, "Throttle", "circle", VirtualButton.Throttle, new Vector2(1, 0), new Vector2(-150, 150), 220, "ACELERAR");
            TouchBtn(_tDrive.transform, "Up", "chevron_up", VirtualButton.Up, new Vector2(1, 0), new Vector2(-370, 250), 140, null);
            TouchBtn(_tDrive.transform, "Down", "chevron_down", VirtualButton.Down, new Vector2(1, 0), new Vector2(-370, 90), 140, null);
            TouchBtn(_tDrive.transform, "Horn", "circle", VirtualButton.Action, new Vector2(0, 0), new Vector2(370, 120), 110, "CLAXON");
            SetTouchMode(TouchLayout.None);
        }

        private static void Fill(GameObject go)
        {
            var rt = (RectTransform)go.transform;
            rt.anchorMin = Vector2.zero;
            rt.anchorMax = Vector2.one;
            rt.sizeDelta = Vector2.zero;
        }

        private static TouchButton TouchBtn(Transform parent, string name, string sprite, VirtualButton b, Vector2 anchor, Vector2 pos, float size, string label)
        {
            var img = UIFactory.Image(parent, name, GameAssets.UISprite(sprite), Color.white, anchor, pos, new Vector2(size, size), true);
            if (sprite == "circle") img.color = new Color(0.04f, 0.1f, 0.18f, 0.55f);
            if (sprite == "pause")
            {
                var bg = UIFactory.Image(img.transform, "Bg", GameAssets.UISprite("circle"), new Color(0.04f, 0.1f, 0.18f, 0.5f), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(size, size));
                bg.transform.SetAsFirstSibling();
            }
            if (label != null)
            {
                UIFactory.Text(img.transform, "Label", label, UIStyle.Sans, label.Length > 2 ? 20 : 44, UIStyle.Cream, TextAnchor.MiddleCenter,
                    label.Length > 2 ? 14f : 0f, null, Vector2.zero, new Vector2(size, size));
                UIFactory.Image(img.transform, "Ring", GameAssets.UISprite("ring"), new Color(1, 1, 1, 0.6f), new Vector2(0.5f, 0.5f), Vector2.zero, new Vector2(size, size));
            }
            var tb = img.gameObject.AddComponent<TouchButton>();
            tb.Button = b;
            return tb;
        }

        public void SetTouchMode(TouchLayout layout)
        {
            _touchLayout = layout;
            UpdateTouch();
        }

        private void UpdateTouch()
        {
            if (_touchRoot == null) return;
            bool on = GameInput.TouchMode;
            bool paused = GameManager.I != null && GameManager.I.Paused;
            _touchRoot.gameObject.SetActive(on);
            if (!on) return;
            _tWalk.SetActive(!paused && _touchLayout == TouchLayout.Walk);
            _tInspect.SetActive(!paused && _touchLayout == TouchLayout.Inspect);
            _tDrive.SetActive(!paused && _touchLayout == TouchLayout.Drive);
            _tPause.SetActive(!paused && _touchLayout != TouchLayout.None);
        }
    }
}

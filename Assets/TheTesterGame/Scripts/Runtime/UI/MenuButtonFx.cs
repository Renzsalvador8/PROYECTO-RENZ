using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace TheTester
{
    /// <summary>Hover/selection feedback for MenuButton (underline growth + colour), restrained timing.</summary>
    public sealed class MenuButtonFx : MonoBehaviour, ISelectHandler, IDeselectHandler, IPointerEnterHandler, IPointerExitHandler
    {
        private Text _text;
        private RectTransform _line;
        private float _width;
        private float _k, _target;

        public void Init(Text text, RectTransform line, float width)
        {
            _text = text;
            _line = line;
            _width = width;
        }

        public void OnSelect(BaseEventData e) { _target = 1f; Tick(); }
        public void OnDeselect(BaseEventData e) => _target = 0f;
        public void OnPointerEnter(PointerEventData e)
        {
            if (EventSystem.current != null) EventSystem.current.SetSelectedGameObject(gameObject);
        }
        public void OnPointerExit(PointerEventData e) { }

        private static void Tick()
        {
            if (AudioManager.I != null) AudioManager.I.Sfx("ui_tick", 0.25f);
        }

        private void OnDisable() { _k = 0f; _target = 0f; Apply(); }

        private void Update()
        {
            _k = Mathf.MoveTowards(_k, _target, Time.unscaledDeltaTime * 5f);
            Apply();
        }

        private void Apply()
        {
            if (_line == null) return;
            float e = Ease.OutCubic(_k);
            _line.sizeDelta = new Vector2(_width * e, 2f);
            _text.color = Color.Lerp(UIStyle.OffWhite, UIStyle.Cream, e);
            _text.transform.localScale = Vector3.one * (1f + 0.03f * e);
        }
    }
}

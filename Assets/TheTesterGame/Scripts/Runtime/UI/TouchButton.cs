using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;

namespace TheTester
{
    /// <summary>On-screen button feeding GameInput's virtual buttons (multi-touch safe).</summary>
    public sealed class TouchButton : MonoBehaviour, IPointerDownHandler, IPointerUpHandler, IPointerExitHandler
    {
        public VirtualButton Button;
        private Image _img;
        private bool _held;

        private void Awake() => _img = GetComponent<Image>();

        public void OnPointerDown(PointerEventData e) => Set(true);
        public void OnPointerUp(PointerEventData e) => Set(false);
        public void OnPointerExit(PointerEventData e) => Set(false);
        private void OnDisable() => Set(false);

        private void Set(bool held)
        {
            if (_held == held) return;
            _held = held;
            GameInput.SetVirtual(Button, held);
            if (_img != null) _img.color = held ? new Color(1f, 0.85f, 0.75f, 1f) : Color.white;
            transform.localScale = held ? Vector3.one * 0.92f : Vector3.one;
        }
    }
}

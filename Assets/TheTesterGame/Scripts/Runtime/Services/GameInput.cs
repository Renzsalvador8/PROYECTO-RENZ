using UnityEngine;
using UnityEngine.EventSystems;
#if TT_INPUT_SYSTEM && ENABLE_INPUT_SYSTEM
using UnityEngine.InputSystem;
#endif

namespace TheTester
{
    public enum VirtualButton { Left, Right, Interact, Action, Pause, Up, Down, Throttle, Brake, Count }

    /// <summary>
    /// One place for all player input: keyboard, mouse and touch (Input System package when active,
    /// legacy Input Manager otherwise), plus on-screen touch buttons and a simulation hook for tests.
    /// Edge states ("Down") are valid for exactly one frame; GameInputUpdater refreshes them early each frame.
    /// </summary>
    public static class GameInput
    {
        public static float MoveX { get; private set; }
        public static bool InteractDown { get; private set; }
        public static bool ActionDown { get; private set; }
        public static bool PauseDown { get; private set; }
        public static bool UpDown { get; private set; }
        public static bool DownDown { get; private set; }
        public static bool ThrottleHeld { get; private set; }
        public static bool BrakeHeld { get; private set; }
        public static bool LensKeysActive { get; private set; }
        public static Vector2 LensKeys { get; private set; }

        public static Vector2 PointerScreen { get; private set; }
        public static bool PointerHeld { get; private set; }
        public static bool PointerDown { get; private set; }
        public static bool PointerMoved { get; private set; }
        public static bool PointerOverUI { get; private set; }

        /// <summary>True once a touch has been seen or the platform is mobile — shows touch controls.</summary>
        public static bool TouchMode { get; private set; }

        /// <summary>Simulated input used by automated tests/autoplay. Null in normal play.</summary>
        public static InputSimulation Simulation;

        private static readonly bool[] VirtualHeld = new bool[(int)VirtualButton.Count];
        private static readonly bool[] VirtualPrev = new bool[(int)VirtualButton.Count];
        private static Vector2 _lastPointer;
        private static int _lastFrame = -1;

        public static void SetVirtual(VirtualButton b, bool held) => VirtualHeld[(int)b] = held;

        public static void ClearVirtual()
        {
            for (int i = 0; i < VirtualHeld.Length; i++) VirtualHeld[i] = false;
        }

        public static void ForceTouchMode(bool on) => TouchMode = on;

        private static bool VDown(VirtualButton b) => VirtualHeld[(int)b] && !VirtualPrev[(int)b];
        private static bool VHeld(VirtualButton b) => VirtualHeld[(int)b];

        internal static void Refresh()
        {
            if (_lastFrame == Time.frameCount) return;
            _lastFrame = Time.frameCount;
            if (!TouchMode && Application.isMobilePlatform) TouchMode = true;

            float move = 0f;
            bool interact = false, action = false, pause = false, up = false, down = false, throttle = false, brake = false;
            Vector2 lens = Vector2.zero;
            Vector2 pointer = PointerScreen;
            bool pHeld = false, pDown = false;

#if TT_INPUT_SYSTEM && ENABLE_INPUT_SYSTEM
            var kb = Keyboard.current;
            if (kb != null)
            {
                bool left = kb.aKey.isPressed || kb.leftArrowKey.isPressed;
                bool right = kb.dKey.isPressed || kb.rightArrowKey.isPressed;
                move = (right ? 1f : 0f) - (left ? 1f : 0f);
                interact = kb.eKey.wasPressedThisFrame || kb.enterKey.wasPressedThisFrame || kb.numpadEnterKey.wasPressedThisFrame;
                action = kb.spaceKey.wasPressedThisFrame;
                pause = kb.escapeKey.wasPressedThisFrame || kb.pKey.wasPressedThisFrame;
                up = kb.wKey.wasPressedThisFrame || kb.upArrowKey.wasPressedThisFrame;
                down = kb.sKey.wasPressedThisFrame || kb.downArrowKey.wasPressedThisFrame;
                throttle = right;
                brake = left;
                lens = new Vector2(move, (kb.wKey.isPressed || kb.upArrowKey.isPressed ? 1f : 0f) - (kb.sKey.isPressed || kb.downArrowKey.isPressed ? 1f : 0f));
            }
            var ts = Touchscreen.current;
            bool touching = false;
            if (ts != null)
            {
                var t = ts.primaryTouch;
                if (t.press.isPressed)
                {
                    touching = true;
                    TouchMode = true;
                    pointer = t.position.ReadValue();
                    pHeld = true;
                    pDown = t.press.wasPressedThisFrame;
                }
            }
            var mouse = Mouse.current;
            if (!touching && mouse != null)
            {
                pointer = mouse.position.ReadValue();
                pHeld = mouse.leftButton.isPressed;
                pDown = mouse.leftButton.wasPressedThisFrame;
            }
#else
            bool leftK = Input.GetKey(KeyCode.A) || Input.GetKey(KeyCode.LeftArrow);
            bool rightK = Input.GetKey(KeyCode.D) || Input.GetKey(KeyCode.RightArrow);
            move = (rightK ? 1f : 0f) - (leftK ? 1f : 0f);
            interact = Input.GetKeyDown(KeyCode.E) || Input.GetKeyDown(KeyCode.Return) || Input.GetKeyDown(KeyCode.KeypadEnter);
            action = Input.GetKeyDown(KeyCode.Space);
            pause = Input.GetKeyDown(KeyCode.Escape) || Input.GetKeyDown(KeyCode.P);
            up = Input.GetKeyDown(KeyCode.W) || Input.GetKeyDown(KeyCode.UpArrow);
            down = Input.GetKeyDown(KeyCode.S) || Input.GetKeyDown(KeyCode.DownArrow);
            throttle = rightK;
            brake = leftK;
            lens = new Vector2(move, (Input.GetKey(KeyCode.W) || Input.GetKey(KeyCode.UpArrow) ? 1f : 0f) - (Input.GetKey(KeyCode.S) || Input.GetKey(KeyCode.DownArrow) ? 1f : 0f));
            if (Input.touchCount > 0)
            {
                TouchMode = true;
                var t = Input.GetTouch(0);
                pointer = t.position;
                pHeld = t.phase != TouchPhase.Ended && t.phase != TouchPhase.Canceled;
                pDown = t.phase == TouchPhase.Began;
            }
            else
            {
                pointer = Input.mousePosition;
                pHeld = Input.GetMouseButton(0);
                pDown = Input.GetMouseButtonDown(0);
            }
#endif
            // on-screen buttons
            if (VHeld(VirtualButton.Left)) move -= 1f;
            if (VHeld(VirtualButton.Right)) move += 1f;
            interact |= VDown(VirtualButton.Interact);
            action |= VDown(VirtualButton.Action);
            pause |= VDown(VirtualButton.Pause);
            up |= VDown(VirtualButton.Up);
            down |= VDown(VirtualButton.Down);
            throttle |= VHeld(VirtualButton.Throttle);
            brake |= VHeld(VirtualButton.Brake);
            for (int i = 0; i < VirtualHeld.Length; i++) VirtualPrev[i] = VirtualHeld[i];

            bool overUI = EventSystem.current != null && (pHeld || pDown) && IsOverInteractiveUI(pointer);

            var sim = Simulation;
            if (sim != null)
            {
                move = sim.MoveX;
                interact = sim.ConsumeInteract();
                action = sim.ConsumeAction();
                up = sim.ConsumeUp();
                down = sim.ConsumeDown();
                throttle = sim.Throttle;
                brake = sim.Brake;
                pause = false;
                if (sim.PointerOverride)
                {
                    pointer = sim.Pointer;
                    pHeld = sim.PointerHeld;
                    pDown = sim.ConsumeClick();
                    overUI = false;
                }
            }

            MoveX = Mathf.Clamp(move, -1f, 1f);
            InteractDown = interact;
            ActionDown = action;
            PauseDown = pause;
            UpDown = up;
            DownDown = down;
            ThrottleHeld = throttle;
            BrakeHeld = brake;
            LensKeys = lens;
            LensKeysActive = lens.sqrMagnitude > 0.01f;
            PointerMoved = (pointer - _lastPointer).sqrMagnitude > 0.5f;
            _lastPointer = pointer;
            PointerScreen = pointer;
            PointerHeld = pHeld;
            PointerDown = pDown && !overUI;
            PointerOverUI = overUI;
        }

        private static readonly System.Collections.Generic.List<RaycastResult> Hits = new System.Collections.Generic.List<RaycastResult>();

        /// <summary>True when the pointer is over a button or other clickable UI (not over decorative overlays).</summary>
        private static bool IsOverInteractiveUI(Vector2 position)
        {
            var es = EventSystem.current;
            var data = new PointerEventData(es) { position = position };
            Hits.Clear();
            es.RaycastAll(data, Hits);
            foreach (var h in Hits)
                if (h.gameObject.GetComponentInParent<UnityEngine.UI.Selectable>() != null || h.gameObject.GetComponentInParent<TouchButton>() != null
                    || h.gameObject.GetComponentInParent<UIBlocker>() != null)
                    return true;
            return false;
        }
    }



    /// <summary>Scripted input for automated play-throughs (PlayMode tests / QA autoplay).</summary>
    public sealed class InputSimulation
    {
        public float MoveX;
        public bool Throttle, Brake;
        public bool PointerOverride;
        public Vector2 Pointer;
        public bool PointerHeld;
        private bool _interact, _action, _up, _down, _click;

        public void PressInteract() => _interact = true;
        public void PressAction() => _action = true;
        public void PressUp() => _up = true;
        public void PressDown() => _down = true;
        public void Click() => _click = true;

        internal bool ConsumeInteract() { bool v = _interact; _interact = false; return v; }
        internal bool ConsumeAction() { bool v = _action; _action = false; return v; }
        internal bool ConsumeUp() { bool v = _up; _up = false; return v; }
        internal bool ConsumeDown() { bool v = _down; _down = false; return v; }
        internal bool ConsumeClick() { bool v = _click; _click = false; return v; }
    }


}

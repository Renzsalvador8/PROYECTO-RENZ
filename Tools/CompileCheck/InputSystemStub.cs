// Compile-check stub of the Unity Input System API surface used by the game (signatures verified against
// com.unity.inputsystem 1.11.2 source). Only used by Tools/CompileCheck — never shipped in the Unity project.
using UnityEngine;

namespace UnityEngine.InputSystem.Controls
{
    public abstract class InputControl { }
    public abstract class InputControl<TValue> : InputControl where TValue : struct
    {
        public TValue ReadValue() => default;
    }
    public class AxisControl : InputControl<float> { }
    public class ButtonControl : AxisControl
    {
        public bool isPressed => false;
        public bool wasPressedThisFrame => false;
        public bool wasReleasedThisFrame => false;
    }
    public class KeyControl : ButtonControl { }
    public class TouchPressControl : ButtonControl { }
    public class Vector2Control : InputControl<Vector2> { }
    public class TouchControl : InputControl<int>
    {
        public TouchPressControl press { get; set; }
        public Vector2Control position { get; set; }
    }
}

namespace UnityEngine.InputSystem
{
    using UnityEngine.InputSystem.Controls;

    public class InputDevice { }

    public class Keyboard : InputDevice
    {
        public static Keyboard current { get; private set; }
        public KeyControl aKey => null; public KeyControl dKey => null; public KeyControl eKey => null;
        public KeyControl pKey => null; public KeyControl sKey => null; public KeyControl wKey => null;
        public KeyControl spaceKey => null; public KeyControl enterKey => null; public KeyControl numpadEnterKey => null;
        public KeyControl escapeKey => null; public KeyControl leftArrowKey => null; public KeyControl rightArrowKey => null;
        public KeyControl upArrowKey => null; public KeyControl downArrowKey => null;
    }

    public class Pointer : InputDevice
    {
        public Vector2Control position { get; protected set; }
        public ButtonControl press { get; protected set; }
        public static Pointer current { get; internal set; }
    }

    public class Mouse : Pointer
    {
        public ButtonControl leftButton { get; protected set; }
        public new static Mouse current { get; private set; }
    }

    public class Touchscreen : Pointer
    {
        public TouchControl primaryTouch { get; protected set; }
        public new static Touchscreen current { get; internal set; }
    }
}

namespace UnityEngine.InputSystem.UI
{
    public class InputSystemUIInputModule : UnityEngine.EventSystems.BaseInputModule
    {
        public override void Process() { }
    }
}

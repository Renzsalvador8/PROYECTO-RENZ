using UnityEngine;

namespace TheTester
{
    /// <summary>Refreshes GameInput before any gameplay script runs.</summary>
    [DefaultExecutionOrder(-1000)]
    public sealed class GameInputUpdater : MonoBehaviour
    {
        private void Update() => GameInput.Refresh();
    }
}

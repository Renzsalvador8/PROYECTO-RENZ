using UnityEngine;

namespace TheTester
{
    /// <summary>Places a layer root at camera * (1 - factor): 1 = gameplay plane, &lt;1 = farther, &gt;1 = foreground.</summary>
    [DefaultExecutionOrder(100)]
    public sealed class ParallaxLayer : MonoBehaviour
    {
        public float FactorX = 1f;
        public float FactorY = 1f;
        public Transform CameraTransform;

        private void LateUpdate() => Apply();

        public void Apply()
        {
            if (CameraTransform == null) return;
            var c = CameraTransform.position;
            transform.position = new Vector3(c.x * (1f - FactorX), c.y * (1f - FactorY), 0f);
        }
    }
}

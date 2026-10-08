using TheTester.Core;
using UnityEngine;

namespace TheTester
{
    /// <summary>Shared plumbing for the close-up inspection views (a 1920×1080 painting at 100 px/unit).</summary>
    public abstract class InspectionStage : MonoBehaviour
    {
        protected DirectorBase D;
        protected Vector2 Center;
        protected Magnifier Lens;
        protected Vector2 LensTarget;
        protected bool LensLocked;
        public bool Completed { get; protected set; }
        public float LensSpeedKeys = 7f;

        protected static Vector2 PxToLocal(float px, float py) => new Vector2((px - 960f) / 100f, (540f - py) / 100f);

        protected SpriteRenderer Painting(string sprite, int order)
        {
            var go = new GameObject(sprite);
            go.transform.SetParent(transform, false);
            go.transform.localPosition = Vector3.zero;
            var sr = go.AddComponent<SpriteRenderer>();
            sr.sprite = GameAssets.Sprite(sprite, 100f, new Vector2(0.5f, 0.5f));
            sr.sortingOrder = order;
            return sr;
        }

        protected Vector2 LensLocal => Lens.Position - Center;

        /// <summary>Moves the lens with the pointer (mouse/touch) or the keyboard, smoothly and clamped to the painting.</summary>
        protected void UpdateLens(float dt)
        {
            Cursor.visible = GameInput.TouchMode || (GameManager.I != null && GameManager.I.Paused);
            if (!LensLocked)
            {
                bool pointerDriven = GameInput.Simulation != null ? GameInput.Simulation.PointerOverride
                    : GameInput.TouchMode ? GameInput.PointerHeld : true;
                if (GameInput.LensKeysActive && !GameInput.PointerMoved && !GameInput.PointerHeld)
                {
                    LensTarget += GameInput.LensKeys.normalized * LensSpeedKeys * dt;
                    pointerDriven = false;
                }
                if (pointerDriven && !GameInput.PointerOverUI && (GameInput.PointerMoved || GameInput.PointerHeld || GameInput.Simulation != null))
                    LensTarget = D.Cam.ScreenToWorld(GameInput.PointerScreen);
            }
            var local = LensTarget - Center;
            local.x = Mathf.Clamp(local.x, -9.3f, 9.3f);
            local.y = Mathf.Clamp(local.y, -5.1f, 5.1f);
            LensTarget = Center + local;
            Lens.Position = Vector2.Lerp(Lens.Position, LensTarget, 1f - Mathf.Exp(-16f * dt));
        }

        protected static Vec2 V(Vector2 v) => new Vec2(v.x, v.y);
    }
}

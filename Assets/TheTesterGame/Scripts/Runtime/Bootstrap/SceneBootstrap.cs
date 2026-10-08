using UnityEngine;

namespace TheTester
{
    /// <summary>
    /// The only component saved in each scene file. It makes sure the persistent GameManager exists and
    /// starts the scene's director, which builds the level from data (art, layout, gameplay) at runtime.
    /// Pressing Play in any of the four scenes works on its own.
    /// </summary>
    public sealed class SceneBootstrap : MonoBehaviour
    {
        public GameScene scene = GameScene.MainMenu;

        private void Start()
        {
            var gm = GameManager.Ensure();
            gm.OnSceneStarted(scene, gameObject);
        }
    }
}

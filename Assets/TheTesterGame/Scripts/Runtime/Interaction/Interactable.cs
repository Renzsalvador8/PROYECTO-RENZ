using System;
using System.Collections;
using UnityEngine;

namespace TheTester
{
    /// <summary>Something Jean Paul can inspect/use. The director supplies the behaviour as a coroutine.</summary>
    public sealed class Interactable : MonoBehaviour
    {
        public string Id;
        public string Prompt;
        public float Radius = 1.5f;
        public float PromptHeight = 2.9f;
        public bool Available = true;
        public bool Highlight;
        public Func<IEnumerator> OnInteract;

        public static Interactable Create(string id, float x, float y, string prompt, float radius, Func<IEnumerator> onInteract, Transform parent = null)
        {
            var go = new GameObject("Interactable · " + id);
            if (parent != null) go.transform.SetParent(parent, false);
            go.transform.position = new Vector3(x, y, 0f);
            var it = go.AddComponent<Interactable>();
            it.Id = id;
            it.Prompt = prompt;
            it.Radius = radius;
            it.OnInteract = onInteract;
            InteractionSystem.Register(it);
            return it;
        }

        public Vector3 PromptAnchor => transform.position + new Vector3(0f, PromptHeight, 0f);

        private void OnDestroy() => InteractionSystem.Unregister(this);
    }
}

using System.Collections;
using System.Collections.Generic;
using UnityEngine;

namespace TheTester
{
    /// <summary>Finds the nearest available interactable, shows its contextual prompt and runs it on E / tap.</summary>
    public sealed class InteractionSystem : MonoBehaviour
    {
        private static readonly List<Interactable> All = new List<Interactable>();
        public static void Register(Interactable i) { if (!All.Contains(i)) All.Add(i); }
        public static void Unregister(Interactable i) => All.Remove(i);

        public bool Enabled = true;
        public Interactable Current { get; private set; }
        public bool Running { get; private set; }
        private PlayerController2D _player;

        public void Init(PlayerController2D player) => _player = player;

        private void Update()
        {
            if (_player == null) return;
            Interactable best = null;
            if (Enabled && !Running && _player.InputEnabled && !_player.Busy)
            {
                float bestD = float.MaxValue;
                float px = _player.transform.position.x;
                foreach (var it in All)
                {
                    if (it == null || !it.Available || !it.isActiveAndEnabled) continue;
                    float d = Mathf.Abs(it.transform.position.x - px);
                    if (d <= it.Radius && d < bestD) { best = it; bestD = d; }
                }
            }
            if (best != Current)
            {
                Current = best;
                if (UIManager.I != null)
                {
                    if (best != null) UIManager.I.ShowPrompt(best.Prompt, best.PromptAnchor);
                    else UIManager.I.HidePrompt();
                }
            }
            else if (best != null && UIManager.I != null)
            {
                UIManager.I.MovePrompt(best.PromptAnchor);
            }
            if (Current != null && GameInput.InteractDown && !GameManager.I.Paused)
                StartCoroutine(RunInteraction(Current));
        }

        private IEnumerator RunInteraction(Interactable it)
        {
            Running = true;
            UIManager.I.HidePrompt();
            Current = null;
            bool prev = _player.InputEnabled;
            _player.InputEnabled = false;
            _player.Stop();
            if (it.OnInteract != null) yield return it.OnInteract();
            _player.InputEnabled = prev || _player.InputEnabled;
            Running = false;
        }

        /// <summary>Used by automated tests: trigger the interactable with this id if in range.</summary>
        public Interactable Find(string id)
        {
            foreach (var it in All) if (it != null && it.Id == id) return it;
            return null;
        }

        private void OnDestroy()
        {
            All.RemoveAll(i => i == null);
        }
    }
}

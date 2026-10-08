using System.Collections;
using System.Collections.Generic;
using TheTester.Core;
using UnityEngine;

namespace TheTester
{
    /// <summary>
    /// TEST 02 — the detail test inside the cabin. The notebook shows magnified crops of four details;
    /// the player must find each one and click it with the lens over it. Wrong clicks earn dry remarks.
    /// Finishes with the critic re-checking, then producing a much larger magnifier: "Esto es sospechoso."
    /// </summary>
    public sealed class DetailTest : InspectionStage
    {
        private DetailPuzzle _puzzle;
        private float _sinceFind;
        private int _nothingCount;
        private int _hintIndex;

        public static IEnumerator Run(DirectorBase director, Vector2 center)
        {
            var go = new GameObject("Inspection · Interior");
            go.transform.position = center;
            var dt = go.AddComponent<DetailTest>();
            dt.D = director;
            dt.Center = center;
            yield return dt.Play();
            Object.Destroy(go);
        }

        public DetailPuzzle Puzzle => _puzzle;

        public Vector2 WorldOf(string id)
        {
            var s = _puzzle?.Find(id);
            return s == null ? Center : Center + new Vector2(s.Center.X, s.Center.Y);
        }

        private IEnumerator Play()
        {
            var ui = UIManager.I;
            var cabin = Painting("Art/Inspection/ioniq5_interior", 2000);
            var data = GameAssets.Json("Data/Inspection/interior");
            _puzzle = new DetailPuzzle { ClickCooldown = 0.3f };
            foreach (var id in Lines.InteriorOrder)
            {
                var t = data["targets"][id];
                var c = t["center"].AsFloats(960, 540);
                _puzzle.AddTarget(id, V(PxToLocal(c[0], c[1])), t.GetFloat("radius", 60f) / 100f);
            }
            foreach (var id in data["decoys"].Keys)
            {
                var t = data["decoys"][id];
                var c = t["center"].AsFloats(960, 540);
                _puzzle.AddDecoy(id, V(PxToLocal(c[0], c[1])), t.GetFloat("radius", 60f) / 100f);
            }
            Lens = Magnifier.Create(transform, 1.05f, 2.2f, 2010, cabin);
            Lens.Position = LensTarget = Center;

            D.Cam.Cut(Center, 5.4f);
            ui.SetHudVisible(false);
            ui.SetTouchMode(TouchLayout.Inspect);
            var entries = new List<UIManager.NotebookEntry>();
            foreach (var id in Lines.InteriorOrder)
                entries.Add(new UIManager.NotebookEntry
                {
                    Id = id, Label = Lines.InteriorClues[id],
                    Image = GameAssets.Sprite("Art/Inspection/clue_" + id, 100f),
                });
            ui.OpenNotebook(Lines.InteriorTitle, GameInput.TouchMode ? Lines.InteriorHintTouch : Lines.InteriorHint, entries);
            AudioManager.I.Sfx("door_close", 0.6f);
            yield return ui.FadeIn(0.9f);
            Cursor.visible = false;

            while (!_puzzle.IsComplete)
            {
                float dt = Time.deltaTime;
                _puzzle.Tick(dt);
                _sinceFind += dt;
                UpdateLens(dt);
                bool click = GameInput.PointerDown || GameInput.InteractDown || GameInput.ActionDown;
                if (click)
                {
                    Vector2 probe = LensLocal;
                    if (GameInput.PointerDown)
                    {
                        // the lens sits under the pointer: inspect exactly where the player clicked/tapped
                        LensTarget = D.Cam.ScreenToWorld(GameInput.PointerScreen);
                        probe = LensTarget - Center;
                    }
                    Handle(_puzzle.Click(V(probe)));
                }
                if (_sinceFind > 40f) GiveHint();
                yield return null;
            }

            // ---- the critic is unsatisfied: re-checks, then a bigger magnifier
            yield return Tween.Wait(UIManager.ReadingTime(Lines.InteriorFound["reloj"]) * 0.5f);
            LensLocked = true;
            ui.CloseNotebook();
            yield return MoveLens(WorldOf("reloj"), 1.3f);
            ui.Caption(Lines.InteriorRecheck1, 1.8f);
            yield return Tween.Wait(1.4f);
            yield return MoveLens(WorldOf("volante"), 1.1f);
            ui.Caption(Lines.InteriorRecheck2, 2.2f);
            yield return Tween.Wait(2.2f);
            AudioManager.I.Sfx("big_magnifier", 0.8f);
            AudioManager.I.DuckMusic(0.2f, 0.4f);
            float r0 = Lens.Radius;
            yield return Tween.Run(0.75f, k => Lens.Radius = Mathf.LerpUnclamped(r0, 2.6f, k), k => Ease.OutBack(k, 1.2f));
            D.Cam.Shake(0.05f);
            yield return Tween.Wait(0.5f);
            ui.Caption(Lines.InteriorSuspicious, 3.0f);
            yield return Tween.Wait(3.2f);
            Completed = true;
            Cursor.visible = true;
            AudioManager.I.DuckMusic(1f, 1.5f);
            yield return ui.FadeOut(0.9f);
        }

        private IEnumerator MoveLens(Vector2 target, float time)
        {
            var from = Lens.Position;
            yield return Tween.Run(time, k => { Lens.Position = Vector2.Lerp(from, target, k); LensTarget = Lens.Position; }, Ease.InOutCubic);
        }

        private void Handle(DetailPuzzle.Result r)
        {
            var ui = UIManager.I;
            switch (r.Kind)
            {
                case DetailPuzzle.ResultKind.Found:
                    _sinceFind = 0f;
                    AudioManager.I.Sfx("inspect_found", 0.65f);
                    ui.CheckNotebook(r.Id);
                    ui.Caption(Lines.InteriorFound[r.Id]);
                    D.Cam.Shake(0.015f);
                    break;
                case DetailPuzzle.ResultKind.Decoy:
                    AudioManager.I.Sfx("wrong", 0.4f);
                    if (Lines.InteriorDecoys.TryGetValue(r.Id, out var line)) ui.Caption(line);
                    break;
                case DetailPuzzle.ResultKind.AlreadyFound:
                    ui.Caption(Lines.InteriorAlready, 2f);
                    break;
                case DetailPuzzle.ResultKind.Nothing:
                    AudioManager.I.Sfx("wrong", 0.25f, 1.15f);
                    if (_nothingCount++ % 2 == 0)
                        ui.Caption(Lines.InteriorNothing[(_nothingCount / 2) % Lines.InteriorNothing.Length], 1.6f);
                    break;
            }
        }

        private void GiveHint()
        {
            _sinceFind = 0f;
            for (int i = 0; i < Lines.InteriorOrder.Length; i++)
            {
                var id = Lines.InteriorOrder[(_hintIndex + i) % Lines.InteriorOrder.Length];
                var s = _puzzle.Find(id);
                if (s != null && !s.Found)
                {
                    _hintIndex = (_hintIndex + i + 1) % Lines.InteriorOrder.Length;
                    UIManager.I.Caption("«" + Lines.InteriorClues[id] + "»", 3.5f);
                    return;
                }
            }
        }
    }
}

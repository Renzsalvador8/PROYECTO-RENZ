using System.Collections;
using System.Collections.Generic;
using TheTester.Core;
using UnityEngine;

namespace TheTester
{
    /// <summary>
    /// TEST 01 — exterior close-up. Five areas (headlights, wheels, bodywork, door alignment, grille) must each be
    /// examined by resting the magnifier over them. Each completion writes a deadpan note in the notebook.
    /// </summary>
    public sealed class ExteriorInspection : InspectionStage
    {
        private InspectionSession _session;
        private readonly Dictionary<string, SpriteRenderer> _markers = new Dictionary<string, SpriteRenderer>();
        private readonly Dictionary<string, SpriteRenderer> _checks = new Dictionary<string, SpriteRenderer>();
        private float _time;

        public static IEnumerator Run(DirectorBase director, Vector2 center)
        {
            var go = new GameObject("Inspection · Exterior");
            go.transform.position = center;
            var ins = go.AddComponent<ExteriorInspection>();
            ins.D = director;
            ins.Center = center;
            yield return ins.Play();
            Object.Destroy(go);
        }

        private IEnumerator Play()
        {
            var ui = UIManager.I;
            var bg = Painting("Art/Inspection/bg_exterior", 2000);
            var car = Painting("Art/Inspection/ioniq5_34_teal", 2001);
            _session = new InspectionSession { DwellTime = 1.35f, LensRadius = 1.1f };
            var hs = GameAssets.Json("Data/Vehicles/ioniq5")["inspectionHotspots"];
            foreach (var id in Lines.ExteriorOrder)
            {
                var h = hs[id];
                var c = h["center"].AsFloats(960, 540);
                var local = PxToLocal(c[0], c[1]);
                float r = h.GetFloat("radius", 80f) / 100f;
                _session.Add(id, V(local), r);
                var mk = Marker(local, r, 2005);
                _markers[id] = mk;
                var chk = new GameObject("Check · " + id).AddComponent<SpriteRenderer>();
                chk.transform.SetParent(transform, false);
                chk.transform.localPosition = new Vector3(local.x + r * 0.7f, local.y + r * 0.7f, 0f);
                chk.sprite = GameAssets.Sprite("UI/check", 100f);
                chk.color = new Color(0.71f, 0.47f, 0.33f, 0f);
                chk.sortingOrder = 2006;
                chk.transform.localScale = Vector3.one * 0.55f;
                _checks[id] = chk;
            }
            _session.TargetCompleted += OnTargetDone;
            Lens = Magnifier.Create(transform, 1.25f, 2.1f, 2010, bg, car);
            Lens.Position = LensTarget = Center + new Vector2(-2.5f, 0.5f);

            D.Cam.Cut(Center, 5.4f);
            ui.SetHudVisible(false);
            ui.SetLetterbox(0f, 0f);
            ui.SetTouchMode(TouchLayout.Inspect);
            var entries = new List<UIManager.NotebookEntry>();
            foreach (var id in Lines.ExteriorOrder) entries.Add(new UIManager.NotebookEntry { Id = id, Label = Lines.ExteriorLabels[id] });
            ui.OpenNotebook(Lines.ExteriorTitle, GameInput.TouchMode ? Lines.ExteriorHintTouch : Lines.ExteriorHint, entries);
            yield return ui.FadeIn(0.9f);
            Cursor.visible = false;
            AudioManager.I.Sfx("magnifier_up", 0.5f);

            while (!_session.IsComplete)
            {
                float dt = Time.deltaTime;
                _time += dt;
                UpdateLens(dt);
                _session.Update(dt, V(LensLocal), true);
                UpdateMarkers();
                var hov = _session.Hovered;
                if (hov != null && !hov.Done)
                    ui.SetDwell(true, ui.WorldToSafe(Lens.Position), ui.WorldUnitsToSafePixels(Lens.Radius), hov.Progress);
                else
                    ui.SetDwell(false, Vector2.zero, 0f, 0f);
                yield return null;
            }
            ui.SetDwell(false, Vector2.zero, 0f, 0f);
            Completed = true;
            UpdateMarkers();
            yield return Tween.Wait(UIManager.ReadingTime(Lines.ExteriorNotes[Lines.ExteriorOrder[0]]) * 0.6f);
            // the lens drifts back to centre, the critic finds nothing more
            LensLocked = true;
            LensTarget = Center + new Vector2(0.4f, 0.4f);
            float t = 0f;
            while (t < 1.4f) { UpdateLens(Time.deltaTime); t += Time.deltaTime; yield return null; }
            ui.Caption(Lines.ExteriorAllDone, 1.6f);
            yield return Tween.Wait(1.8f);
            Cursor.visible = true;
            ui.CloseNotebook();
            yield return ui.FadeOut(0.9f);
        }

        private SpriteRenderer Marker(Vector2 local, float r, int order)
        {
            var sr = new GameObject("Marker").AddComponent<SpriteRenderer>();
            sr.transform.SetParent(transform, false);
            sr.transform.localPosition = new Vector3(local.x, local.y, 0f);
            sr.sprite = GameAssets.Sprite("UI/ring", 100f);
            float s = (r * 2f) / 2.56f;
            sr.transform.localScale = new Vector3(s, s, 1f);
            sr.sortingOrder = order;
            sr.color = new Color(0.93f, 0.89f, 0.84f, 0.15f);
            return sr;
        }

        private void UpdateMarkers()
        {
            foreach (var t in _session.Targets)
            {
                var mk = _markers[t.Id];
                float pulse = 0.5f + 0.5f * Mathf.Sin(_time * 2.2f + t.Center.X);
                float a = t.Done ? 0f : (t == _session.Hovered ? 0.55f : 0.10f + 0.10f * pulse);
                var c = mk.color;
                c.a = Mathf.Lerp(c.a, a, 1f - Mathf.Exp(-8f * Time.deltaTime));
                mk.color = c;
                var chk = _checks[t.Id];
                var cc = chk.color;
                cc.a = Mathf.Lerp(cc.a, t.Done ? 0.9f : 0f, 1f - Mathf.Exp(-6f * Time.deltaTime));
                chk.color = cc;
            }
        }

        private void OnTargetDone(InspectionSession.Target t)
        {
            AudioManager.I.Sfx("inspect_found", 0.6f);
            UIManager.I.CheckNotebook(t.Id);
            UIManager.I.Caption(Lines.ExteriorNotes[t.Id]);
            D.Cam.Shake(0.015f);
        }

        /// <summary>For automated tests: the lens position (world) that inspects a given area.</summary>
        public Vector2 WorldOf(string id)
        {
            var t = _session?.Find(id);
            return t == null ? Center : Center + new Vector2(t.Center.X, t.Center.Y);
        }

        public InspectionSession Session => _session;
    }
}

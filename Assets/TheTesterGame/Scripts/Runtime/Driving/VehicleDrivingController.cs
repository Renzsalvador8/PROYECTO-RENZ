using System;
using System.Collections.Generic;
using TheTester.Core;
using UnityEngine;
using UnityEngine.Rendering;

namespace TheTester
{
    /// <summary>
    /// The IONIQ 5 in the test drive: wraps the engine-independent VehicleModel/DriveCourse and presents them —
    /// rolling wheels, suspension pitch, lane changes with depth, the driver visible through the glass and EV audio.
    /// </summary>
    public sealed class VehicleDrivingController : MonoBehaviour
    {
        public VehicleModel Model { get; } = new VehicleModel();
        public DriveCourse Course { get; private set; }
        public TesterRig Driver { get; private set; }
        public RigAnimator DriverAnim { get; private set; }
        public bool InputEnabled;
        public DriveAutopilot Autopilot;              // used only by automated tests / QA autoplay
        public float NearY = -3.58f, FarY = -2.72f;
        public int NearOrder = -850, FarOrder = -895;
        public event Action<DriveEvent> CourseEvent;
        public event Action LaneRefused;

        private Transform _body;
        private readonly List<Transform> _wheels = new List<Transform>();
        private SortingGroup _group;
        private float _pitch, _pitchVel, _bobT;
        private float _laneRefuseCooldown;

        public static VehicleDrivingController Create(Transform parent, DriveCourse course, float x)
        {
            var meta = GameAssets.Json("Data/Vehicles/ioniq5");
            var go = new GameObject("IONIQ 5");
            go.transform.SetParent(parent, false);
            var vc = go.AddComponent<VehicleDrivingController>();
            vc.Course = course;
            vc._group = go.AddComponent<SortingGroup>();
            vc._group.sortingOrder = vc.NearOrder;

            var body = new GameObject("Body").transform;
            body.SetParent(go.transform, false);
            vc._body = body;
            var carMeta = meta["sprites"]["ioniq5_side_teal_cabin"];
            var piv = carMeta["pivot"].AsFloats(0.5f, 0f);
            float ppu = carMeta.GetFloat("ppu", 200f);
            AddSprite(body, "Cabin", "Art/Drive/cabin_interior", ppu, new Vector2(piv[0], piv[1]), 0);
            vc.Driver = TesterRig.Create("tester_side", body, 10, "Driver");
            vc.Driver.transform.localPosition = new Vector3(0.30f + 0.016f, 0.68f - 1.036f, 0f);
            vc.Driver.SetHidden(true, "thigh_f", "thigh_b", "shin_f", "shin_b", "shoe_f", "shoe_b");
            vc.DriverAnim = go.AddComponent<RigAnimator>();
            vc.DriverAnim.Init(vc.Driver);
            vc.DriverAnim.Play("sit_drive", 0f);
            AddSprite(body, "Body Paint", carMeta.GetString("sprite"), ppu, new Vector2(piv[0], piv[1]), 20);

            var wMeta = meta["sprites"]["ioniq5_wheel"];
            float wr = meta.GetFloat("wheelRadiusUnits", 0.474f);
            foreach (var ax in new[] { meta.GetFloat("rearAxleUnits", -1.97f), meta.GetFloat("frontAxleUnits", 1.925f) })
            {
                var w = AddSprite(go.transform, "Wheel", wMeta.GetString("sprite"), wMeta.GetFloat("ppu", 200f), new Vector2(0.5f, 0.5f), 30);
                w.transform.localPosition = new Vector3(ax, wr, 0f);
                vc._wheels.Add(w.transform);
            }
            vc.Model.WheelRadius = wr;
            vc.Model.HalfLength = meta.GetFloat("lengthUnits", 6.02f) * 0.5f;
            vc.Model.Teleport(x, 0);
            vc.Present(0f);
            return vc;
        }

        private static SpriteRenderer AddSprite(Transform parent, string name, string sprite, float ppu, Vector2 pivot, int order)
        {
            var go = new GameObject(name);
            go.transform.SetParent(parent, false);
            var sr = go.AddComponent<SpriteRenderer>();
            sr.sprite = GameAssets.Sprite(sprite, ppu, pivot);
            sr.sortingOrder = order;
            return sr;
        }

        private void Update()
        {
            float dt = Time.deltaTime;
            if (dt <= 0f) return;
            bool throttle = false, brake = false;
            int laneReq = -1;
            if (Autopilot != null)
            {
                var c = Autopilot.Decide(Model, Course);
                throttle = c.Throttle;
                brake = c.Brake;
                laneReq = c.RequestLane;
            }
            else if (InputEnabled)
            {
                throttle = GameInput.ThrottleHeld;
                brake = GameInput.BrakeHeld;
                if (GameInput.UpDown) laneReq = 1;
                if (GameInput.DownDown) laneReq = 0;
                if (GameInput.ActionDown) Horn();
            }
            _laneRefuseCooldown -= dt;
            if (laneReq >= 0 && laneReq != Model.Lane)
            {
                if (Model.RequestLane(laneReq)) AudioManager.I.Sfx("indicator", 0.5f);
                else if (Autopilot == null && _laneRefuseCooldown <= 0f)
                {
                    _laneRefuseCooldown = 4f;
                    LaneRefused?.Invoke();
                }
            }
            Model.Step(dt, throttle, brake, Course.StopLimit(Model));
            var events = Course.Update(dt, Model);
            for (int i = 0; i < events.Count; i++) CourseEvent?.Invoke(events[i]);
            Present(dt);
        }

        public void Horn()
        {
            AudioManager.I.Sfx("horn", 0.55f);
        }

        /// <summary>Puts the visuals where the model says, with springy pitch and a little road texture.</summary>
        private void Present(float dt)
        {
            float laneT = Model.LaneT;
            float y = Mathf.Lerp(NearY, FarY, laneT);
            transform.position = new Vector3(Model.X, y, 0f);
            float s = Mathf.Lerp(1f, 0.93f, laneT);
            transform.localScale = new Vector3(s, s, 1f);
            _group.sortingOrder = laneT > 0.5f ? FarOrder : NearOrder;
            float deg = Model.WheelAngle * Mathf.Rad2Deg;
            foreach (var w in _wheels) w.localRotation = Quaternion.Euler(0f, 0f, deg);
            if (dt > 0f)
            {
                float target = Model.Accelerating * 1.3f + (Model.ChangingLane ? Mathf.Sign(Model.Lane - laneT) * 0.4f : 0f);
                float k = 60f, c = 9f;
                float acc = k * (target - _pitch) - c * _pitchVel;
                _pitchVel += acc * dt;
                _pitch += _pitchVel * dt;
                _bobT += dt * Mathf.Abs(Model.Speed) * 0.9f;
            }
            float bob = Mathf.Sin(_bobT * 6.1f) * 0.006f * Mathf.Clamp01(Mathf.Abs(Model.Speed) / 6f);
            _body.localPosition = new Vector3(0f, bob, 0f);
            _body.localRotation = Quaternion.Euler(0f, 0f, _pitch);
            float spd = Mathf.Abs(Model.Speed) / Model.MaxSpeed;
            AudioManager.I.SetLoop("motor", 0.12f + 0.32f * spd + (Model.Accelerating > 0.05f ? 0.08f : 0f), 0.62f + 1.05f * spd);
            AudioManager.I.SetLoop("road", 0.05f + 0.45f * spd, 0.8f + 0.4f * spd);
        }

        public void StartAudio()
        {
            AudioManager.I.Loop("motor", "ev_motor", 0.12f);
            AudioManager.I.Loop("road", "road_noise", 0.05f);
        }

        public void StopAudio()
        {
            AudioManager.I.StopLoop("motor");
            AudioManager.I.StopLoop("road");
        }

        /// <summary>World position of the driver's head (for the closing close-up).</summary>
        public Vector3 DriverHead
        {
            get
            {
                var b = Driver.Bone("head");
                return b != null ? b.position + new Vector3(0.05f, 0.25f, 0f) : transform.position;
            }
        }
    }
}

using System;

namespace TheTester.Core
{
    /// <summary>
    /// Approachable side-on driving model: throttle, brake (and slow reverse when held at a standstill),
    /// smooth two-lane positioning and a "never collide" stop limit supplied by the course.
    /// Units: world units (1 u = 0.77 m) and seconds.
    /// </summary>
    public sealed class VehicleModel
    {
        public const float MetresPerUnit = 0.77f;
        public const float KmhPerUnitPerSecond = MetresPerUnit * 3.6f;

        public float MaxSpeed = 20f;          // ~55 km/h
        public float Accel = 5.2f;
        public float BrakeDecel = 10f;
        public float CoastDecel = 0.9f;
        public float AeroDrag = 0.006f;
        public float ReverseMax = 2.6f;
        public float ReverseAccel = 2.2f;
        public float ReverseDelay = 0.35f;
        public float LaneChangeTime = 1.1f;
        public float HalfLength = 3.0f;
        public float MinLaneChangeSpeed = 1.0f;

        public float X;
        public float Speed;
        public int Lane;                       // 0 = near lane, 1 = far lane
        public float LaneT;                    // 0..1 eased lateral position
        public bool Reversing { get; private set; }
        public float Accelerating { get; private set; }   // -1..1, used for body pitch
        public bool AutoBraking { get; private set; }
        public float WheelAngle;               // radians, for wheel sprites
        public float WheelRadius = 0.474f;

        private float _laneProgress;           // linear 0..1 toward the target lane
        private float _brakeHeld;
        private bool _prevBrake;
        private bool _reverseArmed;            // brake pressed again from a standstill

        public float Kmh => Math.Abs(Speed) * KmhPerUnitPerSecond;
        public float Front => X + HalfLength;
        public bool ChangingLane => Math.Abs(_laneProgress - Lane) > 1e-3f;
        public bool InFarLane => LaneT > 0.5f;

        public bool RequestLane(int lane)
        {
            lane = lane <= 0 ? 0 : 1;
            if (lane == Lane) return false;
            if (Math.Abs(Speed) < MinLaneChangeSpeed) return false;
            Lane = lane;
            return true;
        }

        /// <param name="stopLimit">x the front bumper must not pass (float.MaxValue = none)</param>
        public void Step(float dt, bool throttle, bool brake, float stopLimit = float.MaxValue)
        {
            if (dt <= 0) return;
            float prevSpeed = Speed;
            AutoBraking = false;

            // Reverse needs a fresh brake press while stopped, so holding the brake at a red light never rolls back.
            if (brake && !_prevBrake && Math.Abs(Speed) <= 0.05f) _reverseArmed = true;
            if (!brake) { _reverseArmed = false; _brakeHeld = 0f; }
            else if (_reverseArmed) _brakeHeld += dt;
            _prevBrake = brake;
            Reversing = _reverseArmed && !throttle && _brakeHeld >= ReverseDelay;

            if (Reversing)
            {
                Speed = MathUtil.MoveTowards(Speed, -ReverseMax, ReverseAccel * dt);
            }
            else if (Speed < 0f)
            {
                // leaving reverse: always roll back to a stop first
                Speed = MathUtil.MoveTowards(Speed, 0f, (throttle ? BrakeDecel : CoastDecel * 3f) * dt);
            }
            else
            {
                if (brake)
                {
                    Speed = Math.Max(0f, Speed - BrakeDecel * dt);
                }
                else if (throttle)
                {
                    float k = 1f - (Speed / MaxSpeed) * 0.75f;      // torque falls off gently
                    Speed = Math.Min(MaxSpeed, Speed + Accel * k * dt);
                }
                else
                {
                    Speed = Math.Max(0f, Speed - (CoastDecel + AeroDrag * Speed * Speed) * dt);
                }
            }

            // comfortable automatic braking so the car never touches an obstacle
            if (Speed > 0f && stopLimit < float.MaxValue)
            {
                float gap = stopLimit - Front;
                float comfortable = 7.5f;
                float stopping = Speed * Speed / (2f * comfortable);
                if (gap <= stopping + 0.4f)
                {
                    AutoBraking = true;
                    float need = gap > 0.05f ? Speed * Speed / (2f * gap) : BrakeDecel * 2f;
                    Speed = Math.Max(0f, Speed - Math.Min(need, BrakeDecel * 2f) * dt);
                }
            }

            X += Speed * dt;
            if (stopLimit < float.MaxValue && Front > stopLimit)
            {
                X = stopLimit - HalfLength;
                if (Speed > 0f) Speed = 0f;
            }

            Accelerating = MathUtil.Clamp((Speed - prevSpeed) / dt / 8f, -1f, 1f);
            WheelAngle -= Speed * dt / WheelRadius;

            float step = dt / LaneChangeTime;
            _laneProgress = MathUtil.MoveTowards(_laneProgress, Lane, step);
            LaneT = MathUtil.SmoothStep(_laneProgress);
        }

        public void Teleport(float x, int lane)
        {
            X = x; Speed = 0f; Lane = lane; _laneProgress = lane; LaneT = lane; _brakeHeld = 0f; Reversing = false; _reverseArmed = false; _prevBrake = false;
        }
    }
}

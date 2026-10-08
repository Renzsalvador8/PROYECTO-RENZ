using System;

namespace TheTester.Core
{
    /// <summary>
    /// A careful reference driver used by automated tests (and the optional demo/QA autoplay).
    /// It obeys the light, changes lanes around the van, respects the school zone and parks.
    /// </summary>
    public sealed class DriveAutopilot
    {
        public struct Controls
        {
            public bool Throttle;
            public bool Brake;
            public int RequestLane;   // -1 = no request
        }

        public float CruiseKmh = 46f;
        public float SchoolKmh = 27f;
        private bool _reverseTap;

        public Controls Decide(VehicleModel car, DriveCourse course)
        {
            var c = new Controls { RequestLane = -1 };
            float target = CruiseKmh;
            float front = car.Front;

            // traffic light: stop a little before the line while it is not green
            if (course.Light != LightState.Green && front < course.StopLineX)
            {
                float stopAt = course.StopLineX - 1.2f;
                target = SpeedForStop(stopAt - front);
            }
            // lane change around the obstacle, then back
            if (front > course.ObstacleStart - 45f && car.X - car.HalfLength < course.ObstacleEnd + 2f)
                c.RequestLane = 1;
            else if (car.X - car.HalfLength > course.ObstacleEnd + 4f)
                c.RequestLane = 0;
            // school zone (start braking a bit before entering)
            if (car.X > course.SchoolStart - 25f && car.X < course.SchoolEnd)
                target = Math.Min(target, SchoolKmh);
            // parking: aim the centre of the car at the box
            if (course.Stage == DriveStage.Parking || car.X > course.SchoolEnd)
            {
                float dist = course.ParkingX - car.X;
                target = Math.Min(target, SpeedForStop(dist));
                if (dist < -0.3f && car.Speed <= 0.05f)
                {
                    // overshot: tap then hold the brake to reverse slowly
                    _reverseTap = !_reverseTap || car.Reversing;
                    c.Brake = _reverseTap;
                    return c;
                }
            }
            float kmh = car.Speed * VehicleModel.KmhPerUnitPerSecond;
            if (target <= 0.5f)
            {
                c.Brake = car.Speed > 0.02f;
                return c;
            }
            if (kmh < target - 1.5f) c.Throttle = true;
            else if (kmh > target + 3f) c.Brake = true;
            return c;
        }

        /// <summary>Speed (km/h) that lets the car stop within 'distance' using a gentle 4 u/s² deceleration.</summary>
        private static float SpeedForStop(float distance)
        {
            if (distance <= 0.15f) return 0f;
            float v = (float)Math.Sqrt(2f * 4.0f * distance);
            return Math.Max(3f, v * VehicleModel.KmhPerUnitPerSecond);
        }
    }
}

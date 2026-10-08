using System;
using System.Collections.Generic;

namespace TheTester.Core
{
    public enum DriveEvent
    {
        LightAmber, LightRed, LightGreen, StoppedAtLight, RanRedLight, TooFarFromLine,
        ObstacleAhead, AutoBrake, PassedObstacle, BackInLane,
        EnteredSchoolZone, SpeedingInSchoolZone, LeftSchoolZone,
        ApproachingParking, Parked, ReachedBarrier,
    }

    public enum DriveStage { Start, TrafficLight, Obstacle, SchoolZone, Parking, Done }

    public enum LightState { Green, Amber, Red }

    /// <summary>Objectives of the 45–60 s test drive. Pure rules; DriveDirector turns events into presentation.</summary>
    public sealed class DriveCourse
    {
        public float StopLineX = 110f;
        public float LightTriggerDistance = 55f;
        public float StopZoneDepth = 9f;          // valid stopping band before the line
        public float AmberTime = 1.6f;
        public float HoldToGreen = 1.2f;
        public float ObstacleStart = 239.5f;
        public float ObstacleEnd = 259f;
        public float SchoolStart = 360f;
        public float SchoolEnd = 470f;
        public float SchoolLimitKmh = 30f;
        public float ParkingX = 600f;
        public float ParkingTolerance = 1.2f;
        public float ParkingHold = 0.9f;
        public float BarrierX = 615f;

        public LightState Light { get; private set; } = LightState.Green;
        public DriveStage Stage { get; private set; } = DriveStage.Start;
        public bool RanRed { get; private set; }
        public bool StoppedCorrectly { get; private set; }
        public bool UsedAutoBrake { get; private set; }
        public bool SpedInSchool { get; private set; }
        public float MaxSchoolKmh { get; private set; }
        public bool IsParked { get; private set; }
        public float ParkingOffset { get; private set; }
        public float Elapsed { get; private set; }

        private float _lightTimer;
        private float _stillTimer;
        private float _farTimer;
        private bool _farHintGiven;
        private bool _obstacleWarned;
        private bool _passedObstacle;
        private bool _backInLane;
        private bool _schoolEntered, _schoolLeft, _speedingFlagged;
        private bool _parkingAnnounced;
        private float _parkTimer;
        private bool _wasAutoBraking;
        private readonly List<DriveEvent> _events = new List<DriveEvent>();

        public void Configure(LevelData level)
        {
            if (level == null) return;
            StopLineX = level.MarkerX("stop_line", StopLineX);
            var obs = level.FindMarker("obstacle");
            if (obs != null)
            {
                ObstacleStart = obs.X;
                ObstacleEnd = obs.X + obs.Extra.GetFloat("length", ObstacleEnd - ObstacleStart);
            }
            var school = level.FindMarker("school_start");
            if (school != null)
            {
                SchoolStart = school.X;
                SchoolLimitKmh = school.Extra.GetFloat("limit_kmh", SchoolLimitKmh);
            }
            SchoolEnd = level.MarkerX("school_end", SchoolEnd);
            var park = level.FindMarker("parking");
            if (park != null)
            {
                ParkingX = park.X;
                ParkingTolerance = park.Extra.GetFloat("tolerance", ParkingTolerance);
            }
            BarrierX = ParkingX + 15f;
        }

        /// <summary>The x the front bumper must not pass this frame (obstacle in lane, end barrier).</summary>
        public float StopLimit(VehicleModel car)
        {
            float limit = BarrierX;
            bool inNearLane = car.LaneT < 0.65f;
            if (inNearLane && car.Front < ObstacleStart + 0.5f)
                limit = Math.Min(limit, ObstacleStart - 0.35f);
            return limit;
        }

        public string Objective
        {
            get
            {
                switch (Stage)
                {
                    case DriveStage.Start: return Lines.DriveObjectiveStart;
                    case DriveStage.TrafficLight: return Light == LightState.Green && StoppedCorrectly ? Lines.DriveObjectiveContinue : Lines.DriveObjectiveLight;
                    case DriveStage.Obstacle: return _passedObstacle ? Lines.DriveObjectiveBackLane : Lines.DriveObjectiveObstacle;
                    case DriveStage.SchoolZone: return Lines.DriveObjectiveSchool;
                    case DriveStage.Parking: return Lines.DriveObjectiveParking;
                    default: return Lines.DriveObjectiveDone;
                }
            }
        }

        public IReadOnlyList<DriveEvent> Update(float dt, VehicleModel car)
        {
            _events.Clear();
            if (Stage == DriveStage.Done) return _events;
            Elapsed += dt;
            float front = car.Front;
            float speedAbs = Math.Abs(car.Speed);

            // ---- traffic light
            if (Light == LightState.Green && !StoppedCorrectly && !RanRed && front >= StopLineX - LightTriggerDistance && front < StopLineX)
            {
                Light = LightState.Amber;
                _lightTimer = 0f;
                Stage = DriveStage.TrafficLight;
                _events.Add(DriveEvent.LightAmber);
            }
            else if (Light == LightState.Amber)
            {
                _lightTimer += dt;
                if (_lightTimer >= AmberTime)
                {
                    Light = LightState.Red;
                    _lightTimer = 0f;
                    _events.Add(DriveEvent.LightRed);
                }
            }
            else if (Light == LightState.Red)
            {
                if (front > StopLineX + 0.5f)
                {
                    RanRed = true;
                    Light = LightState.Green;
                    _events.Add(DriveEvent.RanRedLight);
                    _events.Add(DriveEvent.LightGreen);
                }
                else if (speedAbs < 0.15f)
                {
                    if (front >= StopLineX - StopZoneDepth)
                    {
                        _stillTimer += dt;
                        if (_stillTimer >= HoldToGreen)
                        {
                            StoppedCorrectly = true;
                            Light = LightState.Green;
                            _events.Add(DriveEvent.StoppedAtLight);
                            _events.Add(DriveEvent.LightGreen);
                        }
                    }
                    else
                    {
                        _farTimer += dt;
                        if (_farTimer > 2.5f && !_farHintGiven)
                        {
                            _farHintGiven = true;
                            _events.Add(DriveEvent.TooFarFromLine);
                        }
                    }
                }
                else
                {
                    _stillTimer = 0f;
                }
            }
            if (Stage == DriveStage.Start && front >= StopLineX - LightTriggerDistance) Stage = DriveStage.TrafficLight;
            if (Stage == DriveStage.TrafficLight && front > StopLineX + 4f && Light == LightState.Green) Stage = DriveStage.Obstacle;

            // ---- obstacle in the near lane
            if (!_obstacleWarned && front >= ObstacleStart - 60f && front < ObstacleStart)
            {
                _obstacleWarned = true;
                if (Stage < DriveStage.Obstacle) Stage = DriveStage.Obstacle;
                _events.Add(DriveEvent.ObstacleAhead);
            }
            if (car.AutoBraking && !_wasAutoBraking && front > ObstacleStart - 30f && front < ObstacleStart + 1f)
            {
                UsedAutoBrake = true;
                _events.Add(DriveEvent.AutoBrake);
            }
            _wasAutoBraking = car.AutoBraking;
            if (!_passedObstacle && car.X - car.HalfLength > ObstacleEnd)
            {
                _passedObstacle = true;
                _events.Add(DriveEvent.PassedObstacle);
            }
            if (_passedObstacle && !_backInLane && car.LaneT < 0.05f)
            {
                _backInLane = true;
                _events.Add(DriveEvent.BackInLane);
            }

            // ---- school zone
            bool inSchool = car.X >= SchoolStart && car.X <= SchoolEnd;
            if (inSchool && !_schoolEntered)
            {
                _schoolEntered = true;
                Stage = DriveStage.SchoolZone;
                _events.Add(DriveEvent.EnteredSchoolZone);
            }
            if (inSchool)
            {
                MaxSchoolKmh = Math.Max(MaxSchoolKmh, car.Kmh);
                if (!_speedingFlagged && car.Kmh > SchoolLimitKmh + 2f)
                {
                    _speedingFlagged = true;
                    SpedInSchool = true;
                    _events.Add(DriveEvent.SpeedingInSchoolZone);
                }
            }
            if (_schoolEntered && !_schoolLeft && car.X > SchoolEnd)
            {
                _schoolLeft = true;
                Stage = DriveStage.Parking;
                _events.Add(DriveEvent.LeftSchoolZone);
            }

            // ---- parking
            if (!_parkingAnnounced && front >= ParkingX - 45f)
            {
                _parkingAnnounced = true;
                if (Stage < DriveStage.Parking) Stage = DriveStage.Parking;
                _events.Add(DriveEvent.ApproachingParking);
            }
            if (front >= BarrierX - 0.05f && speedAbs < 0.1f)
                _events.Add(DriveEvent.ReachedBarrier);
            float offset = car.X - ParkingX;
            if (Stage == DriveStage.Parking && Math.Abs(offset) <= ParkingTolerance && car.LaneT < 0.15f && speedAbs < 0.08f)
            {
                _parkTimer += dt;
                if (_parkTimer >= ParkingHold)
                {
                    IsParked = true;
                    ParkingOffset = Math.Abs(offset);
                    Stage = DriveStage.Done;
                    _events.Add(DriveEvent.Parked);
                }
            }
            else
            {
                _parkTimer = 0f;
            }
            return _events;
        }

        public int ParkingCentimetres => (int)Math.Round(ParkingOffset * VehicleModel.MetresPerUnit * 100f);

        /// <summary>Deadpan score out of 10 (one decimal).</summary>
        public float Score()
        {
            float s = 10f;
            if (RanRed) s -= 1.5f;
            else if (!StoppedCorrectly) s -= 0.5f;
            if (UsedAutoBrake) s -= 0.5f;
            if (SpedInSchool) s -= 1.0f;
            s -= Math.Min(1.2f, ParkingCentimetres / 60f);
            s = Math.Max(0f, Math.Min(10f, s));
            return (float)Math.Round(s, 1);
        }
    }
}

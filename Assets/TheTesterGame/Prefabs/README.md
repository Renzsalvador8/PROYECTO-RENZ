# Prefabs

The game assembles its objects at runtime from data, so no prefabs are required:

* Jean Paul Tester — `TesterRig.Create("tester_side", …)` from `Data/Rigs/tester_side.json` + the character atlas.
* Levels — `LevelInstance.Build(...)` from `Data/Levels/*.json`.
* The IONIQ 5 for the drive — `VehicleDrivingController.Create(...)`.
* UI — `UIManager` (built in code with uGUI).

If you want designer-facing prefabs, enter Play mode, select the generated object in the Hierarchy and drag it here.
Note that sprites created at runtime are not assets, so re-point sprite references to the textures in `Art/Resources`.

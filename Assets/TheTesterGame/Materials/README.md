# Materials

No custom materials are needed: every sprite uses the default sprite material, which keeps the game render-pipeline
agnostic (Built-in or URP 2D) and avoids shader compilation risk on WebGL. Lighting is painted into the art and
layered with translucent light sprites (spot cones, light shafts, glows).

#!/usr/bin/env bash
# Downloads Unity reference assemblies (NuGet) used to compile-check the game's C# without the Unity Editor.
# These are API stubs from older Unity versions (2021.x) — good for catching syntax/type errors.
# The real verification remains opening the project in Unity 6.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p .refs
fetch() {
  local id=$1 ver=$2
  if [ ! -d ".refs/$id" ]; then
    curl -sSL -o ".refs/$id.nupkg" "https://api.nuget.org/v3-flatcontainer/$id/$ver/$id.$ver.nupkg"
    mkdir -p ".refs/$id" && (cd ".refs/$id" && unzip -q -o "../$id.nupkg")
  fi
}
fetch unityengine.modules 2021.3.33
fetch unity3d.unityengine.ui 2020.3.21
fetch unity3d.sdk 2021.1.14.1
echo "refs ready in $(pwd)/.refs"

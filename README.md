# angle-openomsi

Builds of Google's [ANGLE](https://chromium.googlesource.com/angle/angle) for openOMSI's
"ANGLE (DirectX 11)" graphics option on Windows: OpenGL ES 3.0 over Direct3D 11, for older
graphics cards whose DirectX 12, Vulkan and OpenGL drivers do not run openOMSI. openOMSI's
fork of wgpu ([wgpu-openomsi](https://github.com/openOMSI-Project/wgpu-openomsi), the `angle`
feature) loads `libEGL.dll` and `libGLESv2.dll` from the game's folder.

* `ANGLE_REVISION`: the ANGLE branch and commit that is built.
* `args.gn`: the build arguments (Direct3D 11 only, x64, release).
* `.github/workflows/build.yml`: builds them on GitHub Actions when either changes (or by
  hand) and publishes a release `angle-<branch>-<commit>-r<recipe>` with the DLLs, ANGLE's licence,
  the revision, the arguments, `SHA256SUMS`, and a build provenance attestation
  (`gh attestation verify <file> --repo openOMSI-Project/angle-openomsi`).

Nothing here is modified ANGLE: the DLLs are built from the upstream source as it is. ANGLE
is BSD-licensed; its licence travels with every release as `LICENSE-ANGLE.txt`.

To move to a newer ANGLE: put another `chromium/<branch> <commit>` in `ANGLE_REVISION`,
push, and point openOMSI's Windows packaging at the new release tag and checksum.

The recipe suffix hashes the pinned revision, GN arguments, workflow and identity helper,
so changing build settings without changing ANGLE's source creates a new release instead of
silently reusing the previous DLLs. Existing release tags are left intact. Pull requests run
the recipe tests only; the Windows build and release run after a push to main or a manual run.

"""Identify the pinned ANGLE source and the recipe used to build its DLLs."""

import hashlib
from pathlib import Path
import re


def build_id(root: Path) -> dict[str, str]:
    fields = (root / "ANGLE_REVISION").read_text(encoding="utf-8").split()
    if len(fields) != 2:
        raise ValueError("ANGLE_REVISION must contain a chromium branch and a full commit SHA")
    branch, sha = fields
    match = re.fullmatch(r"chromium/([0-9]+)", branch)
    if match is None or re.fullmatch(r"[0-9a-f]{40}", sha) is None:
        raise ValueError("ANGLE_REVISION must contain chromium/<number> and a full lowercase SHA")
    recipe = hashlib.sha256()
    for name in ("ANGLE_REVISION", "args.gn", ".github/workflows/build.yml", "tools/build_id.py"):
        data = (root / name).read_bytes().replace(b"\r\n", b"\n")
        recipe.update(name.encode("utf-8") + b"\0")
        recipe.update(str(len(data)).encode("ascii") + b"\0" + data)
    digest = recipe.hexdigest()
    return {
        "branch": branch,
        "sha": sha,
        "recipe_sha256": digest,
        "tag": f"angle-{match[1]}-{sha[:10]}-r{digest[:12]}",
    }


if __name__ == "__main__":
    for key, value in build_id(Path(__file__).resolve().parents[1]).items():
        print(f"{key}={value}")

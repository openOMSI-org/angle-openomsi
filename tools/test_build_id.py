import importlib.util
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("build_id", Path(__file__).with_name("build_id.py"))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class BuildIdTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.files = {
            "ANGLE_REVISION": "chromium/8091 " + "a" * 40 + "\n",
            "args.gn": 'target_cpu = "x64"\n',
            ".github/workflows/build.yml": "name: Build ANGLE\n",
            "tools/build_id.py": "# build identity\n",
        }
        for name, data in self.files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(data, encoding="utf-8", newline="")

    def test_same_recipe_has_the_same_identity(self):
        result = MODULE.build_id(self.root)
        self.assertEqual(result, MODULE.build_id(self.root))
        self.assertRegex(result["tag"], r"^angle-8091-a{10}-r[0-9a-f]{12}$")
        self.assertEqual(len(result["recipe_sha256"]), 64)

    def test_every_build_input_changes_the_release_identity(self):
        before = MODULE.build_id(self.root)["tag"]
        for name in ("args.gn", ".github/workflows/build.yml", "tools/build_id.py"):
            with self.subTest(name=name):
                path = self.root / name
                path.write_text(self.files[name] + "# changed\n", encoding="utf-8")
                self.assertNotEqual(before, MODULE.build_id(self.root)["tag"])
                path.write_text(self.files[name], encoding="utf-8")

    def test_windows_checkout_line_endings_do_not_change_the_identity(self):
        before = MODULE.build_id(self.root)
        for name, data in self.files.items():
            (self.root / name).write_bytes(data.replace("\n", "\r\n").encode("utf-8"))
        self.assertEqual(before, MODULE.build_id(self.root))

    def test_revision_changes_are_in_the_tag_and_recipe(self):
        before = MODULE.build_id(self.root)
        (self.root / "ANGLE_REVISION").write_text("chromium/8092 " + "b" * 40, encoding="utf-8")
        after = MODULE.build_id(self.root)
        self.assertTrue(after["tag"].startswith("angle-8092-" + "b" * 10 + "-r"))
        self.assertNotEqual(before["recipe_sha256"], after["recipe_sha256"])

    def test_invalid_revision_is_rejected(self):
        for value in ("", "chromium/8091 short", "wrong " + "a" * 40, "chromium/8091 " + "a" * 40 + " extra"):
            with self.subTest(value=value):
                (self.root / "ANGLE_REVISION").write_text(value, encoding="utf-8")
                with self.assertRaises(ValueError):
                    MODULE.build_id(self.root)

    def test_missing_build_input_is_not_silently_ignored(self):
        (self.root / "args.gn").unlink()
        with self.assertRaises(FileNotFoundError):
            MODULE.build_id(self.root)


if __name__ == "__main__":
    unittest.main()

"""Tests for Linux launcher and package layout, using synthetic overlay bytes."""
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

ROOT = Path(__file__).parent

def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

launcher = load("ativar_ptbr_linux")
packer = load("build_linux_packages")

class LinuxTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)
        self.data = self.dir / "data"
        self.data.mkdir()
        self.o3ro = self.data / "mods" / "OoT3D-PTBR" / "OoT3D-PTBR.o3ro"
        self.o3ro.parent.mkdir(parents=True)
        self.o3ro.write_bytes(b"synthetic-translation-fixture")
        self.digest = hashlib.sha256(self.o3ro.read_bytes()).hexdigest()

    def test_launcher_backup_and_idempotence(self):
        profile = self.data / "TriAevum.launch.json"
        before = {"arguments": ["--ui-texture-pack", "original-path"], "other": "keep"}
        profile.write_text(json.dumps(before))
        with patch.object(launcher, "EXPECTED", self.digest):
            launcher.activate(self.dir)
            launcher.activate(self.dir)
        after = json.loads(profile.read_text())
        self.assertEqual(after["arguments"].count("--romfs-overlay"), 1)
        self.assertEqual(after["arguments"][-1], str(self.o3ro.resolve()))
        self.assertEqual(after["arguments"][:2], before["arguments"])
        self.assertEqual(json.loads((self.data / "TriAevum.launch.json.backup-antes-ptbr.json").read_text()), before)

    def test_invalid_overlay_preserves_profile(self):
        profile = self.data / "TriAevum.launch.json"
        profile.write_text('{"arguments": []}')
        with self.assertRaises(ValueError):
            launcher.activate(self.dir)
        self.assertEqual(profile.read_text(), '{"arguments": []}')

    def test_linux_packages_have_correct_structure(self):
        source = self.dir / "windows.zip"
        with ZipFile(source, "w") as z:
            z.writestr("Ativar-PTBR.cmd", "")
            z.writestr("Ativar-PTBR.ps1", "")
            z.writestr("LEIA-ME.txt", "Créditos")
            z.write(self.o3ro, packer.OVERLAY)
        with patch.object(packer, "EXPECTED", self.digest):
            outputs = packer.build(source, self.dir / "out")
        self.assertEqual(len(outputs), 2)
        for output in outputs:
            with ZipFile(output) as z:
                self.assertIn(packer.OVERLAY, z.namelist())
                self.assertIn("LEIA-ME.txt", z.namelist())
                self.assertIn("LEIA-ME-LINUX.txt", z.namelist())
                self.assertIn("Ativar-PTBR-Linux.sh", z.namelist())

if __name__ == "__main__":
    unittest.main()

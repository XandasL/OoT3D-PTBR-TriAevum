"""Offline tests: synthetic O3RO fixture, never real copyrighted assets."""
import hashlib
import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

SCRIPT = Path(__file__).with_name("gerar_zip_local.py")
spec = importlib.util.spec_from_file_location("gerar_zip_local", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class CleanPackageTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.o3ro = self.root / "fixture.o3ro"
        self.o3ro.write_bytes(b"synthetic fixture, not a real ROMFS overlay")
        self.zip = self.root / "package.zip"

    def test_exact_members_without_images(self):
        with patch.object(module, "EXPECTED", hashlib.sha256(self.o3ro.read_bytes()).hexdigest()):
            module.generate(self.o3ro, self.zip)
        with zipfile.ZipFile(self.zip) as archive:
            self.assertEqual(tuple(archive.namelist()), module.MEMBERS)
            self.assertFalse(any(p.lower().endswith((".png", ".ctxb", ".jpg")) for p in archive.namelist()))
            self.assertEqual(archive.read(module.MEMBERS[-1]), self.o3ro.read_bytes())

    def test_invalid_digest_does_not_create_zip(self):
        with self.assertRaisesRegex(ValueError, "Hash"):
            module.generate(self.o3ro, self.zip)
        self.assertFalse(self.zip.exists())

    def test_existing_zip_not_overwritten(self):
        self.zip.write_bytes(b"existing")
        with patch.object(module, "EXPECTED", hashlib.sha256(self.o3ro.read_bytes()).hexdigest()):
            with self.assertRaisesRegex(ValueError, "existe"):
                module.generate(self.o3ro, self.zip)
        self.assertEqual(self.zip.read_bytes(), b"existing")

if __name__ == "__main__":
    unittest.main()

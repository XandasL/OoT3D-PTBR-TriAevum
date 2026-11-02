import hashlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

ROOT = Path(__file__).parent
spec = importlib.util.spec_from_file_location("build_linux_packages", ROOT / "build_linux_packages.py")
packer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(packer)

class LinuxPackageTest(unittest.TestCase):
    def test_bash_packages(self):
        with tempfile.TemporaryDirectory() as td:
            folder = Path(td)
            source = folder / "windows.zip"
            payload = b"synthetic-fixture"
            with ZipFile(source, "w") as z:
                z.writestr("Ativar-PTBR.cmd", "")
                z.writestr("Ativar-PTBR.ps1", "")
                z.writestr("LEIA-ME.txt", "creditos")
                z.writestr(packer.OVERLAY, payload)
            with patch.object(packer, "EXPECTED", hashlib.sha256(payload).hexdigest()):
                outputs = packer.build(source, folder / "out")
            self.assertEqual(len(outputs), 2)
            for out in outputs:
                with ZipFile(out) as z:
                    self.assertEqual(set(z.namelist()), {packer.OVERLAY, "LEIA-ME.txt", "LEIA-ME-LINUX.txt", "Ativar-PTBR-Linux.sh"})
                    self.assertNotIn("ativar_ptbr_linux.py", z.namelist())
                    self.assertIn(b"jq", z.read("Ativar-PTBR-Linux.sh"))
                    self.assertEqual(z.read(packer.OVERLAY), payload)

if __name__ == "__main__":
    unittest.main()

"""Safety tests for switching PT-BR font modes without modifying game content."""
import importlib.util
import hashlib
from pathlib import Path
import tempfile
import unittest

MODULE_PATH = Path(__file__).parent / "installer" / "font_mode.py"
spec = importlib.util.spec_from_file_location("ptbr_font_mode_test", MODULE_PATH)
manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manager)


class FontModeTests(unittest.TestCase):
    def test_original_from_existing_noto_and_back(self):
        with tempfile.TemporaryDirectory() as temp:
            pack = Path(temp) / "font_coverage.zip"
            original = b"previous-user-HD-asset"
            noto = b"generated-HD-asset"
            pack.write_bytes(original)
            self.assertEqual(manager.choose(pack, "hd", lambda: noto), "hd")
            self.assertEqual(pack.read_bytes(), noto)
            receipt, backup, disabled = manager.paths(pack)
            self.assertEqual(backup.read_bytes(), original)
            self.assertEqual(manager.choose(pack, "original"), "original")
            self.assertEqual(pack.read_bytes(), original)
            self.assertEqual(disabled.read_bytes(), noto)
            self.assertEqual(manager.choose(pack, "hd", lambda: noto), "hd")
            self.assertEqual(pack.read_bytes(), noto)
            self.assertFalse(disabled.exists())
            manager.restore_previous(pack)
            self.assertEqual(pack.read_bytes(), original)
            self.assertFalse(receipt.exists())
            self.assertFalse(backup.exists())

    def test_default_original_does_not_require_hd_font(self):
        with tempfile.TemporaryDirectory() as temp:
            pack = Path(temp) / "font_coverage.zip"
            self.assertEqual(manager.choose(pack, "original"), "unchanged")
            self.assertFalse(pack.exists())
            self.assertIsNone(manager.read_state(pack))
            manager.restore_previous(pack)
            self.assertFalse(pack.exists())

    def test_disable_legacy_pack_and_restore_exact_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            pack = Path(temp) / "font_coverage.zip"
            pack.write_bytes(b"legacy-original")
            self.assertEqual(manager.choose(pack, "original"), "unchanged")
            self.assertEqual(pack.read_bytes(), b"legacy-original")
            manager.restore_previous(pack)
            self.assertEqual(pack.read_bytes(), b"legacy-original")

    def test_reject_tampered_active_noto(self):
        with tempfile.TemporaryDirectory() as temp:
            pack = Path(temp) / "font_coverage.zip"
            manager.choose(pack, "hd", lambda: b"trusted")
            pack.write_bytes(b"modified")
            with self.assertRaisesRegex(RuntimeError, "alterados"):
                manager.choose(pack, "original")
            self.assertEqual(pack.read_bytes(), b"modified")

    def test_reject_tampered_disabled_noto(self):
        with tempfile.TemporaryDirectory() as temp:
            pack = Path(temp) / "font_coverage.zip"
            manager.choose(pack, "hd", lambda: b"trusted")
            manager.choose(pack, "original")
            manager.paths(pack)[2].write_bytes(b"modified")
            with self.assertRaisesRegex(RuntimeError, "alterado"):
                manager.choose(pack, "hd", lambda: b"replacement")
            self.assertFalse(pack.exists())

    def test_reject_unknown_preexisting_orphan_backup(self):
        with tempfile.TemporaryDirectory() as temp:
            pack = Path(temp) / "font_coverage.zip"
            manager.paths(pack)[1].write_bytes(b"user-data")
            with self.assertRaisesRegex(RuntimeError, "sem recibo"):
                manager.choose(pack, "original")
            self.assertEqual(manager.paths(pack)[1].read_bytes(), b"user-data")

    def test_reject_invalid_mode(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                manager.choose(Path(temp) / "font_coverage.zip", "unknown")


if __name__ == "__main__":
    unittest.main()

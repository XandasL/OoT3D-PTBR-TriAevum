"""Synthetic regression checks: journal and preservation of a user's font pack."""
import importlib.util
from pathlib import Path
import tempfile
import unittest

MODULES = Path(__file__).resolve().parent / "installer"


def load(name):
    spec = importlib.util.spec_from_file_location("test_v130_" + name, MODULES / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SafetySmokeTests(unittest.TestCase):
    def test_original_font_does_not_disable_user_pack(self):
        font = load("font_mode")
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "font_coverage.zip"
            path.write_bytes(b"existing user texture/font coverage")
            self.assertEqual(font.choose(path, "original"), "unchanged")
            self.assertEqual(path.read_bytes(), b"existing user texture/font coverage")
            self.assertIsNone(font.read_state(path))

    def test_hd_original_hd_and_restore_user_font(self):
        font = load("font_mode")
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "font_coverage.zip"
            path.write_bytes(b"user font")
            self.assertEqual(font.choose(path, "hd", lambda: b"generated hd"), "hd")
            self.assertEqual(path.read_bytes(), b"generated hd")
            self.assertEqual(font.choose(path, "original"), "original")
            self.assertEqual(path.read_bytes(), b"user font")
            self.assertEqual(font.read_state(path)["mode"], "original")
            self.assertEqual(font.choose(path, "hd", lambda: b"generated hd"), "hd")
            self.assertEqual(path.read_bytes(), b"generated hd")
            font.restore_previous(path)
            self.assertEqual(path.read_bytes(), b"user font")
            self.assertIsNone(font.read_state(path))

    def test_pending_journal_blocks_new_operation(self):
        transaction = load("transaction_guard")
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            target = transaction.write_journal(root, {
                "format": "oot3d_ptbr_v130_transaction_v1",
                "operation": "install", "phase": "preparing",
            })
            self.assertIsNotNone(transaction.pending(root))
            with self.assertRaises(transaction.PendingTransaction):
                transaction.refuse_pending(root)
            with self.assertRaises(transaction.PendingTransaction):
                transaction.write_journal(root, {"format": "oot3d_ptbr_v130_transaction_v1"})
            transaction.complete_journal(target)
            self.assertIsNone(transaction.pending(root))

    def test_durable_replace_writes_complete_file(self):
        transaction = load("transaction_guard")
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "profile.json"
            transaction.durable_replace(p, b"original")
            transaction.durable_replace(p, b"translated")
            self.assertEqual(p.read_bytes(), b"translated")


if __name__ == "__main__":
    unittest.main()

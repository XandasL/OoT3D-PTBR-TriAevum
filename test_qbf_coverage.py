import importlib.util
import struct
import unittest
from pathlib import Path

path = Path(__file__).parent / "installer" / "qbf_coverage.py"
spec = importlib.util.spec_from_file_location("qbf_coverage", path)
import sys
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def fake_qbf(codes):
    raw = bytearray(16 + 8 * len(codes))
    raw[:4] = b"QBF1"
    struct.pack_into("<H", raw, 4, len(codes))
    for i, code in enumerate(codes):
        struct.pack_into("<H", raw, 16 + 8 * i, code)
    return bytes(raw)


class QbfCoverageTests(unittest.TestCase):
    def test_complete_ptbr_coverage(self):
        result = module.inspect_qbf_coverage(fake_qbf(map(ord, module.PTBR_CHARS)))
        self.assertTrue(result.covers_ptbr)
        self.assertEqual(result.missing_ptbr, ())

    def test_missing_accents_are_reported(self):
        result = module.inspect_qbf_coverage(fake_qbf([ord("a"), ord("ç")]))
        self.assertFalse(result.covers_ptbr)
        self.assertIn("ã", result.missing_ptbr)
        self.assertNotIn("ç", result.missing_ptbr)

    def test_rejects_invalid_or_truncated_table(self):
        for data in (b"", b"BAD!", b"QBF1" + b"\\x00" * 12,
                     fake_qbf([65])[:16]):
            with self.subTest(data=data):
                with self.assertRaises(ValueError):
                    module.inspect_qbf_coverage(data)

    def test_rejects_duplicate_codes(self):
        with self.assertRaisesRegex(ValueError, "duplicados"):
            module.inspect_qbf_coverage(fake_qbf([65, 65]))


if __name__ == "__main__":
    unittest.main()

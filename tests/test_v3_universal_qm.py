"""Regression tests for the validated v3.0 universal message conversion."""
import hashlib
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
import build_v3_universal_qm as qm


def fake_qm():
    size = qm.TABLE_END
    data = bytearray(size)
    import struct
    struct.pack_into("<4sIII", data, 0, b"QM\\0\\0", 4, qm.RECORD_COUNT, 0)
    for i in range(qm.RECORD_COUNT):
        struct.pack_into("<4I", data, 16 + i * 96, i + 1, 0, 2, 3)
    return data


class UniversalQmTests(unittest.TestCase):
    def test_rebuild_deduplicates_and_preserves_european_slots(self):
        import struct
        eur = fake_qm()
        source = fake_qm()
        original_text = b"Original English"
        eur.extend(original_text)
        # Keep a native EUR English entry and another European language.
        struct.pack_into("<II", eur, 16 + 16 + 2 * 8, qm.TABLE_END, len(original_text))
        struct.pack_into("<II", eur, 16 + 16 + 4 * 8, qm.TABLE_END, len(original_text))
        portuguese_text = b"Texto em portugues"
        source.extend(portuguese_text)
        for i in (0, 1):
            struct.pack_into("<II", source, 16 + i * 96 + 24,
                             qm.TABLE_END, len(portuguese_text))
        with patch.object(qm, "EUR_QM_SHA256", hashlib.sha256(eur).hexdigest()), \
             patch.object(qm, "V2_QM_SHA256", hashlib.sha256(source).hexdigest()), \
             patch.object(qm, "V3_QM_SHA256", None):
            # Verify mechanics with a synthetic result, then the final hash guard.
            with self.assertRaisesRegex(ValueError, "in-game-tested"):
                qm.build_universal_qm(bytes(eur), bytes(source))
            expected = bytearray(eur)
            expected.extend(b"\\0" * (-len(expected) % 4))
            offset = len(expected)
            expected.extend(portuguese_text)
            for i in (0, 1):
                for slot in (1, 2):
                    struct.pack_into("<II", expected, 16 + i * 96 + 16 + slot * 8,
                                     offset, len(portuguese_text))
            with patch.object(qm, "V3_QM_SHA256", hashlib.sha256(expected).hexdigest()):
                result = qm.build_universal_qm(bytes(eur), bytes(source))
        self.assertEqual(result, bytes(expected))
        self.assertEqual(result.count(portuguese_text), 1)
        self.assertEqual(result[qm.TABLE_END:qm.TABLE_END + len(original_text)],
                         original_text)

    def test_mismatched_record_identifiers_are_rejected(self):
        eur, source = fake_qm(), fake_qm()
        source[16] ^= 1
        with patch.object(qm, "EUR_QM_SHA256", hashlib.sha256(eur).hexdigest()), \
             patch.object(qm, "V2_QM_SHA256", hashlib.sha256(source).hexdigest()):
            with self.assertRaisesRegex(ValueError, "record IDs differ"):
                qm.build_universal_qm(bytes(eur), bytes(source))


if __name__ == "__main__":
    unittest.main()

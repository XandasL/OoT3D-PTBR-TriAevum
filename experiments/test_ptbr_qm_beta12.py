"""Synthetic no-ROM tests for beta.1.2 QM conversion and target routing."""
from __future__ import annotations

import hashlib
import importlib.util
import pathlib
import struct
import sys
import unittest
from unittest.mock import patch

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ptbr_qm_beta12 as qm
import build_ptbr_o3ro_beta12 as overlay


def fixture() -> bytes:
    table = 16 + qm.EXPECTED_RECORDS * qm.RECORD_SIZE
    pt = "Hyrule ä ö Ä Ö".encode("utf-8")
    fr = b"bonjour"
    es = b"hola"
    output = bytearray(table + len(pt) + len(fr) + len(es))
    struct.pack_into("<4sIII", output, 0, b"QM\x00\x00", 4, qm.EXPECTED_RECORDS, 0)
    for slot, offset, data in ((1, table, pt), (5, table + len(pt), fr),
                               (7, table + len(pt) + len(fr), es)):
        struct.pack_into("<II", output, 16 + 16 + slot * 8, offset, len(data))
        output[offset:offset + len(data)] = data
    return bytes(output)


class QmConversionTests(unittest.TestCase):
    def convert_fixture(self, original):
        with patch.object(qm, "EXPECTED_QM_SHA256", hashlib.sha256(original).hexdigest()):
            return qm.convert_usa_to_eur(original)

    def test_eur_slots_and_ptbr_tildes(self):
        original = fixture()
        converted = self.convert_fixture(original)
        self.assertEqual(len(converted), len(original))
        for target, source in qm.SLOT_MAP:
            field = 32 + target * 8
            original_field = 32 + source * 8
            self.assertEqual(converted[field:field + 8], original[original_field:original_field + 8])
        payload_start = 16 + qm.EXPECTED_RECORDS * qm.RECORD_SIZE
        self.assertEqual(converted[payload_start:payload_start + len("Hyrule ä ö Ä Ö".encode())],
                         "Hyrule ã õ Ã Õ".encode("utf-8"))
        self.assertIn(b"bonjourhola", converted)
        self.assertEqual(self.convert_fixture(original), converted)

    def test_reject_unknown_hash(self):
        with self.assertRaisesRegex(ValueError, "SHA-256"):
            qm.convert_usa_to_eur(fixture())

    def test_reject_invalid_span(self):
        original = bytearray(fixture())
        # Source slot 1 points into table rather than text region.
        struct.pack_into("<II", original, 32 + 8, 5, 12)
        with self.assertRaisesRegex(ValueError, "outside valid payload"):
            self.convert_fixture(bytes(original))

    def test_reject_shared_pt_and_fr_span(self):
        original = bytearray(fixture())
        portuguese_offset, portuguese_size = struct.unpack_from("<II", original, 40)
        struct.pack_into("<II", original, 32 + 5 * 8, portuguese_offset, portuguese_size)
        with self.assertRaisesRegex(ValueError, "overlaps another language"):
            self.convert_fixture(bytes(original))

    def test_romfs_mapping(self):
        self.assertEqual(overlay.source_targets("message/us/us.qm"), "message/eu/eu.qm")
        self.assertEqual(overlay.source_targets("message/us/ltn16.qbf"), "message/eu/ltn16.qbf")
        self.assertEqual(overlay.source_targets("misc/us/english/ura.ctxb"),
                         "misc/eu/english/ura.ctxb")
        self.assertEqual(overlay.source_targets("actor/a.zar"), "actor/a.zar")
        self.assertEqual(len(overlay.EU_MIRRORS), 14)


if __name__ == "__main__":
    unittest.main()

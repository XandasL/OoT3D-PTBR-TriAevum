import importlib.util
import struct
import sys
import unittest
from pathlib import Path

source = Path(__file__).parent / "installer" / "build_open_hd_qbf.py"
spec = importlib.util.spec_from_file_location("build_open_hd_qbf", source)
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def qbf(entries, glyphs=2, fallback=65):
    raw = bytearray(16 + 8 * len(entries) + glyphs * 128)
    raw[:4] = b"QBF1"
    struct.pack_into("<HHH", raw, 4, len(entries), glyphs, fallback)
    raw[12:16] = bytes((4, 16, 16, 2))
    for i, (code, index) in enumerate(entries):
        struct.pack_into("<HH", raw, 16 + 8 * i, code, index)
    return bytes(raw)


class OpenQbfTests(unittest.TestCase):
    def test_valid_native_directory(self):
        self.assertEqual(module.parse_native(qbf([(65, 0), (66, 1)])),
                         ([(65, 0), (66, 1)], 2))

    def test_rejects_duplicate_and_unsorted_codes(self):
        for entries in ([(65, 0), (65, 1)], [(66, 0), (65, 1)]):
            with self.subTest(entries=entries), self.assertRaises(ValueError):
                module.parse_native(qbf(entries))

    def test_rejects_invalid_glyph_index(self):
        with self.assertRaises(ValueError):
            module.parse_native(qbf([(65, 2)]))

    def test_rejects_wrong_bitmap_extent(self):
        with self.assertRaises(ValueError):
            module.parse_native(qbf([(65, 0)])[:-1])

    def test_rejects_wrong_encoding(self):
        data = bytearray(qbf([(65, 0)]))
        data[15] = 3
        with self.assertRaises(ValueError):
            module.parse_native(bytes(data))

    def test_rejects_invalid_pixel_size(self):
        with self.assertRaises(ValueError):
            module.build_hd_qbf(qbf([(65, 0)]), "unused.ttf", pixel_size=100)


if __name__ == "__main__":
    unittest.main()

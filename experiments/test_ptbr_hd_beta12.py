"""Local-only regression checks for the authored HD ZIP contract."""
import io
import tempfile
import unittest
import zipfile
from pathlib import Path

from install_ptbr_hd_vanilla_beta12 import ATLAS, parse_zip, png_dimensions, find_targets


def png(w, h):
    import struct
    return b"\x89PNG\r\n\x1a\n" + struct.pack(">I", 13) + b"IHDR" + struct.pack(">II", w, h) + b"\x08\x06\x00\x00\x00" + b"\x00\x00\x00\x00"


class TextureZipTests(unittest.TestCase):
    def test_final_zip_contract(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "textures.zip"
            atlas = png(4096, 2048)
            with zipfile.ZipFile(p, "w") as z:
                z.writestr("TopScreen/ui_atlas_hd.png", atlas)
                z.writestr("VanillaUI/" + ATLAS, atlas)
                for n in range(19):
                    z.writestr(f"VanillaUI/tex1_{n}.png", png(512, 256))
            found = parse_zip(p)
            self.assertEqual(len(found), 21)

    def test_reject_disagreeing_atlas(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "textures.zip"
            with zipfile.ZipFile(p, "w") as z:
                z.writestr("TopScreen/ui_atlas_hd.png", png(4096, 2048))
                z.writestr("VanillaUI/" + ATLAS, png(2048, 1024))
                for n in range(19):
                    z.writestr(f"VanillaUI/tex1_{n}.png", png(512, 256))
            with self.assertRaisesRegex(ValueError, "differ"):
                parse_zip(p)

    def test_ambiguous_basename_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            base = Path(d)
            files = []
            for lang in ("01_US_ENGLISH", "02_EU_ENGLISH"):
                f = base / "languages" / lang / "UI" / "sample.png"
                f.parent.mkdir(parents=True)
                f.write_bytes(b"x")
                files.append(f)
            with self.assertRaisesRegex(ValueError, "Ambiguous"):
                find_targets(base, "VanillaUI/sample.png", files)


if __name__ == "__main__":
    unittest.main()

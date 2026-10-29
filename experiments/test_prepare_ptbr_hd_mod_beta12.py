"""Tests for local HD mod preparation with no runtime modifications."""
import tempfile
import unittest
from pathlib import Path

from prepare_ptbr_hd_mod_beta12 import plan
from install_ptbr_hd_vanilla_beta12 import ATLAS

class HdModMappingTests(unittest.TestCase):
    def test_missing_target_is_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaisesRegex(ValueError, "Missing Vanilla original"):
                from unittest.mock import patch
                with patch("prepare_ptbr_hd_mod_beta12.parse_zip",
                           return_value={"VanillaUI/not_here.png": b"x",
                                         "TopScreen/ui_atlas_hd.png": b"y"}):
                    plan(Path("not-read.zip"), Path(t), {})

    def test_does_not_guess_duplicate_basenames(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            for name in ("common", "languages/02_EU_ENGLISH"):
                p = root / name / "UI" / ATLAS
                p.parent.mkdir(parents=True)
                p.write_bytes(b"texture")
            from unittest.mock import patch
            with patch("prepare_ptbr_hd_mod_beta12.parse_zip",
                       return_value={"VanillaUI/" + ATLAS: b"texture",
                                     "TopScreen/ui_atlas_hd.png": b"texture"}):
                with self.assertRaisesRegex(ValueError, "Ambiguous"):
                    plan(Path("not-read.zip"), root, {})

if __name__ == "__main__":
    unittest.main()

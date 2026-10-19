import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).parent / "installer"
sys.path.insert(0, str(ROOT))
spec = importlib.util.spec_from_file_location("open_font_atlas", ROOT / "open_font_atlas.py")
atlas = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = atlas
spec.loader.exec_module(atlas)


class OpenFontAtlasTests(unittest.TestCase):
    def test_rejects_oversized_cells(self):
        with self.assertRaises(ValueError):
            atlas.render_ptbr_atlas("missing.ttf", "unused", cell_size=512)

    def test_rejects_missing_accents_before_writing(self):
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "out"
            with patch.object(atlas, "check_font_coverage", return_value={
                "covers_ptbr": False, "missing_ptbr": ["ã", "ç"]
            }):
                with self.assertRaisesRegex(ValueError, "ãç"):
                    atlas.render_ptbr_atlas("missing.ttf", target)
            self.assertFalse(target.exists())


if __name__ == "__main__":
    unittest.main()

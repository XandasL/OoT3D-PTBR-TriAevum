"""Regression checks for the v1.3 full-translation/optional-HD contract.

Runs without a game image, graphics packs, or generated native font.
"""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parent
CORE = ROOT / "installer" / "text_translation.py"


def load_core():
    spec = importlib.util.spec_from_file_location("test_v13_text_translation", CORE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class V130TranslationContractTests(unittest.TestCase):
    def test_full_translation_includes_native_graphics_and_eur_mirrors(self):
        core = load_core()
        # Simulated verified payload: 112 sources and 126 RomFS destinations.
        translated = {"message/eu/eu.qm": b"mensagens PTBR"}
        translated.update({f"menu/01_us_english/item_{i}.ctxb": b"menu PTBR"
                           for i in range(14)})
        translated.update({f"menu/02_eu_english/item_{i}.ctxb": b"espelho PTBR"
                           for i in range(14)})
        translated["actor/link/face.ctxb"] = b"textura PTBR"
        for i in range(96):
            translated[f"scene/test_{i}.ctxb"] = b"textura PTBR"
        self.assertEqual(len(translated), 126)

        source_items = [{"source_rel": f"payload/{i}", "source": Path(f"payload/{i}")} for i in range(112)]
        patch_items = [{"target": name, "source_rel": name}
                       for name in translated]
        manifest = {x["source_rel"]: "validated" for x in source_items}
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "payload-manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
            with (patch.object(core, "HERE", root),
                  patch.object(core, "TRAD_ROOT", root),
                  patch.object(core, "sha256_file", return_value="validated"),
                  patch.object(core.parser, "collect_translation", return_value=source_items),
                  patch.object(core.parser, "collect_v4_items", return_value=patch_items),
                  patch.object(core.parser, "prepare_payload",
                               side_effect=lambda item: translated[item["target"]])):
                resources = core.prepared_resources(b"original font bytes")

        self.assertEqual(len(resources), 126)
        self.assertEqual(resources["message/eu/eu.qm"], b"mensagens PTBR")
        self.assertEqual(resources["actor/link/face.ctxb"], b"textura PTBR")
        self.assertEqual(resources["menu/02_eu_english/item_0.ctxb"], b"espelho PTBR")

    def test_only_hd64_is_offered_by_gui_and_generated_by_core(self):
        gui = (ROOT / 'installer/OoT3D_PTBR_TriAevum_v1.3.0.py').read_text(encoding='utf-8')
        core = CORE.read_text(encoding='utf-8')
        self.assertIn('text="Fonte HD 64"', gui)
        self.assertNotIn('text="Fonte HD 128"', gui)
        self.assertIn("'font_modes': ['original', 'hd64']", gui)
        self.assertIn("cell = 64", core)
        self.assertIn("half_a4_atlas", core)
        self.assertNotIn("make_font(native, 128)", core)

    def test_installer_does_not_manage_hd_texture_packs(self):
        code = CORE.read_text(encoding="utf-8")
        # The installer must not perform pack-copying or graphics-setting edits.
        for forbidden in ("LoadCustomTextures", "DumpTextures", "Azahar",
                          "pack.json", "hd_textures.install",
                          "prepare_local_text_only"):
            self.assertNotIn(forbidden, code)


if __name__ == "__main__":
    unittest.main()

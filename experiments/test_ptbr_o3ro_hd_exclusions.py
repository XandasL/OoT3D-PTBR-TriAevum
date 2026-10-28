"""Fail-closed coverage for the O3RO HD/menu/logo exclusion contract."""
import unittest
from pathlib import Path
from build_ptbr_o3ro_beta12 import EU_MIRRORS, HD_EXCLUDED_LOGOS, hd_exclusion_paths


class HdExclusionTests(unittest.TestCase):
    def sample(self):
        paths = {f"menu/{lang}/{filename}": Path("placeholder")
                 for lang in ("01_US_ENGLISH", "02_EU_ENGLISH")
                 for filename in EU_MIRRORS}
        paths.update({name: Path("placeholder") for name in HD_EXCLUDED_LOGOS})
        paths.update({f"misc/eu/english/{name}.ctxb": Path("placeholder")
                      for name in ("challenge00", "guideline_parts00",
                                   "hint_movie_parts01", "ura")})
        return paths

    def test_only_menu_and_logos_excluded(self):
        source = self.sample()
        excluded = hd_exclusion_paths(source)
        self.assertEqual(len(excluded), 31)
        self.assertEqual(len(source) - len(excluded), 4)
        self.assertTrue(all(name not in excluded for name in (
            "misc/eu/english/challenge00.ctxb",
            "misc/eu/english/guideline_parts00.ctxb",
            "misc/eu/english/hint_movie_parts01.ctxb",
            "misc/eu/english/ura.ctxb")))

    def test_missing_logo_fails_closed(self):
        source = self.sample()
        del source[HD_EXCLUDED_LOGOS[0]]
        with self.assertRaisesRegex(ValueError, "Missing expected"):
            hd_exclusion_paths(source)

    def test_unexpected_menu_ctxb_fails_closed(self):
        source = self.sample()
        source["menu/01_US_ENGLISH/unexpected.ctxb"] = Path("placeholder")
        with self.assertRaisesRegex(ValueError, "Unexpected menu"):
            hd_exclusion_paths(source)


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3

import unittest
import xml.etree.ElementTree as ET

import generate_header


class HeaderTests(unittest.TestCase):
    def test_every_variant_is_valid_svg_in_its_language(self) -> None:
        for theme in generate_header.THEMES:
            for lang, texts in generate_header.TEXTS.items():
                svg = generate_header.build_header(theme, lang)
                ET.fromstring(svg)
                self.assertIn("Yeray Lois Sanchez", svg)
                self.assertIn(texts["profile"], svg)
                self.assertIn("prefers-reduced-motion", svg)

    def test_tabs_use_the_language_accent(self) -> None:
        for (lang, theme), (background, _) in generate_header.TABS.items():
            svg = generate_header.build_tab(theme, lang)
            ET.fromstring(svg)
            self.assertIn(background, svg)
            self.assertIn(generate_header.TAB_LABELS[lang][1], svg)


if __name__ == "__main__":
    unittest.main()

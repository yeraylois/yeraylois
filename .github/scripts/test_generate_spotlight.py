#!/usr/bin/env python3
"""Regression tests for the editorial weekly-project spotlight."""

import unittest

import generate_spotlight


PROJECT = {
    "id": "sample",
    "name": "Embedded Sample",
    "description_es": "Muestra embebida para validación de hardware.",
    "description_en": "Embedded sample for hardware validation.",
    "tech": [
        {"id": "c", "label": "C"},
        {"id": "zephyr", "label": "Zephyr RTOS"},
    ],
    "repo": "https://github.com/yeraylois/sample",
}


class SpotlightTests(unittest.TestCase):
    def test_spotlight_is_editorial_instead_of_a_card(self) -> None:
        svg = generate_spotlight.build_svg(PROJECT, week=29, theme="dark", lang="es")
        self.assertNotIn("<rect", svg)
        self.assertNotIn("rx=", svg)
        self.assertNotIn("linearGradient", svg)
        self.assertIn("W29", svg)
        self.assertIn("SELECCIÓN ACTUAL", svg)

    def test_language_variants_use_their_own_copy(self) -> None:
        es_svg = generate_spotlight.build_svg(PROJECT, 29, "light", "es")
        en_svg = generate_spotlight.build_svg(PROJECT, 29, "light", "en")
        self.assertIn("Muestra embebida", es_svg)
        self.assertIn("ABRIR REPOSITORIO", es_svg)
        self.assertIn("Embedded sample", en_svg)
        self.assertIn("OPEN REPOSITORY", en_svg)

    def test_repo_url_is_shortened(self) -> None:
        self.assertEqual(
            "yeraylois/SE @ TraballoTutelado-2",
            generate_spotlight.short_repo(
                "https://github.com/yeraylois/SE/tree/TraballoTutelado-2"
            ),
        )


if __name__ == "__main__":
    unittest.main()

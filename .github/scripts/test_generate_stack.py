#!/usr/bin/env python3
"""Regression tests for the local stack icon catalog and renderer."""

import hashlib
import json
import unittest

import generate_stack


class StackIconTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.icons, cls.fallback = generate_stack.load_tech_icons()

    def test_catalog_is_complete_and_local(self) -> None:
        self.assertEqual(282, len(self.icons))
        self.assertEqual(282, len(set(self.icons.values())))
        for tech, configured_path in self.icons.items():
            with self.subTest(tech=tech):
                self.assertTrue(configured_path.startswith("./assets/icons/catalog/"))
                self.assertFalse(configured_path.startswith(("http://", "https://")))
                path = generate_stack.ROOT / configured_path.removeprefix("./")
                self.assertTrue(path.is_file(), path)

    def test_every_catalog_entry_is_a_standalone_svg(self) -> None:
        for tech, configured_path in self.icons.items():
            path = generate_stack.ROOT / configured_path.removeprefix("./")
            svg = path.read_text(encoding="utf-8")
            with self.subTest(tech=tech):
                self.assertIn("<svg", svg)
                self.assertFalse(generate_stack.is_badge_svg(svg))
                self.assertNotIn("textLength=", svg)

    def test_catalog_manifest_matches_files(self) -> None:
        manifest_path = generate_stack.ICONS_DIR / "sources.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(set(self.icons), set(manifest))
        generated_count = 0
        for tech, metadata in manifest.items():
            path = generate_stack.ROOT / metadata["file"].removeprefix("./")
            checksum = hashlib.sha256(path.read_bytes()).hexdigest()
            with self.subTest(tech=tech):
                self.assertEqual(metadata["sha256"], checksum)
            generated_count += metadata["resolution"] == "generated"
        self.assertLessEqual(generated_count, 11)

    def test_fallback_is_a_pictogram_without_text(self) -> None:
        icon = generate_stack.build_icon_element("Unknown Tech", 0, 0, 34, {})
        self.assertNotIn("<text", icon)
        self.assertIn("<path", icon)

    def test_mapped_icon_is_embedded_without_network_access(self) -> None:
        icon = generate_stack.get_icon_base64("Zephyr", self.icons)
        self.assertTrue(icon.startswith("data:image/svg+xml;base64,"))

    def test_remote_paths_are_refused(self) -> None:
        icon = generate_stack.get_icon_base64(
            "Unsafe", {"Unsafe": "https://img.shields.io/badge/unsafe-red"}
        )
        self.assertEqual("", icon)

    def test_stack_uses_editorial_rows_instead_of_a_card(self) -> None:
        svg = generate_stack.build_svg(
            ["Python"], ["C"], self.icons, theme="dark", lang="es"
        )
        self.assertNotIn("<rect", svg)
        self.assertNotIn("rx=", svg)
        self.assertNotIn("<animate", svg)
        self.assertIn("EN USO", svg)
        self.assertIn("BASE", svg)


if __name__ == "__main__":
    unittest.main()

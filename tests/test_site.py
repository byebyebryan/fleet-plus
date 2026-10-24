"""Publication guards: reject broken output and preserve an existing destination."""

import importlib.util
from pathlib import Path
import tempfile
import unittest

from markdown_it import MarkdownIt

spec = importlib.util.spec_from_file_location(
    "build", Path(__file__).resolve().parents[1] / "scripts/build.py"
)
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)


class PublicationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name) / "public"

    def test_build_and_source_link_mapping(self):
        result = build.build(self.output)
        self.assertEqual(result["pages"], 10)
        self.assertGreater(result["local_links"], 100)
        self.assertEqual(
            build.link_for_source("docs/start.md", "projects/agent-observer.md"),
            "/fleet-plus/projects/agent-observer/",
        )

    def test_existing_output_is_preserved(self):
        self.output.mkdir()
        marker = self.output / "keep.txt"
        marker.write_bytes(b"existing content")
        with self.assertRaisesRegex(ValueError, "empty"):
            build.build(self.output)
        self.assertEqual(marker.read_bytes(), b"existing content")

    def test_missing_anchor_is_rejected(self):
        build.build(self.output)
        page = self.output / "index.html"
        page.write_text(
            page.read_text().replace('href="#projects"', 'href="#missing-anchor"')
        )
        with self.assertRaisesRegex(ValueError, "anchor"):
            build.validate(self.output)

    def test_extra_public_file_is_rejected(self):
        build.build(self.output)
        (self.output / "private.txt").write_text("unexpected")
        with self.assertRaisesRegex(ValueError, "inventory"):
            build.validate(self.output)

    def test_changed_media_is_rejected(self):
        build.build(self.output)
        with (self.output / "assets/dashboard.png").open("ab") as stream:
            stream.write(b"changed")
        with self.assertRaisesRegex(ValueError, "hash mismatch"):
            build.validate(self.output)

    def test_source_markdown_has_static_media_and_all_read_cases(self):
        observer = (build.ROOT / "docs/projects/agent-observer.md").read_text()
        architecture = (build.ROOT / "docs/architecture.md").read_text()
        agent = (build.ROOT / "docs/projects/agent-plus.md").read_text()
        rendered = (
            MarkdownIt("commonmark", {"html": True}).enable("table").render(observer)
        )
        self.assertIn('src="../../assets/dashboard.png"', rendered)
        self.assertIn("Partial or expired evidence", rendered)
        self.assertIn("Optional fleet delivery", rendered)
        self.assertIn("Tower → Laptop", MarkdownIt().render(architecture))
        self.assertIn('src="../../assets/agent-plus.png"', MarkdownIt().render(agent))
        for text in (observer, architecture, agent):
            self.assertNotIn("{{", text)

    def test_invalid_enhancements_fail_instead_of_hiding_broken_markdown(self):
        cases = [
            ("<!-- fleet-plus:routes -->\nText", "unmatched"),
            (
                "<!-- fleet-plus:unknown -->\nText\n<!-- /fleet-plus:unknown -->",
                "unknown",
            ),
            ("<!-- fleet-plus:routes -->\n\n<!-- /fleet-plus:routes -->", "empty"),
            ("{{DASHBOARD}}", "template tokens"),
            (
                "<!-- fleet-plus:routes -->\n[broken](missing.md)\n<!-- /fleet-plus:routes -->",
                "unregistered",
            ),
        ]
        for text, reason in cases:
            with self.subTest(reason=reason):
                with self.assertRaisesRegex(ValueError, reason):
                    build.prepare_enhancements(text, "docs/architecture.md")

    def test_duplicate_enhancements_cannot_create_duplicate_control_ids(self):
        block = "<!-- fleet-plus:routes -->\nPlain text fallback\n<!-- /fleet-plus:routes -->"
        with self.assertRaisesRegex(ValueError, "duplicate"):
            build.prepare_enhancements(block + "\n\n" + block, "docs/architecture.md")


if __name__ == "__main__":
    unittest.main()

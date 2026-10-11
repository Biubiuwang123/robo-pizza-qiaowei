"""Site checks: run after any edit, before any deploy.

    python3 -m unittest discover tests

They build the site into a temp folder and check what a visitor would get:
every marker filled in, every page framed, every local link resolving, and
every element a scene's script reaches for actually present on its page.
"""
import json
import re
import shutil
import sys
import tempfile
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_site  # noqa: E402

# Ids scene-kit.js itself needs on every scene page.
KIT_IDS = {"mvp", "mvpDone", "mvpPill"}


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.links, self.scripts, self.checklist = set(), [], [], set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            self.ids.add(a["id"])
        if "data-k" in a:
            self.checklist.add(a["data-k"])
        for key in ("href", "src"):
            if a.get(key):
                self.links.append(a[key])
        if tag == "script" and a.get("src"):
            self.scripts.append(a["src"])


def parse(path):
    p = PageParser()
    p.feed(path.read_text())
    return p


class BuiltSiteTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = Path(tempfile.mkdtemp())
        cls.dist = cls.tmp / "dist"
        cls.pages = build_site.build(cls.dist)

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp)

    def test_every_marker_is_filled(self):
        for page in self.pages:
            text = page.read_text()
            self.assertNotIn("<!-- @", text, page.name)
            self.assertNotIn("{{root}}", text, page.name)

    def test_every_page_has_header_footer_and_disclaimer(self):
        for page in self.pages:
            text = page.read_text()
            self.assertIn('class="site-header"', text, page.name)
            self.assertIn('class="site-footer"', text, page.name)
            self.assertIn("public sources only", text, page.name)
            self.assertRegex(text, r"<title>[^<]+</title>", page.name)

    def test_local_links_resolve(self):
        for page in self.pages:
            for link in parse(page).links:
                if re.match(r"^(https?:|mailto:|#)", link):
                    continue
                target = (page.parent / link.split("#")[0]).resolve()
                if link.split("#")[0] in ("", "./", "../"):
                    target = target / "index.html" if target.is_dir() else target
                elif target.is_dir():
                    target = target / "index.html"
                self.assertTrue(target.exists(), f"{page.relative_to(self.dist)} links to missing {link}")

    def test_scene_scripts_find_their_elements(self):
        for page in self.dist.glob("scenes/*.html"):
            info = parse(page)
            self.assertIn("scene-kit.js", info.scripts, f"{page.name} must load scene-kit.js")
            self.assertLess(info.scripts.index("scene-kit.js"), len(info.scripts) - 1,
                            f"{page.name} must load scene-kit.js before its own script")
            self.assertTrue(KIT_IDS <= info.ids, f"{page.name} is missing {KIT_IDS - info.ids}")
            for src in info.scripts:
                if src == "scene-kit.js":
                    continue
                js = (page.parent / src).read_text()
                wanted = set(re.findall(r'\$\("([\w-]+)"\)', js))
                wanted |= set(re.findall(r'getElementById\("([\w-]+)"\)', js))
                missing = wanted - info.ids
                self.assertFalse(missing, f"{src} reaches for ids not on {page.name}: {missing}")
                ticks = set(re.findall(r'tick\("([\w-]+)"\)', js))
                self.assertFalse(ticks - info.checklist,
                                 f"{src} ticks checklist items not on {page.name}: {ticks - info.checklist}")
                locked = re.search(r"locked:\s*\[([^\]]*)\]", js)
                if locked:
                    acts = set(re.findall(r'"([\w-]+)"', locked.group(1)))
                    self.assertFalse(acts - info.ids, f"{src} locks acts not on {page.name}: {acts - info.ids}")

    def test_scene_list_matches_scene_pages(self):
        data = json.loads((ROOT / "site" / "scenes" / "scenes.json").read_text())
        index = (self.dist / "index.html").read_text()
        for sc in data["scenes"]:
            self.assertIn(sc["title"].replace("'", "&#x27;"), index)
            if sc["status"] == "live":
                self.assertTrue((self.dist / "scenes" / sc["page"]).exists(), sc["page"])

    def test_build_rejects_mistakes(self):
        page = ROOT / "site" / "_probe.html"
        try:
            page.write_text("<!-- @replay does-not-exist -->")
            with self.assertRaises(build_site.BuildError):
                build_site.build(self.tmp / "probe")
        finally:
            page.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()

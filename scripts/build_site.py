"""Build the static site: site/ (sources) -> dist/ (what gets deployed).

Pages stay plain HTML. The build only fills in a few markers, so shared pieces
live in exactly one place:

    <!-- @include header -->         site/_partials/header.html (also footer, scene-nav)
    <!-- @scenes -->                 the landing page's scene list, from site/scenes/scenes.json
    <!-- @replay locked-box -->      replays/locked-box.txt, escaped, inside <pre><code>

{{root}} inside a partial becomes the relative path back to the site root
("./" on the landing page, "../" inside scenes/), so partials work at any depth.

    python3 scripts/build_site.py          # build into dist/
    python3 scripts/build_site.py --check  # build into a temp dir, report problems only

The build fails (exit 1) on an unknown marker, a missing replay, a missing
partial, or a "live" scene whose page does not exist, so mistakes never deploy.
"""
import html
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "site"
DIST = ROOT / "dist"
REPLAYS = ROOT / "replays"
PARTIALS = SRC / "_partials"
SKIP = {"_partials", "README.md", ".DS_Store", "scenes.json"}

MARKER = re.compile(r"<!-- @(\w[\w-]*)(?: ([\w-]+))? -->")


class BuildError(Exception):
    pass


def root_prefix(page: Path) -> str:
    depth = len(page.relative_to(SRC).parts) - 1
    return "./" if depth == 0 else "../" * depth


def render_replay(name: str) -> str:
    path = REPLAYS / f"{name}.txt"
    if not path.exists():
        raise BuildError(f"replay '{name}' not found at replays/{name}.txt")
    out = []
    for line in path.read_text().rstrip("\n").splitlines():
        text = html.escape(line)
        if line.startswith("$ "):
            text = '<span class="prompt">$</span>' + text[1:]
        elif line.startswith("# "):
            text = f'<span class="comment">{text}</span>'
        out.append(text)
    return "\n".join(out)


def render_scenes(root: str) -> str:
    data = json.loads((SRC / "scenes" / "scenes.json").read_text())
    items = []
    for num, sc in enumerate(data["scenes"], 1):
        href = f"{root}scenes/{sc['page']}"
        live = sc["status"] == "live"
        if live and not (SRC / "scenes" / sc["page"]).exists():
            raise BuildError(f"scene '{sc['title']}' is live but scenes/{sc['page']} does not exist")
        title = f'<a href="{href}">{html.escape(sc["title"])}</a>' if live else html.escape(sc["title"])
        status = (f'<a class="status live" href="{href}">Play &rarr;</a>' if live
                  else '<span class="status">Coming soon</span>')
        items.append(f'''          <li class="chapter">
            <span class="num">{num}</span>
            <div>
              <h3>{title}</h3>
              <p class="plain">{html.escape(sc["subtitle"])}</p>
              <p>{html.escape(sc["play"])}</p>
              <p class="aws-name">On AWS: {html.escape(sc["aws"])}</p>
            </div>
            {status}
          </li>''')
    return "\n".join(items).lstrip()


def render_page(page: Path) -> str:
    root = root_prefix(page)

    def replace(m):
        kind, arg = m.group(1), m.group(2)
        if kind == "include":
            part = PARTIALS / f"{arg}.html"
            if not part.exists():
                raise BuildError(f"{page.name}: partial '{arg}' not found")
            return part.read_text().rstrip("\n").replace("{{root}}", root).lstrip()
        if kind == "scenes":
            return render_scenes(root)
        if kind == "replay":
            return render_replay(arg)
        raise BuildError(f"{page.name}: unknown marker @{kind}")

    return MARKER.sub(replace, page.read_text())


def build(dest: Path) -> list:
    if dest.exists():
        shutil.rmtree(dest)
    pages = []
    for src in sorted(SRC.rglob("*")):
        rel = src.relative_to(SRC)
        if any(part in SKIP for part in rel.parts) or src.is_dir():
            continue
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        if src.suffix == ".html":
            out.write_text(render_page(src))
            pages.append(out)
        else:
            shutil.copy2(src, out)
    return pages


def main():
    check_only = "--check" in sys.argv
    dest = Path(tempfile.mkdtemp()) / "dist" if check_only else DIST
    try:
        pages = build(dest)
    except BuildError as err:
        sys.exit(f"build failed: {err}")
    print(f"built {len(pages)} pages into {'a temp dir' if check_only else dest.relative_to(ROOT)}")
    if check_only:
        shutil.rmtree(dest.parent)


if __name__ == "__main__":
    main()

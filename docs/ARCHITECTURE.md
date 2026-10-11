# How the site is put together

Plain HTML, CSS and JavaScript. No framework, no npm. A ~150-line Python build
fills in a few shared pieces so that each concept lives in exactly one file.

```
site/                       sources (edit these)
  index.html                landing page
  styles.css                design tokens (colors, light/dark) + site-wide styles
  _partials/                header, footer, scene-nav: shared by every page
  scenes/
    scenes.json             the landing page's scene list (title, blurb, status)
    scene-kit.js            shared scene engine: checklist, progress pill, act locking
    scene.css               shared scene styles: layout, acts, buttons, checklist
    <scene>.html            one page per scene
    <scene>.js              that scene's interactions only
    <scene>.css             that scene's styles only
replays/<name>.txt          real lab transcripts, inserted into pages at build time
lab/                        scripts that produce the replays (openssl, AWS)
scripts/build_site.py       site/ + replays/ -> dist/
scripts/preview.sh          build, then serve dist/ at http://127.0.0.1:8765
scripts/deploy_site.py      build, then upload dist/ to S3 + CloudFront
tests/                      leak check + site checks; run before every deploy
```

## Markers the build fills in

| In a page | Becomes |
|---|---|
| `<!-- @include header -->` | `site/_partials/header.html` (also `footer`, `scene-nav`) |
| `<!-- @scenes -->` | the scene list, from `site/scenes/scenes.json` |
| `<!-- @replay locked-box -->` | `replays/locked-box.txt`, escaped; `$ ` lines get a prompt, `# ` lines are dimmed |

`{{root}}` in a partial becomes the path back to the site root, so links work at any depth.
The build stops on an unknown marker, a missing partial or replay, or a "live" scene
with no page, so a mistake can't reach the live site.

## Common changes

| To change | Edit | Touches nothing else because |
|---|---|---|
| Footer or header text | `site/_partials/*.html` | every page includes the same file |
| A scene's wording or interactions | `site/scenes/<scene>.html` / `.js` | each scene's script only reads its own page |
| A scene's look | `site/scenes/<scene>.css` | loaded only by that scene |
| Checklist or locking behavior for all scenes | `site/scenes/scene-kit.js` | one engine, used by every scene |
| Colors / dark mode | `:root` tokens in `site/styles.css` | every stylesheet uses the tokens |
| The landing page's scene list | `site/scenes/scenes.json` | rendered at build time |
| A "see the real one" transcript | re-run the lab script with `--save` | the page pulls the file at build time |

## Adding a scene

1. Copy an existing scene's `.html`, `.js`, `.css` to `site/scenes/<new>.*`.
2. In the `.html`: keep the `@include` markers, `#mvp` checklist (`<li data-k="...">`),
   `#mvpDone`, `#mvpPill`, and load `scene-kit.js` before the scene's own script.
3. In the `.js`: `const { $, tick, unlock } = SceneKit.start({ pillLabel, locked: [...] })`.
4. Add it to `scenes.json` with `"status": "live"`.
5. `python3 -m unittest discover tests`, then `sh scripts/preview.sh` to play it.

## What the tests catch

- Any marker left unfilled, any page missing its header, footer or disclaimer.
- Any local link or asset that doesn't exist.
- A scene script reaching for an element id, checklist item, or act that isn't on its page.
- A live scene in `scenes.json` with no page.
- Secrets, account IDs, ARNs, emails, IPs, or private terms anywhere in the repo.

# site/

The static website: plain HTML, CSS and a little JavaScript, one page per chapter.
No server, no build step, no third-party fonts or scripts.

Preview locally:

```bash
python3 -m http.server 8765 --bind 127.0.0.1 --directory site
```

Then open http://127.0.0.1:8765.

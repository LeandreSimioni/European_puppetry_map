#!/usr/bin/env python3
"""Repackages dist/index.html as dist/artifact.html for publishing as a
Claude artifact.

An artifact host wraps the file it is given in its own <!doctype>/<head>/<body>
skeleton, so it needs the page body, not a whole document. This script lifts the
<style> and the body out of the built map and prepends a background guard, since
the host's own reset sets a light background that would otherwise show through
the booth interior.

Usage:
    python3 build.py && python3 tools/make_artifact.py
"""
import pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'dist' / 'index.html'
OUT = ROOT / 'dist' / 'artifact.html'

TITLE = 'The Europe of Puppet Booths'

# The map is a night-lit theatre interior: a deliberate single-theme design.
# The guard pins the ground so a host rendering in light theme cannot bleed
# through.
GUARD = """<style>
  html, body { background: #171025 !important; color-scheme: dark; }
</style>
"""

if not SRC.exists():
    sys.exit('dist/index.html missing, run python3 build.py first')

html = SRC.read_text()
style = re.search(r'<style>.*?</style>', html, re.S)
body = re.search(r'<body>(.*)</body>', html, re.S)
if not style or not body:
    sys.exit('unexpected structure in dist/index.html')

OUT.write_text(f'<title>{TITLE}</title>\n{style.group(0)}\n{GUARD}{body.group(1).strip()}\n')
print(f'wrote {OUT} ({OUT.stat().st_size // 1024} kB)')

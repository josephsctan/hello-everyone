"""Build hello-everyone.html from hello-everyone.src.html + langs.json.

Downloads each greeting's audio from Google Translate's text-to-speech endpoint
into audio/ (skipped if already present), then embeds the mp3s as base64 so the
output is a single self-contained file.

Usage: python build.py
"""
import base64
import json
import pathlib
import time
import unicodedata
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).parent
AUDIO_DIR = ROOT / "audio"
AUDIO_DIR.mkdir(exist_ok=True)
langs = json.loads((ROOT / "langs.json").read_text(encoding="utf-8"))
# The menu is alphabetical by name, ignoring accents (so Māori sorts under M).
langs.sort(key=lambda l: unicodedata.normalize("NFKD", l["name"]).encode("ascii", "ignore").decode().lower())


def fetch(tts, text, dest):
    qs = urllib.parse.urlencode({"ie": "UTF-8", "client": "tw-ob", "tl": tts, "q": text})
    req = urllib.request.Request(
        "https://translate.google.com/translate_tts?" + qs,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        data = r.read()
    if len(data) < 1000:
        raise RuntimeError(f"suspiciously small audio for {text!r}: {len(data)} bytes")
    dest.write_bytes(data)


audio = {}
for l in langs:
    for i, it in enumerate(l["items"]):
        key = f'{l["id"]}:{i}'
        f = AUDIO_DIR / f'{l["id"]}_{i}.mp3'
        if not f.exists():
            if not l["tts"]:
                print("no audio for", f.name, "(language not supported by Google TTS; drop an mp3 in audio/ to add one)")
                continue
            fetch(l["tts"], it["t"], f)
            print("downloaded", f.name)
            time.sleep(0.5)
        audio[key] = base64.b64encode(f.read_bytes()).decode("ascii")

html = (ROOT / "hello-everyone.src.html").read_text(encoding="utf-8")


def swap(html, marker, body):
    a = html.index(f"/*{marker}*/")
    b = html.index(f"/*END {marker}*/")
    return html[:a] + f"/*{marker}*/\n  " + body + "\n  " + html[b:]


html = swap(html, "LANGS", "var LANGS = " + json.dumps(langs, ensure_ascii=False, indent=1) + ";")
html = swap(html, "AUDIO", "var AUDIO = " + json.dumps(audio) + ";")
out = ROOT / "hello-everyone.html"
out.write_text(html, encoding="utf-8")
print(f"wrote {out.name}: {out.stat().st_size // 1024} KB, {len(audio)} clips")

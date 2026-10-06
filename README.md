# Hello, everyone

A study page for greeting a room of people in many languages: native script, romanization, a respelling, the meaning, and a recorded clip for each greeting.

- `hello-everyone.html` is the built, self-contained page (audio embedded as base64).
- `hello-everyone.src.html` is the page template and `langs.json` holds the greetings. Edit these, not the built file.
- `build.py` downloads any missing clips into `audio/` (Google Translate text-to-speech) and writes `hello-everyone.html`: `python build.py`.

Māori and Samoan have no clips because Google's text-to-speech doesn't support them. Save recordings as `audio/<id>_<n>.mp3` and rebuild to add them.

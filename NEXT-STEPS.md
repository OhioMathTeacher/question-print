# Question Print — next steps

Repo: `~/Repos/question-print` (public, GitHub Pages **not yet enabled**: Todd turns
it on at Settings → Pages → branch master, folder /). Until then:
`python3 -m http.server 8080` in the repo and open http://localhost:8080 in Firefox.

## What exists (13 Sept 2026)

One file, `index.html`. Five steps: record or drop audio → transcribe in the browser
(Whisper via Transformers.js, module worker, ≤12 min) → tap T/S per line, edit words,
toggle questions → tag each teacher question DOK × Bloom on Hess's Cognitive Rigor
Matrix (descriptor shown; five impossible cells refused) → see it (stats, strip,
matrix with your counts and the machine's, Table-3 transcript). The machine's turn:
copy-prompt/paste-back (no key), or a Gemini / Groq / Claude key kept in the browser.
"Move it up a level" per question. "Setup, not mathematics" label excludes
profiler-type questions from the profile. Second drop zone takes a **Verbatim session
JSON** (or a saved Question Print JSON) and skips to tagging. Print/JSON/copy export.
localStorage resume.

`tools/tag-sessions.py SESSIONS OUT` tags a folder of sessions offline with `claude -p`
(math/setup label, one droppable `*.qp.json` per session, `summary.md`). Ran over the
11 recovered Taylor sessions → `TEA-Taylor-DATA/Analysis/question-print/`.

**Never tested in a real browser.** Only syntax-checked. First real run = the cold test.

## Next

1. Enable Pages; open it in Firefox; drop a short audio file; watch the Whisper worker
   load and time a real 10-minute transcription on a student-class laptop.
2. Fix whatever that breaks (likely: worker/CDN loading, timestamps on long chunks,
   the sentence splitter over-counting list fragments as questions — seen in the
   Taylor run: ~27 of 61 DOK-1 "questions" were fragments like "Degree?").
3. Cold test by a human (Todd or the GA) before any 318P student sees it.
4. 318P home: an **option** in the Week 6 Concept Profile (one of the 2–3 pieces may
   be a transcript of the student working with a focus student, recorded on their own
   device, pseudonyms, never the audio). Field dip is Sept 28 – Oct 1, so ready by ~Sept 25.
   Design note: `fall-2026/TCE-318P/design/question-print-idea.md`.
5. For the Taylor chapter: it is the AI-question coder (see
   `TEA-Taylor-MANUSCRIPT/Fall-2026/design/NEXT-STEPS.md`).

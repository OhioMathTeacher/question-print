# Question Print — next steps

Repo: `~/Repos/question-print` (public). Live at
<https://ohiomathteacher.github.io/question-print/> (Pages enabled 14 Sept, branch
master, folder /). Locally: `python3 -m http.server 8080` in the repo.

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

**First real run, 14 Sept (headless Chromium, driven by DevTools).** Todd's drop of
a Wikimedia *page* saved as `.ogg` did nothing, silently: now a drop the decoder
refuses says what it was (web page / PDF / undecodable) in a toast. With the real
recording (`fall-2026/audio/kwik-e-mart-security-guard.ogg`, 45 s Vorbis): loads at
0:45 with a waveform; Transcribe loaded whisper-tiny.en from the CDN and produced 7
lines in ~9 s, questions flagged, speakers guessed. Found and fixed on that run: the
progress handler read `#tmeter.firstElementChild` (the `<i>` *is* `#tmeter`), so every
model-download message threw and the meter never moved. Still untested by a person, and
untested in Firefox.

**Splitter fixed (14 Sept).** One `splitSentences` in `index.html` (both the Whisper
and the Verbatim paths) mirrored by `split_sentences` in `tools/tag-sessions.py`:
decimals, list markers and math (`$…$`, `\(…\)`) no longer end a sentence; a fragment
with no letters joins the sentence before it; a run of one-word alternatives after a
question ("Finance? Engineering?") is one question; bullet markers and emphasis come
off. Over the 11 Taylor sessions: 291 → 272 AI questions, and the broken-math ones
(`0001?`, `} \)?`) are gone. The `.qp.json` files in TEA-Taylor-DATA were tagged with
the old splitter; re-run `tag-sessions.py` before the chapter quotes those counts.

## Next

1. Open the live page in Firefox; drop a short audio file; watch the Whisper worker
   load and time a real 10-minute transcription on a student-class laptop.
2. Fix whatever that breaks (likely: worker/CDN loading, timestamps on long chunks).
3. Cold test by a human (Todd or the GA) before any 318P student sees it.
4. 318P home: an **option** in the Week 6 Concept Profile (one of the 2–3 pieces may
   be a transcript of the student working with a focus student, recorded on their own
   device, pseudonyms, never the audio). Field dip is Sept 28 – Oct 1, so ready by ~Sept 25.
   Design note: `fall-2026/TCE-318P/design/question-print-idea.md`.
5. For the Taylor chapter: it is the AI-question coder (see
   `TEA-Taylor-MANUSCRIPT/Fall-2026/design/NEXT-STEPS.md`).

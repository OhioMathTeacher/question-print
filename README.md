# Question Print

**[Open it →](https://ohiomathteacher.github.io/question-print/)**

Record five to ten minutes of mathematics talk. Transcribe it on your own
computer. Tag every question you asked by Webb's Depth of Knowledge and
revised Bloom's, on Hess's Cognitive Rigor Matrix. See the shape of your
questioning: a strip through the lesson, the matrix with your counts, and
the transcript tagged the way the Week 4 article's Table 3 is.

Nothing is uploaded. The recording stays in the browser and is never stored.
The transcript and the tags are what you keep, as a PDF and a JSON.

## The five steps

1. **Record** here (the device's microphone) or drop an audio file. Play
   the start; if you can make out the words, the transcriber can.
2. **Transcribe.** Whisper runs in the browser (Transformers.js). The model
   downloads once and is kept. A ten-minute recording takes a few minutes.
3. **Who spoke.** Tap T or S on each line, fix any words, toggle which
   lines are questions. Only the teacher's questions get tagged.
4. **Tag.** You first: DOK 1–4 and Bloom 1–6 for each question, with the
   matrix cell's descriptor shown. The five combinations that don't exist
   are shaded and refused. Then the machine's turn: copy a prompt and paste
   the reply back (no key), or use your own Gemini / Groq / Claude key.
   Where you and the machine disagree, that's the interesting part.
   "Move it up a level" re-asks a question toward the next cell.
5. **See it.** Mean DOK, share at DOK 1, agreement with the machine; the
   strip; the matrix; the tagged transcript. Print to PDF for Canvas.

Work in progress is kept in the browser (localStorage), so a closed tab
doesn't lose the tags. "Start over" clears it.

## For TCE 318P

An option for the Week 6 Concept Profile: one of the two or three pieces of
student work may be a transcript of *you* working with a focus student on
your concept, recorded on your own device and tagged here. Attach the
transcript with pseudonyms, never the audio. It's the same method as the
Week 4 reading, applied to yourself.

Matrix adapted from Hess, K. K., Jones, B. S., Carlock, D., & Walkup, J. R.
(2009). *Cognitive rigor: Blending the strengths of Bloom's Taxonomy and
Webb's Depth of Knowledge to enhance classroom-level processes.*

## Running it

One file. Open `index.html` from a local server (the transcriber loads a
module worker, which `file://` blocks in some browsers):

    python3 -m http.server 8080

Tested in Firefox. Needs a browser with WebAssembly and module workers.

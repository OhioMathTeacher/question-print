#!/usr/bin/env python3
"""Tag every AI question in a folder of session files on the Cognitive Rigor Matrix, offline.

    tools/tag-sessions.py SESSIONS_DIR OUT_DIR [--model claude-sonnet-5]

Reads Verbatim exports (tea-taylor-session/*) or the recovered-corpus shape (turns with
role + text). Extracts questions the way index.html's loadJson does, sends each session's
questions to `claude -p` with the app's own prompt, and writes one Question Print JSON per
session (droppable into the app) plus summary.md across the corpus. The machine's tags are
put in both `ai` and `dok`/`bloom` so the matrix renders; `source.tagged_by` says so.
"""
import json, re, subprocess, sys, os, collections, statistics
from pathlib import Path

BLOOM = ["Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"]
DOK = ["Recall & Reproduction", "Basic Skills & Concepts", "Strategic Thinking & Reasoning", "Extended Thinking"]
CRM = {
    1: ["Recall, recognize, and locate basic facts, ideas, and principles", None, None, None],
    2: ["Describe or explain how (the steps of a specified algorithm)", "Specify and explain relationships (why a specified algorithm is reasonable)", "Explain strategies and reasoning for solving tasks where the procedure has not been specified", "Explain how concepts or ideas relate to other content domains or concepts"],
    3: ["Apply an algorithm or formula", "Solve routine problems applying multiple concepts or decision points", "Use concepts to solve nonroutine problems", "Select or devise an approach among many alternatives to solve a novel problem"],
    4: ["Retrieve information from a table or graph to answer a question", "Compare and contrast figures or data", "Generalize a pattern", "Gather, analyze, and organize information"],
    5: [None, None, "Verify reasonableness of results", "Draw and justify conclusions"],
    6: ["Brainstorm ideas, concepts, or perspectives related to a topic", "Generate conjectures or hypotheses based on observations or prior knowledge", "Formulate an original problem", "Design a model to inform and solve real-world, complex, or abstract situations"],
}
CLAUDE = os.environ.get("CLAUDE_CODE_EXECPATH") or "claude"
SENT = re.compile(r"[^.?!]+[.?!]+[\"')\]]?|[^.?!]+$")
MATH = re.compile(r"\$\$.*?\$\$|\$[^$\n]+\$|\\\(.*?\\\)|\\\[.*?\\\]", re.S)


def split_sentences(text):
    """Same rule as splitSentences in index.html: decimals, list markers and math do not end a
    sentence; a fragment with no letters joins the sentence before it; a run of one- or two-word
    alternatives after a question is one question. Bullet markers and emphasis come off."""
    keep = []
    def mask(m):
        keep.append(m.group(0)); return f"\x00{len(keep)-1}\x00"
    masked = MATH.sub(mask, text)
    masked = re.sub(r"(\d)\.(?=\d)", "\\1\x01", masked)
    masked = re.sub(r"^(\s*(?:\d+|[a-z]))\.(?=\s)", "\\1\x01", masked, count=1, flags=re.I)
    parts = []
    for raw in SENT.findall(masked) or [masked]:
        p = raw.replace("\x01", ".")
        p = re.sub(r"\x00(\d+)\x00", lambda m: keep[int(m.group(1))], p).strip()
        p = re.sub(r"^(?:[*\-•·]\s+)+", "", p)
        p = re.sub(r"^\*+|\*+$", "", p).strip()
        if not p:
            continue
        prev = parts[-1] if parts else None
        words = len(re.findall(r"[^\W\d_][^\W\d_'’]*", p))
        no_letters = not re.search(r"[^\W\d_]", p)
        short_alt = p.endswith("?") and prev is not None and prev.endswith("?") and (
            words <= 1 or words == 2 and not re.match(r"(what|why|how|which|where|when|who)\b", p, re.I))
        if prev is not None and (no_letters or short_alt):
            parts[-1] = prev + " " + p
        else:
            parts.append(p)
    return parts


def lines_from(j):
    turns = j.get("turns") or j.get("conversation") or []
    out = []
    for t in turns:
        text = (t.get("text") or "").strip()
        if not text:
            continue
        who = "T" if t.get("role") in ("ai", "assistant", "T") else "S"
        for par in re.split(r"\n+", text):
            for q in split_sentences(par):
                if q:
                    out.append({"t0": 0, "t1": 0, "text": q, "who": who, "q": who == "T" and bool(re.search(r"\?\s*$", q)) and len(q) < 400,
                                "dok": 0, "bloom": 0, "ai": None, "turn": t.get("i")})
    return turns, out


def matrix_text():
    return "\n".join(f"Bloom {b} ({BLOOM[b-1]}): " + " | ".join(f"DOK {d+1}: {t or '(no such combination)'}" for d, t in enumerate(row)) for b, row in CRM.items())


def prompt_for(qs):
    frame = ("I am a pre-service mathematics teacher learning Hess's Cognitive Rigor Matrix: Webb's Depth of Knowledge (DOK 1 recall and reproduction; "
             "DOK 2 basic skills and concepts; DOK 3 strategic thinking and reasoning; DOK 4 extended thinking) crossed with revised Bloom's "
             "(1 Remember, 2 Understand, 3 Apply, 4 Analyze, 5 Evaluate, 6 Create). Judge by what the student would actually have to do to answer, "
             "not by the verb. Five combinations do not exist: Remember at DOK 2, 3, or 4, and Evaluate at DOK 1 or 2.\n\nThe matrix cells:\n" + matrix_text() + "\n")
    return frame + ("\nBelow are questions an AI tutor asked a student in a typed calculus session. Some are about the mathematics "
                    "(Taylor series, approximation); some are setup: the tutor asking about the student's preferences, feelings, or how to run "
                    "the session. Tag each one, and say which kind it is.\n"
                    "Reply with exactly one line per question, in this form and nothing else:\nQ1: DOK 2, Bloom 3, math — one short reason\n"
                    "(the fourth field is  math  or  setup)\n\nThe questions:\n"
                    + "\n".join(f"Q{n+1}: {l['text']}" for n, l in enumerate(qs)))


TAG = re.compile(r"Q\s*(\d+)\s*[:.)-]\s*DOK[\s-]*(\d)\s*[,;]?\s*Bloom(?:'s)?[\s-]*(\d)\s*[,;]?\s*(math|setup)?\s*(?:[—–:-]\s*(.*))?", re.I)


def tag(qs, model):
    if not qs:
        return 0
    r = subprocess.run([CLAUDE, "-p", "--model", model, "--output-format", "text"], input=prompt_for(qs), capture_output=True, text=True, timeout=900)
    n = 0
    for m in TAG.finditer(r.stdout):
        i = int(m.group(1)) - 1
        if 0 <= i < len(qs):
            d, b = int(m.group(2)), int(m.group(3))
            if 1 <= d <= 4 and 1 <= b <= 6 and CRM[b][d-1]:
                qs[i]["ai"] = {"dok": d, "bloom": b, "kind": (m.group(4) or "math").lower(), "why": (m.group(5) or "").strip()}
                qs[i]["dok"], qs[i]["bloom"] = d, b
                n += 1
    return n


def main():
    src, out = Path(sys.argv[1]), Path(sys.argv[2])
    model = sys.argv[sys.argv.index("--model") + 1] if "--model" in sys.argv else "claude-sonnet-5"
    out.mkdir(parents=True, exist_ok=True)
    corpus = []
    for f in sorted(src.glob("*.json")):
        j = json.loads(f.read_text())
        turns, lines = lines_from(j)
        qs = [l for l in lines if l["q"]]
        n = tag(qs, model)
        name = f.stem
        qp = {"app": "question-print", "name": name, "duration": 0, "model": "",
              "source": {"schema": j.get("schema") or j.get("method"), "participant": j.get("participant"), "group": j.get("group"), "section": j.get("section"),
                         "provider": j.get("provider"), "model": j.get("model"), "tagged_by": f"{model} (machine); no human tags yet"},
              "lines": lines}
        (out / f"{name}.qp.json").write_text(json.dumps(qp, indent=1))
        corpus.append((name, len(turns), qs))
        print(f"{name:14} {len(turns):4} turns  {len(qs):3} AI questions  {n:3} tagged", flush=True)
    summary(corpus, out, model)


def summary(corpus, out, model):
    every = [q for _, _, qs in corpus for q in qs if q["ai"]]
    setup = [q for q in every if q["ai"].get("kind") == "setup"]
    allq = [q for q in every if q["ai"].get("kind") != "setup"]   # the profile is of the mathematics questions
    grid = collections.Counter((q["bloom"], q["dok"]) for q in allq)
    doks = collections.Counter(q["dok"] for q in allq)
    L = [f"# The AI's questioning, on the Cognitive Rigor Matrix", "",
         f"{len(corpus)} sessions (the recovered earlier corpus), {sum(len(qs) for _,_,qs in corpus)} questions the AI asked, {len(every)} tagged by {model}: "
         f"{len(setup)} were setup (the profiler asking about preferences, or how to run the session) and are left out below; **{len(allq)} were about the mathematics**, and those are the profile. "
         "Machine tags only; no human coder has touched these yet, and the corpus is the one with the speaker-recovery caveat. Read it as a first profile, not a finding.", "",
         "## Depth of Knowledge, all sessions", "",
         "| DOK | math questions | share |", "|---|---|---|"]
    for d in range(1, 5):
        L.append(f"| DOK {d} · {DOK[d-1]} | {doks[d]} | {100*doks[d]/max(1,len(allq)):.0f}% |")
    L += ["", f"Mean DOK {statistics.mean(q['dok'] for q in allq):.2f}." if allq else "", "",
          "## The matrix (counts)", "", "| | DOK 1 | DOK 2 | DOK 3 | DOK 4 |", "|---|---|---|---|---|"]
    for b in range(1, 7):
        L.append(f"| {BLOOM[b-1]} | " + " | ".join("·" if CRM[b][d-1] is None else str(grid[(b, d)] or "") for d in range(1, 5)) + " |")
    L += ["", "## Per session", "", "| session | AI questions | mean DOK | DOK 1 | DOK 3+ | first half → second half |", "|---|---|---|---|---|---|"]
    for name, nt, qs in corpus:
        t = [q for q in qs if q["ai"] and q["ai"].get("kind") != "setup"]
        if not t:
            L.append(f"| {name} | {len(qs)} | – | | | |"); continue
        h = len(t) // 2 or 1
        a, b = statistics.mean(q["dok"] for q in t[:h]), statistics.mean(q["dok"] for q in t[h:] or t[:h])
        L.append(f"| {name} | {len(t)} | {statistics.mean(q['dok'] for q in t):.2f} | {sum(q['dok']==1 for q in t)} | {sum(q['dok']>=3 for q in t)} | {a:.2f} → {b:.2f} |")
    L += ["", "## Where the DOK 3 and 4 questions are", ""]
    for name, _, qs in corpus:
        for q in qs:
            if q["ai"] and q["ai"].get("kind") != "setup" and q["dok"] >= 3:
                L.append(f"- **{name}** [DOK {q['dok']}, {BLOOM[q['bloom']-1]}] {q['text']}" + (f"  \n  *{q['ai']['why']}*" if q['ai'].get('why') else ""))
    L += ["", "## A run of the most common kind", ""]
    top = grid.most_common(1)[0][0] if grid else None
    if top:
        L.append(f"The fullest cell is **{BLOOM[top[0]-1]} at DOK {top[1]}** ({grid[top]} questions): {CRM[top[0]][top[1]-1]}. A few:")
        L += [f"- {q['text']}" for q in [q for q in allq if (q['bloom'], q['dok']) == top][:8]]
    (out / "summary.md").write_text("\n".join(L) + "\n")
    print("\n".join(L[:14]))


if __name__ == "__main__":
    main()

"""Find subject pronoun + present-tense verb in the spoken France part of CEFC-ORFEO.

Usage: python extract.py CEFC_DIR OUT_DIR

CEFC_DIR is the unzipped cefc-no-audio.zip (one folder per subcorpus).
Writes OUT_DIR/tokens.csv (one row per hit) and OUT_DIR/transcript_counts.csv,
and prints the counts.
"""
import collections, csv, glob, os, sys

from verbs import ALL, CONTROL, CORE, FORMS

# Spoken, recorded in France. Left out: cfpb, valibel (Belgium), ofrom (Switzerland)
# and the written corpora.
SPOKEN_FRANCE = ["cfpp", "clapi", "coralrom", "crfp", "decoda", "fleuron",
                 "frenchoralnarrative", "reunions-de-travail", "tcof", "tufs"]
PLURAL = {"ils", "elles"}
SINGULAR = {"il", "elle", "on"}
BETWEEN = {"CLN", "CLI"}  # ne and object clitics: ils (ne) (le/lui/y/en...) VERB


def sentences(path):
    sent = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line:
                if sent:
                    yield sent
                sent = []
            elif not line.startswith("#"):
                cols = line.split("\t")
                if len(cols) >= 13:
                    sent.append(cols)
    if sent:
        yield sent


def main(root, out):
    rows = []
    for corpus in SPOKEN_FRANCE:
        for path in sorted(glob.glob(os.path.join(root, corpus, "*.orfeo"))):
            doc = os.path.basename(path)[:-len(".orfeo")]
            for s in sentences(path):
                for i, tok in enumerate(s):
                    subj = tok[1].lower()
                    if tok[3] != "CLS" or subj not in PLURAL | SINGULAR:
                        continue
                    j = i + 1
                    while j < len(s) and s[j][3] in BETWEEN:
                        j += 1
                    if j >= len(s) or s[j][3] != "VRB":
                        continue
                    form = s[j][1].lower()
                    cands = FORMS.get(form, [])
                    if subj in SINGULAR and form in CONTROL:
                        cands = [(s[j][2], "control")]
                    if len(cands) > 1:  # form shared by two verbs: trust the tagger
                        cands = [c for c in cands if c[0] == s[j][2]]
                    # a few words either side, same speaker, for scoring the audio
                    win = [t for t in s[max(0, i - 3): j + 3] if t[12] == s[j][12]]
                    for lemma, written in cands:
                        nxt = s[j + 1] if j + 1 < len(s) else None
                        rows.append({
                            "corpus": corpus, "doc": doc, "speaker": s[j][12],
                            "number": "pl" if subj in PLURAL else "sg",
                            "subject": subj, "lemma": lemma, "written": written,
                            "verb": s[j][1], "verb_start": s[j][10], "verb_end": s[j][11],
                            "next": nxt[1] if nxt else "",
                            "next_start": nxt[10] if nxt else "",
                            "next_end": nxt[11] if nxt else "",
                            "context": " ".join(t[1] for t in s[max(0, i - 5): j + 5]),
                            "win_words": " ".join(t[1] for t in win),
                            "win_verb": win.index(s[j]),
                            "win_start": min(float(t[10]) for t in win),
                            "win_end": max(float(t[11]) for t in win),
                        })
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "tokens.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    # ils/elles + verb, by how the transcript spells the verb
    n = collections.Counter((r["lemma"], r["written"]) for r in rows if r["number"] == "pl")
    with open(os.path.join(out, "transcript_counts.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["lemma", "group", "ils_long_written", "ils_short_written"])
        for lemma in ALL:
            grp = "core" if lemma in CORE else "two-stem"
            if n[(lemma, "long")] or n[(lemma, "short")]:
                w.writerow([lemma, grp, n[(lemma, "long")], n[(lemma, "short")]])
    for grp, lemmas in (("two-stem", [l for l in ALL if l not in CORE]), ("core", list(CORE))):
        lo = sum(n[(l, "long")] for l in lemmas)
        sh = sum(n[(l, "short")] for l in lemmas)
        print(f"{grp}: ils/elles + long {lo}, + short {sh} ({100 * sh / (lo + sh):.1f}% short)")
    # the transcriber wrote il/elle but the verb in its plural form
    print("il/elle/on + ils form:", sum(1 for r in rows if r["number"] == "sg" and r["written"] == "long"))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

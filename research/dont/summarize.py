"""Join the candidates from contexts.py with the hand verdicts in judged.csv,
count each strategy per verb, and look at who uses which.

Usage: python summarize.py CEFC_DIR CANDIDATES_CSV RESULTS_DIR

RESULTS_DIR must hold judged.csv: one row per candidate whose verdict isn't
the default (dont for dont, x = not a real case for everything else). Writes
RESULTS_DIR/strategies.csv (per verb), RESULTS_DIR/cases.csv (every real case,
with the speaker's age and education) and RESULTS_DIR/speakers.csv (how often
each group says dont at all, per million words), and prints all three.
"""
import collections, csv, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from orfeo import SPOKEN_FRANCE, documents, sentences, speakers
from rates import repeated

STRATEGIES = ["dont", "dont+en", "que", "que+en", "de…que", "de ce que", "de qui"]
EDUCATION = {"études supérieures": "higher education", "lycée": "secondary",
             "collège": "secondary", "primaire": "primary"}


def group(info):
    """Education and age band of a speaker, 'unknown' where not recorded."""
    ed = info.get("education", "").lower()
    ed = next((v for k, v in EDUCATION.items() if k in ed or k.replace("é", "e") in ed),
              "higher education" if "supérieur" in ed else "unknown")
    age = info.get("age", "")
    age = age if age[:1].isdigit() else "unknown"
    return ed, age


def main(root, cand_path, res):
    judged = {r["id"]: r for r in csv.DictReader(open(os.path.join(res, "judged.csv"), encoding="utf-8"))}
    meta = {}
    cases = []
    for r in csv.DictReader(open(cand_path, encoding="utf-8")):
        verdict = judged[r["id"]]["verdict"] if r["id"] in judged else (
            "dont" if r["strategy"] == "dont" else "x")
        if verdict == "x":
            continue
        key = (r["corpus"], r["doc"])
        if key not in meta:
            meta[key] = speakers(root, *key)
        info = meta[key].get(r["speaker"], {})
        ed, age = group(info)
        cases.append({"id": r["id"], "verdict": verdict, "target": r["target"],
                      "corpus": r["corpus"], "speaker": r["speaker"], "education": ed,
                      "age": age, "context": r["context"]})

    # strategies per verb
    n = collections.Counter((c["target"], c["verdict"]) for c in cases)
    targets = sorted({c["target"] for c in cases}, key=lambda t: (-sum(n[(t, s)] for s in STRATEGIES), t))
    with open(os.path.join(res, "strategies.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["verb"] + STRATEGIES + ["total"])
        for t in targets + ["ALL"]:
            vals = [sum(n[(x, s)] for x in targets) if t == "ALL" else n[(t, s)] for s in STRATEGIES]
            w.writerow([t] + vals + [sum(vals)])
            print(f"{t:22}", " ".join(f"{s} {v}" for s, v in zip(STRATEGIES, vals) if v), "| total", sum(vals))
    with open(os.path.join(res, "cases.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(cases[0]))
        w.writeheader()
        w.writerows(sorted(cases, key=lambda c: (c["verdict"], c["target"], c["id"])))

    # who: dont and que cases by education and age
    print()
    for field in ("education", "age"):
        for v in ("dont", "que"):
            sel = [c for c in cases if c["verdict"].startswith(v)]
            print(f"{v:5} by {field}:", dict(collections.Counter(c[field] for c in sel).most_common()),
                  "| speakers:", len({(c['corpus'], c['speaker']) for c in sel}))

    # dont per million words, by speaker group (all dont, not only the cases).
    # The subcorpora differ a lot (interviews against phone calls), and so do
    # their speakers, so each group is also compared with what its words would
    # give at the rate of the subcorpora they come from (vs_corpus: 1 = average).
    words, donts = collections.Counter(), collections.Counter()
    for corpus, doc, path in documents(root, SPOKEN_FRANCE):
        info = speakers(root, corpus, doc)
        for s in sentences(path):
            for i, t in enumerate(s):
                ed, age = group(info.get(t[12], {}))
                for g in (("education", ed), ("age", age), ("all", "all")):
                    words[(corpus,) + g] += 1
                    if t[1].lower() == "dont" and not repeated(s, i):
                        donts[(corpus,) + g] += 1
    rate = {c: donts[(c, "all", "all")] / words[(c, "all", "all")] for c in SPOKEN_FRANCE}
    rows = []
    for g in sorted({k[1:] for k in words}):
        keys = [k for k in words if k[1:] == g]
        w_, d_ = sum(words[k] for k in keys), sum(donts[k] for k in keys)
        expected = sum(words[k] * rate[k[0]] for k in keys)
        rows.append({"field": g[0], "group": g[1], "words": w_, "dont": d_,
                     "dont_per_million": round(1e6 * d_ / w_),
                     "vs_corpus": round(d_ / expected, 2) if expected else ""})
    with open(os.path.join(res, "speakers.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print()
    for r in rows:
        print("{field:10} {group:17} {words:>8} words  dont {dont:>4}  {dont_per_million:>4}/M"
              "  vs corpus {vs_corpus}".format(**r))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])

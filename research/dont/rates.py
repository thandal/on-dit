"""How often dont occurs in speech and in writing, against qui, que and où.

Usage: python rates.py CEFC_DIR OUT_DIR

Counts every subcorpus of CEFC-ORFEO recorded or written in France: speech,
edited writing (books, newspapers, science) and comere, which is online writing
(tweets, SMS, Wikipedia talk pages, a chat), kept apart. Writes
OUT_DIR/rates.csv (one row per subcorpus, comere split by kind, plus totals).
Also draws 100 random dont from speech and 100 from edited writing for sorting
by hand into uses: if OUT_DIR/dont_sample.csv already holds the sorted sample,
it prints the breakdown; otherwise it writes the sample there to be sorted.

Words are all tokens except punctuation. dont is always a relative pronoun, so
every dont counts. qui, que and où count as relatives when the tagger marks
them as such (PRQ) and they come straight after a noun, a pronoun or a number
(skipping euh-type fillers and commas): le mec qui, ce que, là où. That leaves
out questions (qui c'est, est-ce que, t'es où) and also some real relatives.
A word said twice in a row (dont euh dont je parle) counts once.
"""
import collections, csv, os, random, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from orfeo import SPOKEN_FRANCE, documents, sentences

WRITTEN = ["frantext", "est-republicain", "chambers-rostand", "annodis", "scientext",
           "comere"]
# comere is computer-mediated writing of several kinds; FAVI is a chat between
# international students, many not native speakers.
COMERE = [("cmr-sms", "comere: SMS"), ("cmr-polititweets", "comere: tweets"),
          ("cmr-wikiconflits", "comere: Wikipedia talk"), ("cmr-favi", "comere: FAVI chat")]
SKIP = {"euh", "heu", "hum", "hein", "ben", "bah", ","}
RELATIVES = ("qui", "que", "où", "dont")
# uses of dont in the hand-sorted sample: a verb or adjective that takes de
# (dont je parle), la façon dont, 'whose' (dont le nom), 'including' (dont deux)
USES = ("verb", "way", "whose", "including", "unclear")


def label(corpus, doc):
    for prefix, name in COMERE:
        if corpus == "comere" and doc.startswith(prefix):
            return name
    return corpus


def norm(w):
    w = w.lower()
    return "que" if w == "qu'" else w


def before(s, i):
    """Index of the word before s[i], skipping fillers and commas."""
    j = i - 1
    while j >= 0 and s[j][1].lower() in SKIP:
        j -= 1
    return j


def repeated(s, i):
    """Is s[i] said again straight after? Then only the last one counts."""
    j = i + 1
    while j < len(s) and s[j][1].lower() in SKIP:
        j += 1
    return j < len(s) and norm(s[j][1]) == norm(s[i][1])


def relative(s, i):
    """Is s[i] (qui, que, qu', où, tagged PRQ) a relative pronoun?"""
    j = before(s, i)
    if j < 0:
        return False
    w, pos = s[j][1].lower(), s[j][3]
    if w == "ce" and j > 0 and s[j - 1][1].lower() in ("est", "qu'est"):
        return False  # est-ce que
    if w == "ça" and j > 0 and s[j - 1][1].lower() in ("pour", "comme"):
        return False  # c'est pour ça que, c'est comme ça que
    if pos in ("NOM", "PRO", "NUM") or w == "là":
        return True
    return pos == "ADJ" and j > 0 and s[j - 1][3] == "DET"  # le seul que


def row(name, mode, n):
    rel = sum(n[w] for w in RELATIVES)
    return {"corpus": name, "mode": mode, "words": n["words"],
            **{w: n[w] for w in RELATIVES},
            "dont_per_million": round(1e6 * n["dont"] / n["words"]),
            "relatives_per_million": round(1e6 * rel / n["words"]),
            "dont_share_of_relatives": round(100 * n["dont"] / rel, 1)}


def main(root, out):
    counts = collections.defaultdict(collections.Counter)
    donts = {"spoken": [], "written": [], "online": []}
    for corpus in SPOKEN_FRANCE + WRITTEN:
        mode = ("spoken" if corpus in SPOKEN_FRANCE else
                "online" if corpus == "comere" else "written")
        for _, doc, path in documents(root, [corpus]):
            n = counts[(mode, label(corpus, doc))]
            sents = list(sentences(path))
            for si, s in enumerate(sents):
                after = sents[si + 1] if si + 1 < len(sents) else []  # for context
                for i, t in enumerate(s):
                    if t[3] != "PUNC":
                        n["words"] += 1
                    w = norm(t[1])
                    if w not in RELATIVES or repeated(s, i):
                        continue
                    if w == "dont":
                        n["dont"] += 1
                        donts[mode].append({
                            "id": f"{corpus}/{doc}/{si}/{i}", "mode": mode,
                            "context": " ".join(x[1] for x in s[max(0, i - 8):i]) + " [dont] "
                            + " ".join(x[1] for x in (s[i + 1:] + after)[:10])})
                    elif t[3] == "PRQ" and relative(s, i):
                        n[w] += 1

    rows = [row(name, mode, n) for (mode, name), n in counts.items()]
    for mode in ("spoken", "written", "online"):
        tot = collections.Counter()
        for (m, _), n in counts.items():
            if m == mode:
                tot.update(n)
        rows.append(row("ALL " + mode, mode, tot))
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "rates.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for r in rows:
        print("{corpus:24} {words:>9} qui {qui:>6} que {que:>6} où {où:>5} dont {dont:>5}"
              "  dont/M {dont_per_million:>5}  rel/M {relatives_per_million:>6}"
              "  dont% {dont_share_of_relatives}".format(**r))

    # 100 random dont from speech and 100 from edited writing, sorted by hand
    # into uses. An existing sorted file is kept and summarized, not overwritten.
    random.seed(1)
    sample = random.sample(donts["spoken"], 100) + random.sample(donts["written"], 100)
    path = os.path.join(out, "dont_sample.csv")
    if os.path.exists(path):
        sorted_ = list(csv.DictReader(open(path, encoding="utf-8")))
        assert [r["id"] for r in sorted_] == [r["id"] for r in sample], "sample changed"
        print()
        per_m = {r["mode"]: r["dont_per_million"] for r in rows if r["corpus"].startswith("ALL")}
        for mode in ("spoken", "written"):
            n = collections.Counter(r["use"] for r in sorted_ if r["mode"] == mode)
            print(f"{mode:8}", "  ".join(f"{u} {n[u]}% (~{per_m[mode] * n[u] // 100}/M)"
                                         for u in USES))
        return
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["id", "mode", "use", "context"])
        w.writeheader()
        w.writerows(sample)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

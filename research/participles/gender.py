"""Noun gender from the corpus itself: how often a noun follows la, une, cette, ma, ta, sa
against le, un, ce, cet, du, au (one adjective may come between). Counted over the
whole of CEFC-ORFEO, written texts included, by lemma, so plurals get the gender of
their singular. ORFEO's tags don't carry gender.

    from gender import noun_genders
    g = noun_genders(CEFC_DIR, CACHE_JSON)   # {lemma: "f" | "m" | "?"}
"""
import collections, glob, json, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from orfeo import sentences

FEM_DET = {"la", "une", "cette", "ma", "ta", "sa"}
MASC_DET = {"le", "un", "ce", "cet", "du", "au"}


def count(root):
    n = collections.defaultdict(lambda: [0, 0])
    for path in sorted(glob.glob(os.path.join(root, "*", "*.orfeo"))):
        for s in sentences(path):
            for i, t in enumerate(s):
                if t[3] != "NOM":
                    continue
                j = i - 1
                if j >= 0 and s[j][3] == "ADJ":
                    j -= 1
                if j < 0 or s[j][3] != "DET":
                    continue
                det = s[j][1].lower()
                lemma = (t[2] if t[2] not in ("-", "_", "") else t[1]).lower()
                if det in FEM_DET:
                    n[lemma][0] += 1
                elif det in MASC_DET:
                    n[lemma][1] += 1
    return n


def decide(f, m):
    if f >= 3 and f >= 0.85 * (f + m):
        return "f"
    if m >= 3 and m >= 0.85 * (f + m):
        return "m"
    return "?"


def noun_genders(root, cache):
    if os.path.exists(cache):
        counts = json.load(open(cache, encoding="utf-8"))
    else:
        counts = count(root)
        json.dump(counts, open(cache, "w", encoding="utf-8"))
    return {lemma: decide(f, m) for lemma, (f, m) in counts.items()}

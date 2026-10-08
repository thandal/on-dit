"""Find relative clauses built on a verb or expression that takes de (parler de,
avoir besoin de...) in the spoken France part of CEFC-ORFEO, and record which
strategy each one uses: dont, que, que + en, de quoi / duquel...

Usage: python contexts.py CEFC_DIR OUT_CSV [SUBCORPUS ...]

By default it reads the spoken France subcorpora; name others (frantext,
est-republicain...) to run it on writing.

Writes one row per candidate. Candidates are deliberately broad: que is any
que/qu' (relative or conjunction, the tagger can't be trusted on the
non-standard ones) that follows a noun or pronoun. The rows still need
checking by hand (judged.csv); summarize.py joins the two.
"""
import collections, csv, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from orfeo import SPOKEN_FRANCE, documents, sentences

FILLERS = {"euh", "heu", "hum", "hein", "ben", "bah", "bon", "quoi"}
REFLEXIVE = {"me", "m'", "te", "t'", "se", "s'", "nous", "vous"}
DE = {"de", "d'", "du", "des"}
# words that may sit between the verb and its de (j'ai vraiment besoin de, je
# me souviens plus de)
ADVERBS = {"pas", "plus", "vraiment", "absolument", "beaucoup", "souvent", "jamais",
           "toujours", "trop", "tellement", "aussi", "déjà", "encore", "un", "peu",
           "bien", "assez", "euh", "hein", "très", "même", "rien", "tout", "surtout"}
SOUVENIR = re.compile(r"souvien|souven(ais|ait|aient|ez|ons|iez|u|ue|us|ues|ir)$")
WINDOW = 7          # tokens after the relative word in which to look for the verb
STOP = {"CSU", "PRQ", "COO"}  # a new clause starts: stop looking


def target(win, k):
    """If win[k] is one of the verbs or expressions, return its name."""
    t = win[k]
    form, lemma, pos = t[1].lower(), t[2].lower(), t[3]
    prev = [w[1].lower() for w in win[max(0, k - 3):k]]
    verb = pos in ("VRB", "VPP", "VNF")
    refl = bool(set(prev) & REFLEXIVE)
    if verb and lemma == "parler":
        return "parler de"
    if form == "besoin":
        return "avoir besoin de"
    if form == "envie" and pos == "NOM":
        return "avoir envie de"
    if form == "peur" and pos == "NOM":
        return "avoir peur de"
    if form == "honte" and pos == "NOM":
        return "avoir honte de"
    if form == "habitude" and pos == "NOM":
        return "avoir l'habitude de"
    if verb and SOUVENIR.match(form):  # the tagger's lemma is unreliable here
        return "se souvenir de"
    if verb and lemma == "occuper" and refl:
        return "s'occuper de"
    if verb and lemma == "servir" and refl:
        return "se servir de"
    if verb and lemma == "rêver":
        return "rêver de"
    if form == "partie" and prev and prev[-1][:2] in ("fa", "fe", "fo", "fi"):
        return "faire partie de"
    if verb and lemma == "agir" and refl:
        return "s'agir de"
    if verb and lemma == "plaindre" and refl:
        return "se plaindre de"
    if verb and lemma == "moquer" and refl:
        return "se moquer de"
    if verb and lemma == "occuper" and refl:
        return "s'occuper de"
    if form in ("fier", "fière", "fiers", "fières"):
        return "être fier de"
    if form == "question" and prev and prev[-1] in ("est", "était", "sera", "a"):
        return "être question de"
    if verb and lemma == "profiter":
        return "profiter de"
    return None


def de_after(win, k):
    """The words after the target: is its de slot filled (besoin de, parlé du)?"""
    j = k + 1
    while j < len(win) and win[j][1].lower() in ADVERBS:
        j += 1
    if j < len(win) and win[j][1].lower() in DE:
        return "de"
    return ""


def antecedent(s, i):
    """The word before the relative word, skipping fillers, if it can be a head
    noun or pronoun (a noun, a pronoun such as ce or ça, a number, là, or an
    adjective after a determiner: le seul que)."""
    j = i - 1
    # skip fillers, and the same word said twice (des endroits que que tu as besoin)
    while j >= 0 and (s[j][1].lower() in FILLERS or s[j][1].lower() == s[i][1].lower()):
        j -= 1
    if j < 0:
        return None
    t = s[j]
    if t[1].lower() == "ce" and j > 0 and s[j - 1][1].lower() in ("est", "qu'est"):
        return None  # est-ce que: a question
    if t[3] in ("NOM", "PRO", "NUM") or t[1].lower() == "là":
        return t
    if t[3] == "ADJ" and j > 0 and s[j - 1][3] == "DET":
        return t
    return None


def strategy(s, i, before):
    """Which relative word starts at s[i], or None. Returns (strategy, start of
    the clause after it). before is s with the end of the sentence before it
    in front, offset accordingly, for finding the antecedent."""
    f = s[i][1].lower()
    nxt = s[i + 1][1].lower() if i + 1 < len(s) else ""
    if f == "dont":
        return "dont", i + 1
    if f in ("que", "qu'") and s[i][3] in ("PRQ", "CSU") and antecedent(*before):
        return "que", i + 1
    if f in ("duquel", "desquels", "desquelles"):
        return "duquel", i + 1
    if f == "de" and nxt in ("laquelle", "lesquels", "lesquelles"):
        return "duquel", i + 2
    if f in ("de", "d'") and nxt in ("qui", "quoi") and s[i + 1][3] == "PRQ":
        return "de " + nxt, i + 2
    return None


def main(root, out, corpora=SPOKEN_FRANCE):
    rows = []
    for corpus, doc, path in documents(root, corpora):
        prev = []
        for si, s in enumerate(sentences(path)):
            # the transcripts are cut into units that can split a noun from its
            # relative clause: let the antecedent be at the end of the unit before,
            # if the same speaker said it
            tail = prev[-8:] if prev and s and prev[-1][12] == s[0][12] else []
            seq = tail + s
            prev = s
            for i in range(len(s)):
                hit = strategy(s, i, (seq, len(tail) + i))
                if not hit:
                    continue
                strat, start = hit
                ant = antecedent(seq, len(tail) + i)
                if ant and ant[2].lower() in ("façon", "manière"):
                    continue  # la façon dont: "the way", not a verb taking de
                win = []
                for t in s[start:start + WINDOW]:
                    if t[3] in STOP:
                        break
                    win.append(t)
                for k in range(len(win)):
                    name = target(win, k)
                    if not name:
                        continue
                    clause = [w[1].lower() for w in win[:k]]
                    rows.append({
                        "id": f"{corpus}/{doc}/{si}/{i}",
                        "corpus": corpus, "doc": doc, "speaker": s[i][12],
                        "strategy": strat, "target": name,
                        "en": "en" if "en" in clause else "",
                        "de_after": de_after(win, k),
                        "antecedent": ant[1] if ant else "",
                        "tag": s[i][3],
                        "context": " ".join(t[1] for t in seq[max(0, len(tail) + i - 8):len(tail) + i])
                        + " [" + s[i][1] + "] "
                        + " ".join(t[1] for t in s[i + 1:start + k + 6]),
                    })
                    break
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    n = collections.Counter((r["strategy"], r["en"], r["de_after"]) for r in rows)
    for k, v in sorted(n.items()):
        print(k, v)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3:] or SPOKEN_FRANCE)

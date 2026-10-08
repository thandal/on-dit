"""Find avoir and être + a participle with an audible feminine (fait/faite, pris/prise...)
in the spoken France part of CEFC-ORFEO, and sort them by what the participle
should agree with.

Usage: python3 extract.py CEFC_DIR OUT_DIR

Writes OUT_DIR/tokens.csv (one row per hit) and prints counts by context and by
how the transcript spells the participle. Contexts:

  rel        noun + que + subject + avoir + participle: la lettre que j'ai écrite.
             The antecedent's gender is in `gender` (f, m or ?). Needs checking by
             hand: que is often not the object (la fois que j'ai pris le train).
  rel_ce     ce que + subject + avoir + participle: ce que j'ai fait. Never agrees.
  clitic     l' or les + avoir + participle: je l'ai prise. Gender unknown here.
  after      subject + avoir + participle + its object: j'ai pris la voiture.
             Nothing comes before to agree with, so masculine only.
  etre_f     elle(s) + être + participle: elle est morte, elle a été prise.
  etre_np    noun + être + participle: ma mère est morte. Gender in `gender`.
  refl_f     elle(s) + se + être + participle: elle s'est mise à pleurer.
  etre_m     il(s) + être + participle: masculine only.
"""
import csv, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
from orfeo import documents, sentences, speakers
from gender import FEM_DET, MASC_DET, noun_genders
from participles import FORMS

AVOIR = set("ai as a avons avez ont avais avait avions aviez avaient aurai auras aura "
            "aurons aurez auront aurais aurait aurions auriez auraient aie aies ait ayons "
            "ayez aient avoir ayant".split())
ETRE = set("suis es est sommes êtes sont étais était étions étiez étaient serai seras sera "
           "serons serez seront serais serait serions seriez seraient sois soit soyons soyez "
           "soient être étant".split())
QUE = {"que", "qu'"}
REFLEXIVE = {"se", "s'"}
OBJECT_CLITICS = {"l'", "les"}
BETWEEN = {"ADN", "ADV", "INT"}  # pas, déjà, bien, euh...
SKIP = {"euh", "hein", "ben", "bah", "bon"}


def form(t):
    return t[1].lower()


def find_aux(s, p):
    """Index of the auxiliary before the participle at p, and whether été comes
    between (a passive: elle a été prise). None if there is none."""
    passive = False
    j = p - 1
    while j >= 0 and p - j <= 5:
        f = form(s[j])
        if f == "été" and s[j][2] == "être":
            passive = True
        elif s[j][3] in BETWEEN and f not in AVOIR | ETRE:
            pass
        elif s[j][2] in ("avoir", "être") and f in AVOIR | ETRE:
            return j, passive
        else:
            return None
        j -= 1
    return None


def subject(s, a):
    """(index where the subject starts, subject words, clitics between) for the aux at a."""
    j = a - 1
    clitics = []
    while j >= 0 and s[j][3] in ("CLN", "CLI"):
        clitics.append(form(s[j]))
        j -= 1
    if j < 0:
        return None
    if s[j][3] == "CLS":
        return j, form(s[j]), clitics
    k = j
    while k >= 0 and j - k < 4 and s[k][3] in ("NOM", "DET", "ADJ", "PRO", "NUM"):
        k -= 1
    if k == j:
        return None
    return k + 1, " ".join(form(t) for t in s[k + 1: j + 1]), clitics


def noun_phrase(s, n, genders):
    """For a noun at n: (determiner, noun, gender, how the gender was decided)."""
    det, k = "", n - 1
    while k >= 0 and n - k <= 3 and s[k][3] in ("ADJ", "NUM", "INT"):
        k -= 1
    if k >= 0 and s[k][3] == "DET":
        det = form(s[k])
    lemma = (s[n][2] if s[n][2] not in ("-", "_", "") else s[n][1]).lower()
    if det in FEM_DET:
        return det, form(s[n]), "f", "det"
    if det in MASC_DET:
        return det, form(s[n]), "m", "det"
    return det, form(s[n]), genders.get(lemma, "?"), "corpus"


def antecedent(s, q, genders):
    """What comes before que at q: (kind, words, gender, source)."""
    j = q - 1
    while j >= 0 and form(s[j]) in SKIP:
        j -= 1
    if j < 0:
        return None
    f, pos = form(s[j]), s[j][3]
    if f in ("celle", "celles"):
        return "pronoun", f, "f", "pronoun"
    if f in ("celui", "ceux"):
        return "pronoun", f, "m", "pronoun"
    if f in ("ce", "c'") or (f == "tout" and pos == "PRO"):
        return "ce", f, "m", "pronoun"
    if pos == "ADJ" and j >= 1 and s[j - 1][3] == "NOM":  # la chose importante que
        j -= 1
        pos = "NOM"
    if pos == "NOM":
        det, noun, g, src = noun_phrase(s, j, genders)
        return "noun", f"{det} {noun}".strip(), g, src
    return None


def classify(s, p, genders):
    """(context, gender, antecedent, source) for the participle at p, or None."""
    found = find_aux(s, p)
    if not found:
        return None
    a, passive = found
    aux = "être" if s[a][2] == "être" or passive else "avoir"
    subj = subject(s, a)
    if not subj:
        return None
    start, subj_words, clitics = subj
    if aux == "être":
        if subj_words in ("elle", "elles"):
            return ("refl_f" if set(clitics) & REFLEXIVE else "etre_f"), "f", subj_words, "pronoun"
        if subj_words in ("il", "ils") and not set(clitics) & REFLEXIVE:
            return "etre_m", "m", subj_words, "pronoun"
        if s[start][3] != "CLS" and not clitics:
            nouns = [k for k in range(start, a) if s[k][3] == "NOM"]
            if nouns and s[start][3] == "DET":
                det, noun, g, src = noun_phrase(s, nouns[-1], genders)
                return "etre_np", g, f"{det} {noun}", src
        return None
    if set(clitics) & OBJECT_CLITICS:
        return "clitic", "?", next(c for c in clitics if c in OBJECT_CLITICS), ""
    if clitics and not set(clitics) <= {"ne", "n'", "y", "en", "lui", "leur"}:
        return None  # me, te, nous, vous, se: object or not, can't tell
    q = start - 1
    while q >= 0 and form(s[q]) in SKIP:
        q -= 1
    if q >= 0 and form(s[q]) in QUE:
        ant = antecedent(s, q, genders)
        if ant:
            kind, words, g, src = ant
            return ("rel_ce" if kind == "ce" else "rel"), g, words, src
        return None
    if s[start][3] == "CLS" and p + 1 < len(s) and (
            s[p + 1][3] == "DET" or form(s[p + 1]) in ("ça", "cela")):
        return "after", "m", "", ""
    return None


def after_flags(s, p):
    """What follows the participle, for spotting que that isn't its object."""
    nxt = [t for t in s[p + 1: p + 4] if form(t) not in SKIP]
    if not nxt:
        return ""
    f0 = form(nxt[0])
    if nxt[0][3] == "VNF":
        return "infinitive"
    if f0 in ("de", "d'", "à") and len(nxt) > 1 and nxt[1][3] == "VNF":
        return "infinitive"
    if f0 in QUE:
        return "que"
    if nxt[0][3] == "DET" or f0 in ("ça", "cela"):
        return "object"
    return ""


def main(root, out):
    os.makedirs(out, exist_ok=True)
    genders = noun_genders(root, os.path.join(out, "noun_gender_counts.json"))
    rows = []
    for corpus, doc, path in documents(root):
        meta = speakers(root, corpus, doc)
        for s in sentences(path):
            for p, t in enumerate(s):
                if form(t) not in FORMS:
                    continue
                c = classify(s, p, genders)
                if not c:
                    continue
                ctx, gender, ant, src = c
                masc, written = FORMS[form(t)]
                nxt = s[p + 1] if p + 1 < len(s) else None
                info = meta.get(t[12], {})
                rows.append({
                    "corpus": corpus, "doc": doc, "speaker": t[12],
                    "sex": info.get("sex", ""), "age": info.get("age", ""),
                    "education": info.get("education", ""),
                    "first_language": info.get("first_language", ""),
                    "context_type": ctx, "gender": gender, "antecedent": ant,
                    "gender_source": src, "participle": masc, "written": written,
                    "form": t[1], "follows": after_flags(s, p),
                    "start": t[10], "end": t[11],
                    "next": nxt[1] if nxt else "",
                    "context": " ".join(u[1] for u in s[max(0, p - 12): p + 6]),
                })
    with open(os.path.join(out, "tokens.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

    print(f"{'context':<10}{'gender':>7}{'masc':>7}{'fem':>6}")
    keys = sorted({(r["context_type"], r["gender"]) for r in rows})
    for ctx, g in keys:
        sub = [r for r in rows if (r["context_type"], r["gender"]) == (ctx, g)]
        fem = sum(r["written"] == "f" for r in sub)
        print(f"{ctx:<10}{g:>7}{len(sub) - fem:>7}{fem:>6}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

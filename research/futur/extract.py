"""Find futur simple (on verra) and futur proche (on va voir) in the spoken
France part of CEFC-ORFEO.

Usage: python extract.py CEFC_DIR OUT_DIR

Futur simple: a finite verb (VRB) whose form is its lemma's future stem plus
-ai, -as, -a, -ons, -ez, -ont (parlera, prendrai, sera, ira, verra, faudra).
Futur proche: aller in the present (vais, vas, va, allons, allez, vont) with a
subject before it, then an infinitive, with only pronouns, ne, a negation word
or a short adverb between (je vais pas le faire, on va bien voir).

Writes OUT_DIR/tokens.csv (one row per future) and OUT_DIR/fs_rejected.csv
(VRB forms ending like a future that didn't pass the lemma check, to look over).
"""
import collections, csv, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from orfeo import documents, sentences  # noqa: E402

ENDINGS = ("ai", "as", "a", "ons", "ez", "ont")
PERSON = {"ai": "je", "as": "tu", "a": "il", "ons": "nous", "ez": "vous", "ont": "ils"}
# Future stems that aren't the infinitive. Prefixed verbs are matched by suffix:
# reviendra (revenir), obtiendra (obtenir), refera (refaire).
IRREGULAR = {
    "être": "ser", "avoir": "aur", "aller": "ir", "faire": "fer", "pouvoir": "pourr",
    "savoir": "saur", "vouloir": "voudr", "falloir": "faudr", "valoir": "vaudr",
    "pleuvoir": "pleuvr", "devoir": "devr", "recevoir": "recevr", "apercevoir": "apercevr",
    "voir": "verr", "envoyer": "enverr", "courir": "courr", "mourir": "mourr",
    "venir": "viendr", "tenir": "tiendr", "asseoir": "assiér", "cueillir": "cueiller",
}
LEMMA_FIX = {"saurer": "savoir", "faillir": "falloir", "ailler": "aller"}
ALLER = {"vais": "je", "vas": "tu", "va": "il", "allons": "nous", "allez": "vous", "vont": "ils"}
NEG = {"pas", "jamais", "rien", "plus", "personne", "point", "guère"}
BETWEEN_ADV = {"bien", "peut-être", "encore", "jamais", "toujours", "vraiment", "tout",
               "quand", "même", "aussi", "déjà", "juste", "peut", "être", "plus", "pas", "rien",
               "euh", "donc", "alors", "enfin", "forcément", "sûrement", "certainement"}
SUBJECT_POS = {"CLS", "PRO", "PRQ", "NOM"}
TEMPORAL = {"quand", "lorsque", "lorsqu'", "dès", "sitôt"}  # dès que, une fois que below


def norm(s):
    """Fold the spelling changes of -er stems (appell/appel, achèt/achet, essai/essay)."""
    s = s.translate(str.maketrans("éèêë", "eeee")).replace("y", "i")
    return re.sub(r"(.)\1", r"\1", s)


def fut_lemma(form, lemma):
    """The verb's lemma if form is a futur simple, else None."""
    lemma = LEMMA_FIX.get(lemma, lemma).replace("(se) ", "")
    for end in ENDINGS:
        if not form.endswith(end):
            continue
        stem = form[: -len(end)]
        for verb, irr in IRREGULAR.items():
            if stem.endswith(irr) and (lemma.endswith(verb) or stem == irr):
                return lemma if lemma.endswith(verb) else verb
        if lemma.endswith("er") and stem.endswith("er"):
            if norm(stem[:-2]) == norm(lemma[:-2]):
                return lemma  # parlera, appellera, achètera, essaiera
        elif lemma.endswith("re") and stem == lemma[:-1]:
            return lemma  # prendra, dira, mettra
        elif lemma.endswith("ir") and stem == lemma:
            return lemma  # finira, partira, sortira
        elif lemma == form and form not in ("cetera", "etcetera") and len(stem) > 4 and \
                stem.endswith(("er", "iendr")):
            return form  # not lemmatized by the tagger: souviendrai, complètera
    return None


def negation(s, i, after):
    """The negation word of the verb at i: one at the positions in after (pas, jamais,
    rien...), else "ne" if ne comes before the verb, else "". ne...que (only) isn't one,
    and nor is plus meaning "more" (plus de, plus simple)."""
    for k in after:
        if k >= len(s):
            break
        w = s[k][1].lower()
        nxt = s[k + 1][1].lower() if k + 1 < len(s) else ""
        more = nxt in ("de", "d'", "que", "qu'") or (
            k + 1 < len(s) and s[k + 1][3] in ("ADJ", "ADV") and nxt != "là")
        if w in NEG and not (w == "plus" and more) \
                and (w != "personne" or s[k][3] == "PRO"):
            return w
    j = i - 1
    while j >= 0 and s[j][3] in ("CLI", "CLN"):
        if s[j][3] == "CLN":
            only = any(s[k][1].lower() in ("que", "qu'") for k in range(i + 1, min(i + 3, len(s))))
            return "" if only else "ne"
        j -= 1
    return ""


def subject(s, i):
    """The word before the clitic group of the verb at i, if it can be a subject."""
    j = i - 1
    while j >= 0 and s[j][3] in ("CLI", "CLN"):
        j -= 1
    return s[j] if j >= 0 and s[j][3] in SUBJECT_POS else None


def temporal(s, i):
    """Is the verb at i in a clause opened by quand, lorsque, dès que, une fois que?"""
    lo = max(0, i - 5)
    words = [t[1].lower() for t in s[lo:i]]
    for k, w in enumerate(words):
        rest = words[k + 1:]
        if w in ("quand", "lorsque", "lorsqu'") and "est-ce" not in rest and "-ce" not in rest:
            return True
        if w in ("que", "qu'") and k and words[k - 1] in ("dès", "fois", "sitôt", "moment"):
            return True
    return False


def situation(xml):
    """Coarse situation from the TEI header: conversation, interview, meeting..."""
    m = re.search(r'<catRef corresp="type" target="([^"]*)"', xml)
    t = m.group(1) if m else ""
    return {"conversation": "conversation", "repas": "conversation", "entretien": "interview",
            "réunion": "meeting", "narration": "storytelling", "transaction": "service",
            "consultation": "service"}.get(t, "public speech" if t else "")


def main(root, out):
    rows, rejected = [], collections.Counter()
    for corpus, doc, path in documents(root):
        xp = os.path.join(root, corpus, doc + ".xml")
        sit = situation(open(xp, encoding="utf-8").read()) if os.path.exists(xp) else ""
        if corpus == "decoda":
            sit = "phone help line"
        elif corpus == "clapi" and not sit:
            sit = "conversation"
        for s in sentences(path):
            for i, t in enumerate(s):
                if t[3] != "VRB":
                    continue
                form = t[1].lower()
                row = None
                if form in ALLER and t[2] == "aller":
                    j = i + 1
                    while j < len(s) and (s[j][3] in ("CLI", "CLN") or
                                          (s[j][3] in ("ADV", "ADN", "INT", "PRO")
                                           and s[j][1].lower() in BETWEEN_ADV)):
                        j += 1
                    if j >= len(s) or s[j][3] != "VNF":
                        continue
                    subj = subject(s, i)
                    inf = s[j][2].replace("(se) ", "")
                    if subj is None and inf != "falloir":
                        continue  # va voir ! (imperative), or no subject in the transcript
                    row = {"type": "proche", "verb": inf, "form": form + " " + s[j][1],
                           "person": ALLER[form], "negation": negation(s, i, range(i + 1, j)),
                           "aux": 0, "between": " ".join(x[1].lower() for x in s[i + 1: j])}
                elif re.search(r"r(ai|as|a|ons|ez|ont)$", form):
                    lemma = fut_lemma(form, t[2])
                    if lemma is None:
                        rejected[(form, t[2])] += 1
                        continue
                    end = next(e for e in ("ons", "ont", "ez", "ai", "as", "a") if form.endswith(e))
                    # futur antérieur (il aura fini): avoir + participle
                    nxt = [x for x in s[i + 1: i + 4] if x[3] not in ("ADV", "ADN")]
                    aux = int(lemma == "avoir" and bool(nxt) and nxt[0][3] == "VPP")
                    row = {"type": "simple", "verb": lemma, "form": form,
                           "person": PERSON[end], "negation": negation(s, i, [i + 1]),
                           "aux": aux, "between": ""}
                if row:
                    subj = subject(s, i)
                    row.update({
                        "corpus": corpus, "situation": sit, "doc": doc, "speaker": t[12],
                        "start": t[10], "subject": subj[1].lower() if subj else "",
                        "before": " ".join(x[1].lower() for x in s[max(0, i - 3): i]),
                        "after_quand": int(temporal(s, i)),
                        "context": " ".join(x[1] for x in s[max(0, i - 6): i + 6]),
                    })
                    rows.append(row)
    os.makedirs(out, exist_ok=True)
    fields = ["type", "verb", "form", "person", "subject", "before", "between", "negation",
              "aux", "after_quand",
              "corpus", "situation", "doc", "speaker", "start", "context"]
    with open(os.path.join(out, "tokens.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    with open(os.path.join(out, "fs_rejected.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["form", "lemma", "n"])
        for (f, l), n in rejected.most_common():
            w.writerow([f, l, n])
    n = collections.Counter(r["type"] for r in rows)
    print(f"futur simple {n['simple']}, futur proche {n['proche']}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

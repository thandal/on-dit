"""Find subjunctive triggers + que + verb in the spoken France part of CEFC-ORFEO,
and sort each verb by whether it is subjunctive or indicative.

Usage: python extract.py CEFC_DIR OUT_DIR

Writes OUT_DIR/tokens.csv: every trigger + verb found, with whether the verb is
counted. Only verbs whose subjunctive sounds different from the indicative for the
person used are counted (see forms.py). summarize.py makes the tables.
"""
import csv, os, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from orfeo import documents, sentences  # noqa: E402
from forms import classify  # noqa: E402

FALLOIR = {"faut": "il faut que", "faudrait": "il faudrait que", "fallait": "il fallait que",
           "fallu": "il a fallu que", "faudra": "il faudra que", "faille": "il faut que"}
VOULOIR = {"veux": "pres", "veut": "pres", "voulez": "pres", "veulent": "pres", "voulons": "pres",
           "voudrais": "cond", "voudrait": "cond", "voudriez": "cond", "voudraient": "cond",
           "voudrions": "cond", "voulais": "past", "voulait": "past", "voulaient": "past",
           "voulu": "past", "voudra": "fut", "voudras": "fut", "vouloir": "inf"}
# Words that can come between the trigger verb and que: il faut bien que, je veux pas que.
FILLER = {"bien", "pas", "plus", "vraiment", "absolument", "surtout", "euh", "même", "quand",
          "toujours", "juste", "aussi", "encore", "abord", "d'", "maintenant", "peut-être",
          "simplement", "seulement", "déjà", "également", "donc", "alors", "enfin", "hein",
          "forcément", "obligatoirement", "mieux", "beaucoup", "un", "peu", "jamais", "là"}
SUBJ = {"je": "je", "j'": "je", "tu": "tu", "t'": "tu", "il": "il", "elle": "il", "on": "il",
        "c'": "il", "ce": "il", "ça": "il", "cela": "il", "ils": "ils", "elles": "ils",
        "vous": "vous", "nous": "nous"}
PLURAL_DET = {"les", "des", "ces", "mes", "tes", "ses", "nos", "vos", "leurs", "certains",
              "plusieurs", "quelques", "deux", "trois"}
STOP = {"CSU", "PRQ", "VNF", "VPP", "COO"}
# Group the trigger labels for the summary.
GROUP = {"il faut que": "falloir que", "il faudrait que": "falloir que",
         "il fallait que": "falloir que", "il a fallu que": "falloir que",
         "il faudra que": "falloir que"}


def flatten(s):
    """Words of a sentence, lowercased, with the index of the token each comes from."""
    words, tok = [], []
    for ti, t in enumerate(s):
        for w in t[1].lower().split():
            words.append(w)
            tok.append(ti)
    return words, tok


def trigger(words, k, s, tok):
    """Name of the trigger ending just before the que at words[k], or None."""
    w = lambda i: words[i] if i >= 0 else "^"
    j = k - 1
    # bien que on its own (although), c'est bien que (it's good that)
    if w(j) == "bien":
        before = w(j - 1)
        if before in ("est", "serait", "était", "sera") and w(j - 2) in ("c'", "ce", "ça"):
            return "c'est bien que"
        verb_before = {w(j - 2), w(j - 3)} & (set(FALLOIR) | set(VOULOIR))
        if before in ("^", "euh", "mais", "donc", "alors", "que", "qu'", "bon", "ben", "bah", "or") \
                and not verb_before:
            return "bien que"
    if w(j) == "mieux" and w(j - 1) in ("vaut", "vaudrait", "valait", "valu", "vaudra"):
        return "il vaut mieux que"
    # skip words that can sit between the trigger verb and que
    n = 0
    while w(j) in FILLER and n < 3:
        j, n = j - 1, n + 1
    a, b, c = w(j), w(j - 1), w(j - 2)
    if a in FALLOIR:
        return FALLOIR[a]
    if a in VOULOIR and tok and s[tok[j]][3] in ("VRB", "VNF", "VPP"):
        return "vouloir que (" + VOULOIR[a] + ")"
    lemma = s[tok[j]][2] if j >= 0 else ""
    pos = s[tok[j]][3] if j >= 0 else ""
    if lemma == "aimer" and pos in ("VRB", "VNF"):
        return "aimer que"
    if lemma == "préférer" and pos in ("VRB", "VNF"):
        return "préférer que"
    if lemma == "souhaiter" and pos in ("VRB", "VNF"):
        return "souhaiter que"
    if lemma == "attendre" and pos in ("VRB", "VNF") and a != "attendant":
        return "attendre que"
    if a == "attendant" and b == "en":
        return "en attendant que"
    # conjunctions: only when nothing was skipped
    if n:
        return None
    if a == "pour":
        return "pour que"
    if a == "avant":
        return "avant que"
    if a == "après":
        return "après que"
    if a == "sans" and b != "sans":
        return "sans que"
    if a == "afin":
        return "afin que"
    if a == "moins" and b == "à":
        return "à moins que"
    if a == "condition" and b == "à":
        return "à condition que"
    if a == "ce" and b == "à":
        if c in ("jusqu'", "jusque"):
            return "jusqu'à ce que"
        if c in ("façon", "manière", "intérêt") or (j >= 2 and s[tok[j - 2]][2] in ("tenir", "attendre", "veiller")):
            return "à ce que"  # de façon à ce que, tenir à ce que, s'attendre à ce que
    if a == "sorte" and b == "en":
        return "faire en sorte que"
    if a == "pourvu":
        return "pourvu que"
    if a == "peur":
        return "avoir peur que"
    if a in ("content", "contente", "contents", "contentes", "heureux", "heureuse", "ravi", "ravie"):
        return "être content que"
    if a == "dommage":
        return "c'est dommage que"
    if a in ("étonnerait", "étonne", "étonnant", "étonnerais"):
        return "ça m'étonnerait que"
    if a == "doute" and b in ("je", "j'", "on") or a == "doutes":
        return "douter que"
    if a in ("possible", "impossible") and b != "plus":
        return "il est possible que"
    if a == "peut" and b == "se":
        return "il se peut que"
    if a == "normal" and b != "plus":
        return "c'est normal que"
    if a in ("important", "essentiel", "nécessaire", "indispensable", "urgent", "primordial"):
        return "il est important que"
    if a in ("suffit", "suffirait", "suffisait", "suffira"):
        return "il suffit que"
    return None


def find_verb(s, start):
    """First finite verb after a que at token index start-1, and its subject.

    Returns (None, None) when the clause doesn't look like subject + verb: no
    subject before the verb, a noun or preposition between a subject pronoun and
    the verb, or a change of subject pronoun (a restart: faut que je c'est...).
    """
    subj, clitic = None, False
    for i in range(start, min(start + 9, len(s))):
        t = s[i]
        form, pos = t[1].lower(), t[3]
        if pos == "VRB" or (pos in ("COO", "NOM") and form in ("soit", "sois", "aille", "fasse")
                            and i > start and s[i - 1][3] in ("CLS", "PRO")):
            if subj is None and i > start and s[i - 1][1].lower() == "t'":
                subj = "tu"
            return (i, subj) if subj else (None, None)
        if form in ("que", "qu'") and pos == "CSU" and subj is None:
            continue  # il faut que que je...
        if pos in STOP:
            return None, None
        if pos == "CLS" and form in SUBJ:
            if subj is None:
                subj, clitic = SUBJ[form], True
            elif SUBJ[form] != subj and form not in ("vous", "nous"):
                return None, None  # faut que tu c'est...: a restart
        elif clitic and pos not in ("CLI", "CLN", "ADN", "ADV", "INT"):
            return None, None
        elif pos == "PRO" and form in ("ça", "cela", "ce", "tout", "rien", "personne", "chacun"):
            subj = subj or "il"
        elif pos == "NOM" and subj is None:
            subj = "pl" if s[i - 1][1].lower() in PLURAL_DET else "il"
    return None, None


RESTART = set(FALLOIR) | {"faudrait", "fallait"}
COMPARATIVE = {"plus", "moins", "aussi", "si", "tellement", "autant", "peu", "trop"}


def skip(trig, s, k_tok, vi, words, k):
    """False positives that the trigger and verb patterns let through."""
    v = s[vi][1].lower()
    nxt = s[vi + 1][1].lower() if vi + 1 < len(s) else ""
    if v in RESTART or (trig.startswith("vouloir") and v in VOULOIR):
        return True  # il faut que il faut que...: the speaker starts again
    between = [t[1].lower() for t in s[k_tok + 1: vi]]
    if (v in ("est", "est-ce") and nxt in ("ce", "-ce")) or set(between) & {"est-ce", "-ce"}:
        return True  # qu'est-ce que
    if v.endswith(("ez", "ons")) and set(between) & {"vous", "nous"} and \
            not set(between[:1]) & {"vous", "nous"}:
        return True  # faut que je vous avez...: a restart with vous
    if s[k_tok][3] == "ADN" and s[k_tok + 1][3] != "CLS":
        return True  # restrictive que: je souhaite qu'une chose
    prev = [words[i] for i in range(max(0, k - 4), k)]
    if trig in ("il est important que", "il est possible que", "c'est normal que",
                "être content que") and set(prev[-3:]) & COMPARATIVE:
        return True  # plus important que (more important than)
    if trig.startswith("vouloir") and prev[-3:-1] in (["si", "tu"], ["si", "vous"]):
        return True  # si tu veux (discourse marker)
    return False


def main(root, out):
    rows = []
    for corpus, doc, path in documents(root):
        for s in sentences(path):
            words, tok = flatten(s)
            for k, wd in enumerate(words):
                if wd not in ("que", "qu'"):
                    continue
                # the que must end its token (à moins que is one token)
                if k + 1 < len(words) and tok[k + 1] == tok[k]:
                    continue
                trig = trigger(words, k, s, tok)
                if not trig:
                    continue
                vi, person = find_verb(s, tok[k] + 1)
                if vi is None or skip(trig, s, tok[k], vi, words, k):
                    continue
                v = s[vi]
                lemma, mood, counted = classify(v[1], v[2], person)
                lo = max(0, tok[k] - 5)
                rows.append({
                    "corpus": corpus, "doc": doc, "speaker": v[12], "start": v[10],
                    "trigger": trig, "group": GROUP.get(trig, trig.split(" (")[0]),
                    "person": person, "verb": v[1], "lemma": lemma, "mood": mood,
                    "counted": int(counted),
                    "context": " ".join(t[1] for t in s[lo: vi + 4]),
                })
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "tokens.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(len(rows), "trigger + verb;", sum(r["counted"] for r in rows), "counted")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

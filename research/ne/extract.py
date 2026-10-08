"""Find negated clauses in the spoken France part of CEFC-ORFEO and whether ne is written.

Usage: python extract.py CEFC_DIR OUT_DIR

CEFC_DIR is the unzipped cefc-no-audio.zip (one folder per subcorpus).
Writes OUT_DIR/negations.csv, one row per negated clause:

  post-verbal  a finite verb followed by pas, plus, jamais, rien, personne or
               que ("only"): je (ne) sais pas, j'(n')ai rien vu, j'(n')ai vu personne
  infinitive   pas, plus, jamais, rien in front of an infinitive, after a
               preposition: de (ne) pas venir, pour (ne) pas paraître
  subject      personne, rien, aucun as the subject: personne (n')est venu

ne counts as present when a ne (tag CLN) sits between the subject and the verb.
Rows are flagged n_ambig when a written n' can't be heard: the word before it
ends in an n that is said before a vowel (on, rien, aucun, personne, a noun in
-ne), so "on n'a" and "on a" sound the same.
"""
import collections, csv, os, re, sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from orfeo import documents, sentences, speakers

VOWEL = tuple("aeiouyhéèêëâàîïôûù")
FILLERS = {"euh", "hum", "ben", "bah"}
# adverbs that can stand between the verb and the negator: je sais vraiment pas
BETWEEN_ADV = {"vraiment", "même", "peut-être", "toujours", "encore", "absolument",
               "forcément", "trop", "plus", "donc", "pourtant", "certainement",
               "souvent", "jamais", "presque", "bien", "quand", "franchement"}
# plus is "no more" or "more": keep it only where the next word rules out "more"
PLUS_NEXT_POS = {"VPP", "VNF", "INT", "CLS", "CLN", "COO"}
PLUS_NEXT_FORM = {"rien", "jamais", "personne", "du", "trop", "là", "maintenant",
                  "aujourd'hui", "non", "hein", "quoi", "vraiment"}
SUBJ_NEG = {"personne", "rien", "aucun", "aucune", "nul"}
N_FINAL = {"on", "rien", "aucun", "personne", "un"}
# il faut, il s'agit (the tagger gives faut the lemma faillir); il y a is caught by its y
IMPERSONAL = {"faut", "fallait", "faudra", "faudrait", "faille", "agit", "agissait"}


def norm_subject(form):
    f = form.lower().lstrip("-").replace("-t-", "")
    return {"j'": "je", "j": "je", "t'": "tu", "t": "tu", "c'": "ce", "c": "ce"}.get(f, f)


def doc_meta(root, corpus, doc):
    path = os.path.join(root, corpus, doc + ".xml")
    meta = {"situation": "", "channel": ""}
    if os.path.exists(path):
        xml = open(path, encoding="utf-8").read()
        for key, field in (("type", "situation"), ("channel", "channel")):
            m = re.search(rf'catRef corresp="{key}" target="([^"]*)"', xml)
            if m:
                meta[field] = m.group(1)
    return meta


def clean(tok):
    return "~" not in tok[1]


ELIDE = {"je": "j'", "ce": "c'", "me": "m'", "te": "t'", "se": "s'", "le": "l'", "la": "l'"}


def surface(toks):
    """The words without ne, elided words joined: je (n') ai pas -> j'ai pas."""
    words = [t[1].lower() for t in toks]
    out = ""
    for i, w in enumerate(words):
        if w in ELIDE and i + 1 < len(words) and words[i + 1].startswith(VOWEL):
            w = ELIDE[w]
        out += w + ("" if w.endswith("'") else " ")
    return out.strip()


def find_verb(s, k):
    """Index of the finite verb that a post-verbal negator at k belongs to, or None."""
    neg = s[k][1].lower()
    j = k - 1
    while j >= 0 and k - j <= 3 and (s[j][1].lower() in FILLERS or
                                     (s[j][3] in ("ADV", "ADN") and s[j][1].lower() in BETWEEN_ADV)):
        j -= 1
    if j < 0:
        return None
    # ça sert à rien, je parle à personne, j'ai besoin de rien
    if neg in ("personne", "que", "qu'", "rien") and s[j][3] == "PRE" and s[j][1].lower() in ("à", "de", "d'"):
        j -= 1
    # j'ai vu personne, j'ai fait que ça
    if neg in ("personne", "que", "qu'") and j > 0 and s[j][3] == "VPP" and s[j - 1][3] == "VRB":
        j -= 1
    if j < 0 or s[j][3] != "VRB" or "-" in s[j][1] or not clean(s[j]):
        return None
    return j


def left_side(s, j):
    """What precedes the verb at j: (has_ne, clitic tokens, subject index or -1,
    subject class, subject form)."""
    i = j - 1
    has_ne, clitics = False, []
    while i >= 0 and s[i][3] in ("CLI", "CLN") and s[i][12] == s[j][12]:
        if s[i][3] == "CLN":
            has_ne = True
        else:
            clitics.insert(0, s[i])
        i -= 1
    none = (has_ne, clitics, -1, "none", "")
    while i >= 0 and j - i <= 6 and s[i][1].lower() in FILLERS:  # les gens euh n'ont pas
        i -= 1
    if i < 0 or s[i][12] != s[j][12]:
        return none
    t, f = s[i], s[i][1].lower()
    after_pre = i > 0 and s[i - 1][3] == "PRE"
    if t[3] == "CLS" and not f.startswith("-"):
        return has_ne, clitics, i, "pronoun", norm_subject(f)
    if t[3] == "PRQ" and f == "qui":
        return has_ne, clitics, i, "qui", "qui"
    if t[3] == "PRO" and not after_pre:
        return has_ne, clitics, i, "ça" if f in ("ça", "cela", "ceci") else "other pronoun", f
    # a noun right before the verb is its subject, except a name before a command
    # (Pierre, ne quittez pas)
    if t[3] in ("NOM", "NPR") and not s[j][1].lower().endswith("ez"):
        return has_ne, clitics, i, "noun", f
    if t[3] == "ADJ" and i > 0 and s[i - 1][3] == "NOM":
        return has_ne, clitics, i - 1, "noun", s[i - 1][1].lower()
    return none


def n_ambiguous(subj_form, subj_class, after):
    """True if a written n' between this subject and the word `after` couldn't be heard."""
    if not after.lower().startswith(VOWEL):
        return False
    if subj_form in N_FINAL:
        return True
    return subj_class == "noun" and subj_form.endswith("ne") and not subj_form.endswith("gne")


def subject_group(r):
    """The subject as reported: je, tu, on, il/elle, ... noun, none."""
    sc, sf = r["subject_class"], r["subject"]
    if r["kind"] == "subject":
        return "personne, rien, aucun"
    if sc == "pronoun":
        if sf == "il" and (r["clitics"].startswith("y") or r["verb"] in IMPERSONAL):
            return "il (il y a, il faut)"
        if sf == "on":
            return "on + vowel" if r["n_ambig"] else "on + consonant"
        if sf in ("je", "tu", "nous", "vous"):
            return sf
        return {"il": "il, elle", "elle": "il, elle", "ils": "ils, elles", "elles": "ils, elles",
                "ce": "ce (c'est)"}.get(sf, "other pronoun")
    if sc == "none":
        if r["clitics"].startswith("y") or r["verb"] in IMPERSONAL:
            return "no subject (y a, faut)"
        return "no subject (commands, cut-off clauses)"
    return sc


def main(root, out):
    rows = []
    stats = collections.Counter()
    for corpus, doc, path in documents(root):
        spk = speakers(root, corpus, doc)
        meta = doc_meta(root, corpus, doc)
        for s in sentences(path):
            seen = set()
            for k, t in enumerate(s):
                f = t[1].lower()
                if not clean(t):
                    continue
                kind = None
                nxt = s[k + 1] if k + 1 < len(s) else None
                # personne, rien heading their own clause are its subject: ..., personne (n')est venu
                heads_clause = nxt is not None and nxt[3] in ("CLN", "CLI", "VRB")
                post = ((f in ("pas", "plus", "jamais", "que", "qu'") and t[3] == "ADN") or
                        (f in ("rien", "personne") and t[3] == "PRO" and not heads_clause))
                if post:
                    if f == "pas" and nxt and nxt[1].lower() == "mal":  # pas mal: quite a lot
                        stats["left out: pas mal"] += 1
                        continue
                    if f == "plus":
                        later = [x[1].lower() for x in s[k + 1: k + 5]]
                        if (nxt and nxt[3] not in PLUS_NEXT_POS and nxt[1].lower() not in PLUS_NEXT_FORM) \
                                or "que" in later or "qu'" in later \
                                or (nxt and nxt[3] == "VPP" and s[k - 1][2] == "être"):
                            stats["left out: plus that could mean more"] += 1
                            continue
                    j = find_verb(s, k)
                    if j is not None and j not in seen and s[j][12] == t[12]:
                        kind, verb_i = "post-verbal", j
                        seen.add(j)
                    elif f in ("pas", "plus", "jamais", "rien") and nxt and nxt[3] == "VNF":
                        # after a preposition: de (ne) pas venir, pour (ne) pas paraître
                        b = k - 1 - (k > 0 and s[k - 1][3] == "CLN")
                        if b >= 0 and s[b][3] == "PRE" and s[b][1].lower() != "sans":
                            kind, verb_i = "infinitive", k + 1
                elif f in SUBJ_NEG and t[3] in ("PRO", "NOM", "DET") and (k == 0 or s[k - 1][3] not in
                                                                    ("PRE", "DET", "CLI", "CLS", "CLN", "VRB", "VPP", "VNF", "ADN")):
                    j = k + 1
                    if t[3] == "DET":  # aucun élève ne
                        j = j + 1 if j < len(s) and s[j][3] == "NOM" else len(s)
                    while j < len(s) and s[j][3] in ("CLI", "CLN"):
                        j += 1
                    if j < len(s) and s[j][3] == "VRB" and "-" not in s[j][1] and \
                            s[j][12] == t[12] and clean(s[j]) and j not in seen:
                        kind, verb_i = "subject", j
                        seen.add(j)  # personne (n')a rien dit: count the clause once, here
                if not kind:
                    continue

                if kind == "infinitive":
                    has_ne = k > 0 and s[k - 1][3] == "CLN"
                    clitics, subj_i, sclass, sform = [], -1, "none", ""
                    first = k - 1 if has_ne else k
                else:
                    has_ne, clitics, subj_i, sclass, sform = left_side(s, verb_i)
                    if kind == "subject":
                        subj_i, sclass, sform = k, "negative word", f
                    first = subj_i if subj_i >= 0 else verb_i - len(clitics) - has_ne
                v = s[verb_i]
                after_subj = (clitics[0] if clitics else v)[1]
                who = spk.get(v[12], {})
                last = max(k, verb_i)
                if kind == "subject":
                    phrase = surface([t] + clitics + [v])
                elif kind == "infinitive":
                    phrase = surface([t, v])
                else:
                    phrase = surface(([s[subj_i]] if subj_i >= 0 else []) + clitics + [v, t])
                row = {
                    "corpus": corpus, "doc": doc, "situation": meta["situation"],
                    "channel": meta["channel"], "speaker": v[12],
                    "sex": who.get("sex", ""), "age": who.get("age", ""),
                    "education": who.get("education", ""),
                    "occupation": who.get("occupation", ""),
                    "first_language": who.get("first_language", ""),
                    "kind": kind, "negator": "que" if f == "qu'" else f,
                    "subject_class": sclass, "subject": sform,
                    "clitics": " ".join(c[1].lower() for c in clitics),
                    "verb": v[1].lower(), "lemma": v[2], "phrase": phrase,
                    "ne": int(has_ne),
                    "n_ambig": int(kind != "infinitive" and n_ambiguous(sform, sclass, after_subj)),
                    "context": " ".join(x[1] for x in s[max(0, first - 4): last + 4]),
                    "time": v[10],
                }
                row["subject_group"] = subject_group(row)
                rows.append(row)
    os.makedirs(out, exist_ok=True)
    with open(os.path.join(out, "negations.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    for k, n in stats.items():
        print(k, n)
    for kind in ("post-verbal", "infinitive", "subject"):
        sub = [r for r in rows if r["kind"] == kind]
        ne = sum(r["ne"] for r in sub)
        print(f"{kind}: {len(sub)} negations, ne written in {ne} ({100 * ne / len(sub):.1f}%)")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

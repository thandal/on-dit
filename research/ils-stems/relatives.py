"""Count plural antecedent + qui + two-stem or core verb in the spoken France part
of CEFC-ORFEO, by whether the transcript shows the plural or the singular form.

Usage: python relatives.py CEFC_DIR

Antecedents counted: ceux qui, celles qui, eux qui, and plural determiner + noun
+ qui, except where the noun phrase hangs off something singular before it
(le cahier des charges qui, un de mes amis qui, une des raisons qui).
Spoken qui and qu'il sound the same ("ki"), so some hits are really qu'il.
"""
import collections, glob, os, sys

from extract import SPOKEN_FRANCE, sentences
from verbs import ALL, CORE, FORMS

PLURAL_DET = {"les", "des", "ces", "mes", "tes", "ses", "nos", "vos", "leurs"}
PLURAL_PRO = {"ceux", "celles", "eux", "elles"}
SINGULAR_HEAD = {"un", "une", "l'un", "l'une", "chacun", "chacune", "aucun", "aucune"}


def plural_antecedent(s, i):
    """Is the word before qui (s[i]) a plural pronoun or plural noun phrase?"""
    if s[i - 1][1].lower() in PLURAL_PRO:
        return True
    if i < 2 or s[i - 1][3] != "NOM" or s[i - 2][1].lower() not in PLURAL_DET:
        return False
    before = [t[1].lower() for t in s[max(0, i - 4): i - 2]]
    if s[i - 2][1].lower() == "des" and i >= 3 and (
            s[i - 3][3] in ("NOM", "NUM", "ADJ") or s[i - 3][1].lower() in SINGULAR_HEAD):
        return False  # le cahier des charges, une des raisons
    if before and before[-1] in ("de", "d'") and set(before) & SINGULAR_HEAD:
        return False  # un de mes amis
    return True


def main(root):
    n = collections.Counter()
    examples = collections.defaultdict(list)
    for corpus in SPOKEN_FRANCE:
        for path in sorted(glob.glob(os.path.join(root, corpus, "*.orfeo"))):
            for s in sentences(path):
                for i in range(1, len(s) - 1):
                    if s[i][1].lower() != "qui":
                        continue
                    if not plural_antecedent(s, i):
                        continue
                    j = i + 1
                    while j < len(s) and s[j][3] in ("CLN", "CLI"):
                        j += 1
                    if j >= len(s) or s[j][3] != "VRB":
                        continue
                    for lemma, written in FORMS.get(s[j][1].lower(), []):
                        if len(FORMS[s[j][1].lower()]) > 1 and s[j][2] != lemma:
                            continue
                        grp = "core" if lemma in CORE else "two-stem"
                        n[(grp, written)] += 1
                        if written == "short":
                            examples[grp].append(
                                f"{corpus}/{os.path.basename(path)[:-6]}: "
                                + " ".join(t[1] for t in s[max(0, i - 4): j + 3]))
    for grp in ("two-stem", "core"):
        lo, sh = n[(grp, "long")], n[(grp, "short")]
        print(f"{grp}: plural antecedent + qui + plural form {lo}, + singular form {sh}"
              f" ({100 * sh / max(lo + sh, 1):.1f}% singular)")
        for e in examples[grp]:
            print("   ", e)


if __name__ == "__main__":
    main(sys.argv[1])

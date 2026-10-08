"""Count how the transcripts spell the participle, by context, after the hand checks.

Usage: python3 transcripts.py TOKENS_CSV HAND_CODED_CSV OUT_DIR

TOKENS_CSV comes from extract.py. HAND_CODED_CSV records the decisions made by
reading each context (results/hand_coded.csv): which avoir cases really have a
feminine direct object before the verb, and which être cases are false hits.
Writes OUT_DIR/transcript_counts.csv and prints the table.
"""
import collections, csv, os, sys

GROUPS = [
    # (label, standard form, test on a token row and its hand coding)
    ("elle(s) + être", "f",
     lambda r, c: r["context_type"] == "etre_f" and (not c or c["keep"] == "yes")),
    ("feminine noun + être", "f",
     lambda r, c: r["context_type"] == "etre_np" and r["gender"] == "f" and (not c or c["keep"] == "yes")),
    ("elle(s) + se + être, se the object", "f",
     lambda r, c: r["context_type"] == "refl_f" and c and c["keep"] == "yes"),
    ("feminine noun + que + avoir", "f",
     lambda r, c: r["context_type"] == "rel" and c and c["keep"] == "yes"),
    ("l' / les (feminine) + avoir", "f",
     lambda r, c: r["context_type"] == "clitic" and c and c["keep"] == "yes"),
    ("control: avoir + participle + object", "m",
     lambda r, c: r["context_type"] == "after"),
    ("control: ce que + avoir", "m",
     lambda r, c: r["context_type"] == "rel_ce"),
    ("control: masculine noun + que + avoir", "m",
     lambda r, c: r["context_type"] == "rel" and r["gender"] == "m" and not c),
    ("control: il(s) + être", "m",
     lambda r, c: r["context_type"] == "etre_m"),
]


def main(tokens_csv, coded_csv, out):
    rows = list(csv.DictReader(open(tokens_csv, encoding="utf-8")))
    coded = {(r["doc"], r["start"]): r for r in csv.DictReader(open(coded_csv, encoding="utf-8"))}
    n = collections.Counter()
    print(f"{'context':<40}{'standard':>9}{'fem':>6}{'masc':>6}{'% fem':>7}")
    for label, std, test in GROUPS:
        sub = [r for r in rows if test(r, coded.get((r["doc"], r["start"])))]
        for r in sub:
            n[(label, r["participle"], r["written"])] += 1
        fem = sum(r["written"] == "f" for r in sub)
        print(f"{label:<40}{std:>9}{fem:>6}{len(sub) - fem:>6}{100 * fem / len(sub):>6.0f}%")
    with open(os.path.join(out, "transcript_counts.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["context", "standard", "participle", "written_fem", "written_masc"])
        for label, std, _ in GROUPS:
            parts = sorted({p for (l, p, _) in n if l == label},
                           key=lambda p: -(n[(label, p, "f")] + n[(label, p, "m")]))
            for p in parts:
                w.writerow([label, std, p, n[(label, p, "f")], n[(label, p, "m")]])


if __name__ == "__main__":
    main(*sys.argv[1:])

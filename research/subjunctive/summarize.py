"""Summarize extract.py output, using the hand check of the indicative hits.

Usage: python summarize.py TOKENS_CSV RESULTS_DIR

Every counted token whose verb isn't subjunctive was read by hand
(RESULTS_DIR/indicative_checked.csv):
    ind  a real indicative after the trigger
    ait  est / es / ai written for ait / aies, which sound the same: a subjunctive
    not  not a trigger + verb (a restart, a relative que, a cleft...)
A token missing from that file is counted as indicative and flagged.

Writes by_trigger.csv, by_verb.csv, by_corpus.csv and combos.csv to RESULTS_DIR.
"""
import collections, csv, os, sys

SIX = ("être", "avoir", "aller", "faire", "pouvoir", "savoir")


def load(tokens_csv, results):
    checked = {(r["doc"], r["start"], r["verb"]): r["check"] for r in
               csv.DictReader(open(os.path.join(results, "indicative_checked.csv"), encoding="utf-8"))}
    rows, unchecked = [], 0
    for r in csv.DictReader(open(tokens_csv, encoding="utf-8")):
        if r["counted"] != "1":
            r["result"] = "same" if r["mood"] == "same" else "excluded"
        elif r["mood"] == "subj":
            r["result"] = "subj"
        else:
            check = checked.get((r["doc"], r["start"], r["verb"]))
            if check is None:
                unchecked += 1
                check = "ind"
            r["result"] = {"ind": "ind", "ait": "subj", "not": "dropped"}[check]
            if check == "ait":
                r["lemma"] = "avoir"
        rows.append(r)
    return rows, unchecked


def table(rows, key, path, extra=()):
    n = collections.Counter((key(r), r["result"]) for r in rows)
    keys = sorted({k for k, _ in n}, key=lambda k: -(n[(k, "subj")] + n[(k, "ind")]))
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["key", "subjunctive", "indicative", "pct_subjunctive", "same_sound"] + list(extra))
        for k in keys:
            s, i = n[(k, "subj")], n[(k, "ind")]
            if s + i:
                w.writerow([k, s, i, round(100 * s / (s + i), 1), n[(k, "same")]])
    return n, keys


def main(tokens_csv, results):
    rows, unchecked = load(tokens_csv, results)
    res = collections.Counter(r["result"] for r in rows)
    s, i = res["subj"], res["ind"]
    print(f"trigger + verb: {len(rows)}; same sound in both moods: {res['same']}; "
          f"set aside (j'ai/j'aie, ils + two-stem): {res['excluded']}; dropped by hand: {res['dropped']}")
    print(f"counted: {s + i}, subjunctive {s}, indicative {i} ({100 * s / (s + i):.1f}% subjunctive)")
    if unchecked:
        print(f"warning: {unchecked} indicative hits not in indicative_checked.csv")
    print("speakers with an indicative:", len({r["speaker"] for r in rows if r["result"] == "ind"}),
          "of", len({r["speaker"] for r in rows if r["result"] in ("subj", "ind")}))

    n, keys = table(rows, lambda r: r["trigger"], os.path.join(results, "by_trigger.csv"))
    print(f"\n{'trigger':<24}{'subj':>6}{'ind':>6}{'% subj':>8}")
    for k in keys:
        a, b = n[(k, "subj")], n[(k, "ind")]
        if a + b:
            print(f"{k:<24}{a:>6}{b:>6}{100 * a / (a + b):>8.0f}")

    n, keys = table(rows, lambda r: r["lemma"], os.path.join(results, "by_verb.csv"))
    print(f"\n{'verb':<16}{'subj':>6}{'ind':>6}")
    for k in keys[:20]:
        print(f"{k:<16}{n[(k, 'subj')]:>6}{n[(k, 'ind')]:>6}")
    six = sum(n[(k, "subj")] for k in SIX)
    print(f"the six of 6.5: {six} of {s} subjunctives ({100 * six / s:.0f}%)")

    n, keys = table(rows, lambda r: r["corpus"], os.path.join(results, "by_corpus.csv"))
    print()
    for k in keys:
        a, b = n[(k, "subj")], n[(k, "ind")]
        print(f"{k:<22}{a:>6}{b:>6}{100 * a / (a + b):>8.0f}")

    # which subjunctives a learner needs: trigger + verb, subjunctive tokens only
    combos = collections.Counter((r["group"], r["lemma"]) for r in rows if r["result"] == "subj")
    forms = collections.Counter()
    for r in rows:
        if r["result"] == "subj":
            ctx = r["context"].lower().split()
            y = " y" if f"y {r['verb'].lower()}" in " ".join(ctx) else ""
            forms[f"{r['person']}{y} {r['verb'].lower()}"] += 1
    with open(os.path.join(results, "combos.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["trigger", "verb", "subjunctive_tokens", "pct_of_all_subjunctives"])
        for (t, l), c in combos.most_common():
            w.writerow([t, l, c, round(100 * c / s, 1)])
    print("\ncommonest trigger + verb:")
    for (t, l), c in combos.most_common(15):
        print(f"  {t} + {l}: {c}")
    print("commonest subject + form:", forms.most_common(15))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

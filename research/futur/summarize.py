"""Summarize extract.py output: futur simple against futur proche.

Usage: python summarize.py TOKENS_CSV RESULTS_DIR

Left out of every comparison: on va dire ("let's say", a discourse marker, not a
future), the futur antérieur (il aura fini), which has no futur proche partner, and
DECODA's call-centre phrase (name) va vous répondre.
Writes by_verb.csv, by_context.csv and fixed.csv to RESULTS_DIR.
"""
import collections, csv, os, sys

NWORDS = {"jamais", "rien", "plus", "personne", "point", "guère"}


def on_va_dire(r):
    return r["type"] == "proche" and r["verb"] == "dire" and r["subject"] == "on" \
        and not r["between"]


def hold_message(r):
    """DECODA's call-centre phrase: (name) va vous répondre, "(name) will answer you"."""
    return r["corpus"] == "decoda" and r["verb"] == "répondre" and r["between"] == "vous"


def pct(fs, fp):
    return round(100 * fs / (fs + fp), 1) if fs + fp else ""


def fixed(r):
    """Name of the fixed expression r belongs to (both members of a pair), or None."""
    subj, v, t, before, between = r["subject"], r["verb"], r["type"], r["before"], r["between"]
    y = before.endswith(" y") if t == "simple" else between == "y"
    if v == "voir" and subj == "on" and not between:
        return "on verra / on va voir"
    if v == "voir" and subj in ("tu", "vous") and not between:
        return "tu verras, vous verrez / tu vas voir, vous allez voir"
    if v == "être" and subj in ("ce", "ça", "c'") and not between:
        return "ce sera / ça va être"
    if v == "avoir" and subj == "il" and y:
        return "il y aura / il va y avoir"
    if v == "falloir":
        return "il faudra / il va falloir"
    if v == "aller" and subj == "ça" and not between:
        return "ça ira / ça va aller"
    if v == "reparler" and subj == "on":
        return "on en reparlera / on va en reparler"
    return None


def main(tokens_csv, results):
    rows = list(csv.DictReader(open(tokens_csv, encoding="utf-8")))
    dire = [r for r in rows if on_va_dire(r)]
    aux = [r for r in rows if r["aux"] == "1"]
    hold = [r for r in rows if hold_message(r)]
    rows = [r for r in rows if not on_va_dire(r) and r["aux"] != "1" and not hold_message(r)]
    n = collections.Counter(r["type"] for r in rows)
    fs, fp = n["simple"], n["proche"]
    print(f"left out: on va dire {len(dire)}, futur antérieur {len(aux)}, "
          f"va vous répondre (DECODA) {len(hold)}")
    print(f"futur simple {fs}, futur proche {fp}: {pct(fs, fp)}% futur simple")

    # by verb
    v = collections.Counter((r["verb"], r["type"]) for r in rows)
    verbs = sorted({k for k, _ in v}, key=lambda k: -(v[(k, "simple")] + v[(k, "proche")]))
    with open(os.path.join(results, "by_verb.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["verb", "futur_simple", "futur_proche", "pct_simple", "pct_of_all_futur_simple"])
        for k in verbs:
            a, b = v[(k, "simple")], v[(k, "proche")]
            if a + b >= 20:
                w.writerow([k, a, b, pct(a, b), round(100 * a / fs, 1)])
    print(f"\n{'verb':<12}{'simple':>8}{'proche':>8}{'% simple':>10}")
    for k in verbs[:25]:
        print(f"{k:<12}{v[(k, 'simple')]:>8}{v[(k, 'proche')]:>8}{pct(v[(k, 'simple')], v[(k, 'proche')]):>10}")
    top = sorted(verbs, key=lambda k: -v[(k, "simple")])[:8]
    share = sum(v[(k, "simple")] for k in top)
    print(f"top 8 verbs of the futur simple {top}: {share} of {fs} ({100 * share / fs:.0f}%)")
    print("verbs with a futur simple:", sum(1 for k in verbs if v[(k, "simple")]))

    # contexts
    def polarity(r):
        g = r["negation"]
        return "affirmative" if not g else "pas" if g == "pas" else \
            "ne alone" if g == "ne" else "other negation word"
    groups = {
        "all": lambda r: "all",
        "polarity": polarity,
        "negated": lambda r: "negated" if r["negation"] else "affirmative",
        "after quand, lorsque, dès que": lambda r: "yes" if r["after_quand"] == "1" else "no",
        "person": lambda r: r["person"],
        "situation": lambda r: r["situation"] or "unknown",
        "corpus": lambda r: r["corpus"],
        "without être, avoir, falloir: negated": lambda r: (
            None if r["verb"] in ("être", "avoir", "falloir")
            else "negated" if r["negation"] else "affirmative"),
        "without je (je -rai / -rais)": lambda r: (
            None if r["person"] == "je" else "negated" if r["negation"] else "affirmative"),
    }
    out = []
    for name, f in groups.items():
        c = collections.Counter((f(r), r["type"]) for r in rows)
        for val in sorted({k for k, _ in c if k is not None}, key=str):
            a, b = c[(val, "simple")], c[(val, "proche")]
            out.append([name, val, a, b, pct(a, b)])
    with open(os.path.join(results, "by_context.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["factor", "value", "futur_simple", "futur_proche", "pct_simple"])
        w.writerows(out)
    print()
    for row in out:
        print(f"{row[0][:38]:<38} {row[1]:<22}{row[2]:>7}{row[3]:>7}{row[4]:>7}")

    # within each common verb, negated against affirmative
    print("\nwithin verb: % futur simple, affirmative / negated")
    for k in verbs[:15]:
        c = collections.Counter((bool(r["negation"]), r["type"]) for r in rows if r["verb"] == k)
        print(f"  {k:<10} {pct(c[(False, 'simple')], c[(False, 'proche')])!s:>6} "
              f"(n={c[(False, 'simple')] + c[(False, 'proche')]})  "
              f"{pct(c[(True, 'simple')], c[(True, 'proche')])!s:>6} "
              f"(n={c[(True, 'simple')] + c[(True, 'proche')]})")

    # fixed expressions
    fx = collections.Counter((fixed(r), r["type"]) for r in rows)
    names = sorted({k for k, _ in fx if k}, key=lambda k: -(fx[(k, "simple")] + fx[(k, "proche")]))
    with open(os.path.join(results, "fixed.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["expression", "futur_simple", "futur_proche", "pct_simple"])
        w.writerow(["on va dire (discourse marker, left out above)", 0, len(dire), 0])
        for k in names:
            w.writerow([k, fx[(k, "simple")], fx[(k, "proche")], pct(fx[(k, "simple")], fx[(k, "proche")])])
    print("\nfixed expressions (simple / proche):")
    for k in names:
        print(f"  {k:<55}{fx[(k, 'simple')]:>6}{fx[(k, 'proche')]:>6}")
    rest = collections.Counter(r["type"] for r in rows if not fixed(r))
    print(f"everything else: {rest['simple']} / {rest['proche']} "
          f"({pct(rest['simple'], rest['proche'])}% futur simple)")
    forms = collections.Counter(f"{r['subject']} {r['before'].split()[-1] + ' ' if r['before'].endswith(' y') else ''}{r['form'].lower()}"
                                for r in rows if r["type"] == "simple")
    print("commonest futur simple forms:", forms.most_common(20))


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

"""Tables of how often ne is written, from extract.py's negations.csv.

Usage: python summarize.py NEGATIONS_CSV OUT_DIR

Unless a table says otherwise it counts post-verbal negations (je sais pas,
j'ai rien vu...) and leaves out the n_ambig ones, where a written n' couldn't
be heard (on n'a / on a). Writes one CSV per table to OUT_DIR and prints them.
"""
import collections, csv, os, statistics, sys

csv.field_size_limit(10 ** 8)

SETTINGS = ["everyday conversation", "interviews", "work meetings", "service encounters",
            "phone calls to a help line", "other monologues", "radio and TV",
            "public speaking", "storytelling performances"]
AGES = ["0-15", "16-20", "21-60", "61+"]
EDUCATION = {"primaire": "primary school", "collège": "lower secondary (collège)",
             "lycée": "upper secondary (lycée)", "études supérieures": "higher education",
             "Niveau d'études Supérieur": "higher education"}


def setting(r):
    c, t, ch = r["corpus"], r["situation"], r["channel"]
    if c == "decoda":
        return "phone calls to a help line"
    if ch in ("tv", "radio") or t == "médias oraux":
        return "radio and TV"
    if t in ("cours", "discours", "présentation publique") or (ch == "en_public" and t != "narration"):
        return "public speaking"
    if t == "narration" and ch == "en_public":
        return "storytelling performances"
    if t == "entretien":
        return "interviews"
    if t == "réunion":
        return "work meetings"
    if c == "fleuron" or t in ("consultation", "transaction"):
        return "service encounters"
    if t in ("conversation", "repas") or c == "clapi":
        return "everyday conversation"
    return "other monologues"


def table(rows, key, order=None, min_n=1, by_speaker=False):
    """Share of negations with ne written, per group. With by_speaker, also the
    number of speakers with 10+ negations in the group and their median rate, so
    one talkative speaker can't carry a group."""
    n, ne = collections.Counter(), collections.Counter()
    spk = collections.defaultdict(lambda: collections.defaultdict(list))
    for r in rows:
        k = key(r)
        if k is None:
            continue
        n[k] += 1
        ne[k] += r["ne"]
        spk[k][(r["corpus"], r["doc"], r["speaker"])].append(r["ne"])
    keys = order if order else sorted(n, key=lambda k: -n[k])
    out = []
    for k in keys:
        if n[k] < min_n:
            continue
        row = {"group": k, "negations": n[k], "ne_written": ne[k], "pct": round(100 * ne[k] / n[k], 1)}
        if by_speaker:
            rates = [100 * sum(v) / len(v) for v in spk[k].values() if len(v) >= 10]
            row["speakers_10plus"] = len(rates)
            row["median_speaker_pct"] = round(statistics.median(rates), 1) if rates else ""
        out.append(row)
    return out


def write(out, name, rows, title):
    with open(os.path.join(out, name), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"\n{title}  ({name})")
    for r in rows:
        print("  " + "  ".join(str(v) for v in r.values()))


def main(neg_csv, out):
    os.makedirs(out, exist_ok=True)
    allrows = list(csv.DictReader(open(neg_csv, encoding="utf-8")))
    for r in allrows:
        r["ne"], r["n_ambig"] = int(r["ne"]), int(r["n_ambig"])
        r["setting"] = setting(r)
    post = [r for r in allrows if r["kind"] == "post-verbal"]
    main_rows = [r for r in post if not r["n_ambig"]]
    # conversation and interviews, leaving out the researchers who ran the recordings
    # (one interviewer alone has 1,200 negations, 44% with ne)
    private = [r for r in main_rows if r["setting"] in ("everyday conversation", "interviews")
               and "chercheur" not in r["occupation"]]

    overview = []
    for name, sub in (("post-verbal, n' audible", main_rows),
                      ("post-verbal, n' inaudible (on n'a...)", [r for r in post if r["n_ambig"]]),
                      ("post-verbal, everyday conversation", [r for r in main_rows if r["setting"] == "everyday conversation"]),
                      ("post-verbal, conversation + interviews, researchers left out", private),
                      ("post-verbal, conversation + interviews, researchers only",
                       [r for r in main_rows if r["setting"] in ("everyday conversation", "interviews")
                        and "chercheur" in r["occupation"]]),
                      ("before an infinitive (de ne pas venir)", [r for r in allrows if r["kind"] == "infinitive"]),
                      ("personne / rien / aucun as subject, n' audible",
                       [r for r in allrows if r["kind"] == "subject" and not r["n_ambig"]])):
        k = sum(r["ne"] for r in sub)
        overview.append({"group": name, "negations": len(sub), "ne_written": k,
                         "pct": round(100 * k / len(sub), 1)})
    write(out, "overview.csv", overview, "Overview")

    write(out, "by_setting.csv", table(main_rows, lambda r: r["setting"], SETTINGS, by_speaker=True),
          "By setting")
    write(out, "by_corpus_situation.csv",
          table(main_rows, lambda r: f"{r['corpus']} / {r['situation'] or '-'} / {r['channel'] or '-'}", min_n=20),
          "By corpus / situation / channel")
    subj_order = ["je", "tu", "on + consonant", "il, elle", "nous", "vous", "ils, elles",
                  "ce (c'est)", "ça", "il (il y a, il faut)", "qui", "noun", "other pronoun",
                  "no subject (commands, cut-off clauses)", "no subject (y a, faut)"]
    write(out, "by_subject.csv", table(main_rows, lambda r: r["subject_group"], subj_order),
          "By subject, all settings")
    write(out, "by_subject_private.csv", table(private, lambda r: r["subject_group"], subj_order),
          "By subject, conversation + interviews")
    write(out, "by_negator.csv", table(private, lambda r: r["negator"]), "By negator, conversation + interviews")

    # age and education, kept to conversation + interviews so the setting doesn't drive them
    write(out, "by_age.csv", table(private, lambda r: r["age"] if r["age"] in AGES else None, AGES, by_speaker=True),
          "By age band, conversation + interviews")
    write(out, "by_education.csv",
          table(private, lambda r: EDUCATION.get(r["education"]),
                ["primary school", "lower secondary (collège)", "upper secondary (lycée)", "higher education"],
                by_speaker=True),
          "By education, conversation + interviews")
    write(out, "by_age_education.csv",
          table(private, lambda r: f"{r['age']} / {EDUCATION[r['education']]}"
                if r["age"] in AGES and r["education"] in EDUCATION else None, min_n=30, by_speaker=True),
          "By age and education, conversation + interviews")
    write(out, "by_sex.csv", table(private, lambda r: r["sex"] if r["sex"] in ("M", "F") else None, by_speaker=True),
          "By sex, conversation + interviews")

    # fixed phrases: the commonest subject + verb + negator combinations
    every = {r["group"]: r for r in table(main_rows, lambda r: r["phrase"])}
    phrases = []
    for r in table(private, lambda r: r["phrase"])[:30]:
        a = every[r["group"]]
        phrases.append({"phrase": r["group"], "conv_interviews_n": r["negations"],
                        "conv_interviews_pct": r["pct"], "all_n": a["negations"], "all_pct": a["pct"]})
    write(out, "by_phrase.csv", phrases, "Commonest phrases, conversation + interviews, and everywhere")

    # how individual speakers behave, conversation + interviews
    per = collections.defaultdict(list)
    for r in private:
        per[(r["corpus"], r["doc"], r["speaker"])].append(r["ne"])
    bands = [("0%", 0, 0), ("under 10%", 1e-9, 10), ("10-25%", 10, 25), ("25-50%", 25, 50),
             ("over 50%", 50, 101)]
    spk = [100 * sum(v) / len(v) for v in per.values() if len(v) >= 20]
    dist = []
    for name, lo, hi in bands:
        c = sum(1 for p in spk if (p == 0 if hi == 0 else lo <= p < hi))
        dist.append({"ne_rate": name, "speakers": c, "pct": round(100 * c / len(spk), 1)})
    write(out, "speakers.csv", dist, f"Speakers with 20+ negations ({len(spk)}), conversation + interviews")

    # the n' that can't be heard: on + vowel against on + consonant, per corpus
    amb = []
    for corpus in sorted({r["corpus"] for r in post}):
        sub = [r for r in post if r["corpus"] == corpus]
        row = {"corpus": corpus}
        for name, grp in (("on_consonant", "on + consonant"), ("on_vowel", "on + vowel")):
            g = [r for r in sub if r["subject_group"] == grp]
            row[name + "_n"] = len(g)
            row[name + "_pct"] = round(100 * sum(r["ne"] for r in g) / len(g), 1) if g else ""
        amb.append(row)
    write(out, "on_vowel.csv", amb, "on + consonant against on + vowel (n' inaudible), per corpus")


if __name__ == "__main__":
    main(*sys.argv[1:])

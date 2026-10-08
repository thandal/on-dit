"""Summarize score_audio.py output.

Usage: python summarize.py SCORES_CSV OUT_DIR

For each set, at several recognition-quality cut-offs, the share of clips where
the short stem fits the audio better (score < 0). Writes OUT_DIR/audio_summary.csv
and OUT_DIR/listen.csv: clean plural clips where the short stem fits best, to
check by ear.
"""
import csv, os, statistics, sys

CUTOFFS = (1.0, 0.4, 0.3, 0.2)  # max phone error rate of the recognizer on the window


def label(r):
    if r["set"] == "pl":
        return "ils, written long" if r["written"] == "long" else "ils, written short"
    return {"sg": "il (short only)", "control": "control (consonant said)"}[r["set"]]


def main(scores_csv, out):
    rows = [r for r in csv.DictReader(open(scores_csv, encoding="utf-8"))
            if r["same_consonant"] == "False"]
    for r in rows:
        r["score"], r["per"] = float(r["score"]), float(r["per"])
    out_rows = []
    print(f"{'set':<26}{'max PER':>8}{'clips':>7}{'short fits better':>19}{'median score':>14}")
    for name in ("ils, written long", "ils, written short", "il (short only)",
                 "control (consonant said)"):
        for cut in CUTOFFS:
            sub = [r for r in rows if label(r) == name and r["per"] <= cut]
            if not sub:
                continue
            short = sum(r["score"] < 0 for r in sub)
            med = statistics.median(r["score"] for r in sub)
            print(f"{name:<26}{cut:>8}{len(sub):>7}{short:>8} ({100 * short / len(sub):4.1f}%)"
                  f"{med:>14.1f}")
            out_rows.append({"set": name, "max_per": cut, "clips": len(sub),
                             "short_fits_better": short,
                             "pct": round(100 * short / len(sub), 1), "median_score": med})
    with open(os.path.join(out, "audio_summary.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out_rows[0]))
        w.writeheader()
        w.writerows(out_rows)

    listen = sorted((r for r in rows if r["set"] == "pl" and r["per"] <= 0.3 and r["score"] < 0),
                    key=lambda r: r["score"])
    keys = ["corpus", "doc", "speaker", "lemma", "written", "win_words", "win_start",
            "win_end", "hyp_long", "hyp_short", "heard", "per", "score"]
    with open(os.path.join(out, "listen.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in listen:
            w.writerow({k: r[k] for k in keys})
    print(f"{len(listen)} clean ils clips where the short stem fits better: {out}/listen.csv")


if __name__ == "__main__":
    main(*sys.argv[1:])

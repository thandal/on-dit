"""Build the blind listening test from score_audio.py output.

Usage: python listen_set.py SCORES_CSV CLIP_DIR OUT_DIR

Picks clean clips (PER <= 0.3, next word not starting with the stem consonant):
  flagged   every ils/elles clip where model 1 prefers the short stem
  plural    40 ils/elles clips where it prefers the long stem
  il        15 il/elle/on + two-stem verb (only the short stem is possible)
  control   15 il/elle/on + one-form verb (the consonant is always said)
shuffles them under neutral ids, and writes
  OUT_DIR/clips/<id>.mp3   the audio, for publishing with the page
  OUT_DIR/items.json       what the page shows: no set, no subject, no verb form
  results/listen_key.csv   which set each id belongs to (kept out of the page)
"""
import csv, json, os, random, subprocess, sys

from score_audio import TWO_STEM, clip_path, word_ipa

SUBJECTS = {"ils", "elles", "il", "elle", "on"}


def pick(rows):
    rng = random.Random(7)
    clean = [r for r in rows if r["same_consonant"] == "False" and float(r["per"]) <= 0.3]
    pl = [r for r in clean if r["set"] == "pl"]
    flagged = [r for r in pl if float(r["score"]) < 0]
    plural = rng.sample([r for r in pl if r["written"] == "long" and float(r["score"]) >= 0], 40)
    il = rng.sample([r for r in clean if r["set"] == "sg"], 15)
    control = rng.sample([r for r in clean if r["set"] == "control"], 15)
    chosen = ([("flagged", r) for r in flagged] + [("plural", r) for r in plural]
              + [("il", r) for r in il] + [("control", r) for r in control])
    rng.shuffle(chosen)
    return chosen


def context(r):
    """The window with the subject, its clitics and the verb blanked out."""
    words = [w.replace("-~", "-").replace("~", "") for w in r["win_words"].split()]
    v = int(r["win_verb"])
    # the subject is the last subject pronoun before the verb (qu'ils is split as qu' ils)
    s = max([i for i in range(v) if words[i].lower() in SUBJECTS], default=v)
    before = " ".join(words[:s]).replace("' ", "'")
    after = " ".join(words[v + 1:]).replace("' ", "'")
    return before, after


def options(r):
    if r["set"] == "control":
        long_ = word_ipa(r["verb"])
        return ({"ipa": long_[:-1], "hint": f"{r['verb']} without its last sound"},
                {"ipa": long_, "hint": f"like {r['verb']}"})
    long_form, short_form = TWO_STEM[r["lemma"]][0], TWO_STEM[r["lemma"]][1].split()[0]
    return ({"ipa": word_ipa(short_form), "hint": f"like {short_form}"},
            {"ipa": word_ipa(long_form), "hint": f"like {long_form}"})


def main(scores_csv, clip_dir, out):
    rows = list(csv.DictReader(open(scores_csv, encoding="utf-8")))
    os.makedirs(os.path.join(out, "clips"), exist_ok=True)
    items, key = [], []
    for n, (group, r) in enumerate(pick(rows), 1):
        cid = f"c{n:03d}"
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", clip_path(clip_dir, r),
                        "-ac", "1", "-b:a", "48k", os.path.join(out, "clips", cid + ".mp3")],
                       check=True)
        before, after = context(r)
        short, long_ = options(r)
        items.append({"id": cid, "before": before, "after": after, "verb": r["lemma"],
                      "short": short, "long": long_})
        key.append({"id": cid, "group": group, "set": r["set"], "written": r["written"],
                    "corpus": r["corpus"], "doc": r["doc"], "speaker": r["speaker"],
                    "lemma": r["lemma"], "verb": r["verb"], "win_words": r["win_words"],
                    "win_start": r["win_start"], "score": r["score"], "per": r["per"]})
    json.dump(items, open(os.path.join(out, "items.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=1)
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, "results", "listen_key.csv"), "w", newline="",
              encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(key[0]))
        w.writeheader()
        w.writerows(key)
    print(len(items), "clips;", {g: sum(k["group"] == g for k in key)
                                for g in ("flagged", "plural", "il", "control")})


if __name__ == "__main__":
    main(*sys.argv[1:])

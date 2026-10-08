"""Rescore the clean clips with a second, independent phone recognizer.

Usage: python cross_check.py SCORES_CSV CLIP_DIR OUT_CSV

Takes the clips that score_audio.py scored with a phone error rate <= 0.3 and
saved to CLIP_DIR, scores them again with facebook/wav2vec2-xlsr-53-espeak-cv-ft
(multilingual, larger, trained differently), and prints, per set, how often each
model and both models prefer the short stem.
"""
import collections, csv, os, sys

import soundfile
import torch
from transformers import AutoModelForCTC, AutoProcessor

from score_audio import clip_path

MODEL = "facebook/wav2vec2-xlsr-53-espeak-cv-ft"
MAX_PER = 0.3


def main(scores_csv, clip_dir, out_csv):
    rows = [r for r in csv.DictReader(open(scores_csv, encoding="utf-8"))
            if r["same_consonant"] == "False" and float(r["per"]) <= MAX_PER]
    proc = AutoProcessor.from_pretrained(MODEL)
    model = AutoModelForCTC.from_pretrained(MODEL).eval()
    vocab = proc.tokenizer.get_vocab()
    blank = proc.tokenizer.pad_token_id
    by_len = sorted((t for t in vocab if not t.startswith("<")), key=len, reverse=True)

    def ids(s):
        s = s.replace("ː", "").replace(" ", "").replace("ɥ", "y")  # no ɥ in this model
        out, i = [], 0
        while i < len(s):
            for t in by_len:
                if s.startswith(t, i):
                    out.append(vocab[t]); i += len(t); break
            else:
                i += 1
        return out

    def ctc(lp, s):
        t = torch.tensor(ids(s))
        return torch.nn.functional.ctc_loss(
            lp.unsqueeze(1), t.unsqueeze(0), torch.tensor([lp.shape[0]]),
            torch.tensor([len(t)]), blank=blank, reduction="sum", zero_infinity=True).item()

    out = []
    for r in rows:
        path = clip_path(clip_dir, r)
        if not os.path.exists(path):
            continue
        x = soundfile.read(path, dtype="float32")[0]
        with torch.inference_mode():
            inp = proc(x, sampling_rate=16000, return_tensors="pt").input_values
            lp = model(inp).logits.log_softmax(-1)[0]
        r["score2"] = round(ctc(lp, r["hyp_short"]) - ctc(lp, r["hyp_long"]), 2)
        out.append(r)
    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0]))
        w.writeheader()
        w.writerows(out)

    n, m1, m2, both = (collections.Counter() for _ in range(4))
    for r in out:
        k = r["set"] if r["set"] != "pl" else f"pl/{r['written']}"
        a, b = float(r["score"]) < 0, r["score2"] < 0
        n[k] += 1; m1[k] += a; m2[k] += b; both[k] += a and b
    for k in n:
        pct = lambda c: f"{c[k]:>4} ({100 * c[k] / n[k]:.0f}%)"
        print(f"{k:<10} clips {n[k]:>4}  short fits better: model 1 {pct(m1)}"
              f"  model 2 {pct(m2)}  both {pct(both)}")


if __name__ == "__main__":
    main(*sys.argv[1:])

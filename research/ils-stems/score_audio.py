"""Check in the audio whether ils/elles + two-stem verb has the long stem.

Usage: python score_audio.py TOKENS_CSV OUT_CSV [CLIP_DIR]

For each token, fetches the stretch of the recording covering a few words
around the verb (an HTTP range request on the corpus WAV), then asks a French
phone recognizer (wav2vec2 fine-tuned on French Common Voice) how well two
transcriptions of that stretch fit it. They differ only in the verb:

    long:  "dɔ̃k|il|sav|le|ʒeʁe"   (ils savent)
    short: "dɔ̃k|il|sɛ|le|ʒeʁe"    (ils sait)

score = CTC loss(short) - CTC loss(long): positive means the long stem fits better.

Three sets are scored:
  pl       every ils/elles token with a two-stem verb: the question
  sg       up to SG_PER_LEMMA il/elle/on + two-stem verb per verb: only the
           short stem is possible, so this shows how often the method wrongly
           prefers a long stem
  control  up to CONTROL_PER_VERB il/elle/on + one-form verb ending in a sound
           that is always said (il reste, il pense), scored against the same
           form minus that sound: shows how often the method misses a final
           consonant that is really there
If CLIP_DIR is given, each clip is saved there for listening.
"""
import concurrent.futures, csv, os, random, struct, sys, urllib.parse, urllib.request

import numpy as np
import soundfile
import torch
import torchaudio

import espeakng_loader
from phonemizer.backend.espeak.wrapper import EspeakWrapper
EspeakWrapper.set_library(espeakng_loader.get_library_path())
EspeakWrapper.set_data_path(espeakng_loader.get_data_path())
from phonemizer import phonemize
from transformers import AutoModelForCTC, AutoProcessor

from verbs import CONTROL, TWO_STEM

BASE = "https://repository.ortolang.fr/api/content/cefc-orfeo/latest/oral"
MODEL = "Cnam-LMSSC/wav2vec2-french-phonemizer-v2"
SG_PER_LEMMA = 30
CONTROL_PER_VERB = 20
MARGIN = 0.25  # seconds of audio kept either side of the words


def wav_url(r):
    return f"{BASE}/{r['corpus']}/{urllib.parse.quote(r['doc'])}.wav"


def wav_header(url):
    """Return (data_offset, sample_rate, channels, bytes_per_sample)."""
    req = urllib.request.Request(url, headers={"Range": "bytes=0-65535"})
    head = urllib.request.urlopen(req, timeout=60).read()
    pos, fmt = 12, None
    while pos + 8 <= len(head):
        cid, size = head[pos:pos + 4], struct.unpack("<I", head[pos + 4:pos + 8])[0]
        if cid == b"fmt ":
            _, ch, sr, _, _, bits = struct.unpack("<HHIIHH", head[pos + 8:pos + 24])
            fmt = (sr, ch, bits // 8)
        if cid == b"data":
            return (pos + 8,) + fmt
        pos += 8 + size + (size & 1)
    raise ValueError("no data chunk in first 64 kB: " + url)


def fetch_clip(url, header, start, end):
    off, sr, ch, bps = header
    frame = ch * bps
    a = off + int(max(start, 0) * sr) * frame
    b = off + int(end * sr) * frame - 1
    req = urllib.request.Request(url, headers={"Range": f"bytes={a}-{b}"})
    raw = urllib.request.urlopen(req, timeout=60).read()
    raw = raw[: len(raw) // frame * frame]
    dtype = {2: np.int16, 4: np.int32}[bps]
    x = np.frombuffer(raw, dtype=dtype).reshape(-1, ch).mean(axis=1)
    x = torch.tensor(x / np.iinfo(dtype).max, dtype=torch.float32)
    return torchaudio.functional.resample(x, sr, 16000) if sr != 16000 else x


_ipa = {}


def ipa(text):
    """Phones for a word or phrase, words separated by spaces."""
    if text not in _ipa:
        _ipa[text] = phonemize(text, language="fr-fr", backend="espeak", strip=True,
                               with_stress=False) if text else ""
    return _ipa[text]


def glue(words):
    """Join elided words to the next one (l' aime -> l'aime) and drop cut-off words.
    Returns the joined words and, for each input word, the index of its joined word."""
    out, where = [], []
    pending = ""
    for w in words:
        if "~" in w:
            where.append(None)
            continue
        where.append(len(out))
        if w.endswith("'"):
            pending += w
        else:
            out.append(pending + w)
            pending = ""
    if pending:
        out.append(pending)
    return out, where


# words espeak spells out when said alone
SPOKEN = {"y": "i", "à": "a", "a": "a", "ou": "u", "où": "u", "euh": "ø", "hum": "œm"}
LIAISON = {"ils": "z", "elles": "z", "nous": "z", "vous": "z", "les": "z", "on": "n"}


def word_ipa(w):
    w = w.lower()
    return SPOKEN.get(w) or ipa(w)


def hypotheses(r):
    """(long, short, verb's long phones, phones after the verb) for the token's
    window of words, or None if it can't be built. Words are phonemized one at a
    time so that no optional liaison is added; the only liaison kept is the
    obligatory one from a subject or object pronoun into a vowel-initial verb."""
    words = r["win_words"].split()
    v = int(r["win_verb"])
    joined, where = glue(words)
    if where[v] is None:
        return None
    k = where[v]
    phones = [word_ipa(w) for w in joined]
    verb_word = joined[k]
    prefix = verb_word[: len(verb_word) - len(words[v])]  # elided clitic glued on, e.g. l'
    if r["written"] == "control":
        long_ = phones[k]
        short = long_[:-1]
    else:
        long_ = word_ipa(prefix + TWO_STEM[r["lemma"]][0])
        short = word_ipa(prefix + TWO_STEM[r["lemma"]][1].split()[0])
    link = ""
    if k and words[v - 1].lower() in LIAISON and long_[:1] in "aeiouyøœɛɔɑə":
        link = LIAISON[words[v - 1].lower()]
    before, after = " ".join(phones[:k]), " ".join(phones[k + 1:])
    return (f"{before} {link}{long_} {after}".strip(), f"{before} {link}{short} {after}".strip(),
            long_, after)


def per(heard, ref):
    """Phone error rate of heard against ref (edit distance / length of ref)."""
    a, b = heard.replace("|", ""), ref.replace(" ", "")
    d = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        prev, d[0] = d[0], i
        for j, cb in enumerate(b, 1):
            prev, d[j] = d[j], min(d[j] + 1, d[j - 1] + 1, prev + (ca != cb))
    return d[len(b)] / max(len(b), 1)


def select(tokens_csv):
    rows = [r for r in csv.DictReader(open(tokens_csv, encoding="utf-8")) if r["win_words"]]
    rng = random.Random(1)
    pick = []
    for lemma in TWO_STEM:
        cand = [r for r in rows if r["number"] == "sg" and r["written"] == "short"
                and r["lemma"] == lemma]
        pick += rng.sample(cand, min(SG_PER_LEMMA, len(cand)))
    for form in CONTROL:
        cand = [r for r in rows if r["written"] == "control" and r["verb"].lower() == form]
        pick += rng.sample(cand, min(CONTROL_PER_VERB, len(cand)))
    pl = [r for r in rows if r["number"] == "pl" and r["lemma"] in TWO_STEM]
    for r in pl:
        r["set"] = "pl"
    for r in pick:
        r["set"] = "control" if r["written"] == "control" else "sg"
    return pl + pick


def clip_path(clip_dir, r):
    name = f"{r['set']}_{r['lemma']}_{r['doc']}_{float(r['win_start']):.2f}.wav"
    return os.path.join(clip_dir, name) if clip_dir else None


def main(tokens_csv, out_csv, clip_dir=None):
    if clip_dir:
        os.makedirs(clip_dir, exist_ok=True)
    todo = select(tokens_csv)
    cached = lambda r: clip_dir and os.path.exists(clip_path(clip_dir, r))
    headers = {}
    for url in sorted({wav_url(r) for r in todo if not cached(r)}):
        try:
            headers[url] = wav_header(url)
        except Exception as e:
            print("header failed", url, e, file=sys.stderr)
    todo = [r for r in todo if cached(r) or wav_url(r) in headers]

    def get(r):
        if cached(r):
            return torch.tensor(soundfile.read(clip_path(clip_dir, r), dtype="float32")[0])
        try:
            return fetch_clip(wav_url(r), headers[wav_url(r)],
                              float(r["win_start"]) - MARGIN, float(r["win_end"]) + MARGIN)
        except Exception as e:
            print("fetch failed", r["doc"], r["win_start"], e, file=sys.stderr)
            return None

    with concurrent.futures.ThreadPoolExecutor(8) as pool:
        clips = list(pool.map(get, todo))

    proc = AutoProcessor.from_pretrained(MODEL)
    model = AutoModelForCTC.from_pretrained(MODEL).eval()
    vocab = proc.tokenizer.get_vocab()
    blank = proc.tokenizer.pad_token_id
    inv = {i: t for t, i in vocab.items()}
    by_len = sorted((t for t in vocab if not t.startswith("<")), key=len, reverse=True)

    # Word boundaries are ignored when scoring: the recognizer often hears a final
    # consonant at the start of the next word (ils connaissent la -> kɔnɛ|sa), as
    # French links it there. Its word-boundary symbol is folded into blank.
    sep = vocab.get("|")

    def ids(s):
        s = s.replace("ː", "").replace(" ", "")
        out, i = [], 0
        while i < len(s):
            for t in by_len:
                if s.startswith(t, i):
                    out.append(vocab[t]); i += len(t); break
            else:
                i += 1  # symbol the model doesn't have: drop it
        return out

    def ctc(lp, s):
        if sep is not None:
            lp = lp.clone()
            lp[:, blank] = torch.logaddexp(lp[:, blank], lp[:, sep])
            lp[:, sep] = -float("inf")
        t = torch.tensor(ids(s))
        return torch.nn.functional.ctc_loss(
            lp.unsqueeze(1), t.unsqueeze(0), torch.tensor([lp.shape[0]]),
            torch.tensor([len(t)]), blank=blank, reduction="sum", zero_infinity=True).item()

    fields = list(todo[0]) + ["hyp_long", "hyp_short", "same_consonant", "heard", "score", "per"]
    with open(out_csv, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        for n, (r, x) in enumerate(zip(todo, clips)):
            if n % 250 == 0:
                print(f"{n}/{len(todo)}", file=sys.stderr, flush=True)
            if x is None or len(x) < 3200:
                continue
            h = hypotheses(r)
            if h is None:
                continue
            r["hyp_long"], r["hyp_short"], long_, after = h
            # next word starts with the long stem's final consonant: can't tell apart
            r["same_consonant"] = after[:1] == long_[-1:]
            with torch.inference_mode():
                inp = proc(x.numpy(), sampling_rate=16000, return_tensors="pt").input_values
                lp = model(inp).logits.log_softmax(-1)[0]
            r["heard"] = "".join(inv[int(i)] for i in torch.unique_consecutive(lp.argmax(-1))
                                 if int(i) != blank)
            r["score"] = round(ctc(lp, r["hyp_short"]) - ctc(lp, r["hyp_long"]), 2)
            # how well the recognizer heard the window at all (lower is better)
            r["per"] = round(min(per(r["heard"], r["hyp_long"]), per(r["heard"], r["hyp_short"])), 3)
            w.writerow(r)
            if clip_dir and not cached(r):
                soundfile.write(clip_path(clip_dir, r), x.numpy(), 16000)


if __name__ == "__main__":
    main(*sys.argv[1:])

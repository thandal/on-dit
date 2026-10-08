# Research

Checks of the grammar's claims against real speech. Each folder takes one question, with the scripts, the method, and what came out. Downloaded data stays out of the repo; each folder says how to fetch it again.

| Folder | Question | Short answer |
| --- | --- | --- |
| [`ils-stems/`](ils-stems/) | Do people say *ils part* instead of *ils partent*, using the short stem for *ils* (4.2)? | No. In conversation recorded in France, 0.7% of cases in the transcripts show it, mostly slips, and the audio confirms the transcripts. 4.2 stands. |

## Data sources

- **CEFC-ORFEO** (Corpus d'Étude pour le Français Contemporain): about 4 million words of transcribed speech (3.2 million recorded in France), aligned word by word with the audio, plus written texts. Free on [ORTOLANG](https://www.ortolang.fr/market/corpora/cefc-orfeo), licence CC BY-NC-SA. Its spoken part bundles older corpora: CFPP2000 (Paris interviews), CLAPI (everyday interaction), CRFP (reference corpus of spoken French), TCOF (Lorraine), TUFS (interviews), C-ORAL-ROM, DECODA (phone calls to the Paris transport help line), FLEURON (university life), French Oral Narrative (storytelling) and work meetings. Belgian (CFPB, VALIBEL) and Swiss (OFROM) speech is also in it; we leave those out.

## Tools

The audio checks use a phone recognizer, [Cnam-LMSSC/wav2vec2-french-phonemizer-v2](https://huggingface.co/Cnam-LMSSC/wav2vec2-french-phonemizer-v2) (MIT licence), and espeak-ng for expected pronunciations. Install into a virtualenv:

```sh
python3 -m venv venv
venv/bin/pip install --index-url https://download.pytorch.org/whl/cpu torch torchaudio
venv/bin/pip install transformers numpy soundfile phonemizer espeakng-loader
```

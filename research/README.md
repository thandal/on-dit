# Research

Checks of the grammar's claims against what is known about real speech. Each folder takes one question, with its sources, any scripts, and what came out. Downloaded data stays out of the repo; each folder says how to fetch it again.

## Method

1. **Start from the literature.** Find what published research already knows: corpus studies, variationist work, reference grammars of spoken French. Report the rates and the factors that matter, say where studies disagree, and cite them in full with links. Note when a finding comes from Canada, Belgium or Switzerland and may not carry over to France.
2. **Count in a corpus only to fill a gap** the literature leaves, and label those counts as transcript-only: transcribers write standard forms, so anything that differs only in sound may be normalized away.
3. **Check recordings only as a last resort.** It's slow, and the automatic methods have real confounds (noisy audio, the recognizer's own biases). [`ils-stems/`](ils-stems/) shows what it takes.

Each README gives the question, the answer, what it means for the grammar, what the research says, any corpus check, and the sources.

| Folder | Question | Short answer |
| --- | --- | --- |
| [`ils-stems/`](ils-stems/) | Do people say *ils part* instead of *ils partent*, using the short stem for *ils* (4.2)? | No. In conversation recorded in France, 0.7% of cases in the transcripts show it, mostly slips, and the audio confirms the transcripts. 4.2 stands. |
| [`participles/`](participles/) | With avoir, do speakers make the participle agree (*la lettre que j'ai écrite*) (5.4)? | Optional: about a third to a half of the time in France, more in careful speech. With être, over 90%. The 5.4 note should call it optional. |
| [`futur/`](futur/) | How often is the futur simple used instead of the futur proche, and where (5.6, 6.4)? | About 40% of futures. It's the verb that decides (*ce sera, il y aura, on pourra, il faudra*), plus negation with *jamais, rien, plus*; "promises and predictions" isn't a reliable cue. 6.4 should change. |
| [`subjunctive/`](subjunctive/) | Is the subjunctive really used after its triggers (6.5)? | Yes: 90–100% after the main triggers in France, stable since 1968. 6.5 stands; add *qu'il y ait*. |
| [`ne/`](ne/) | Is *ne* "almost always left out" (7.1)? | Yes: 2–10% in informal speech in France, much more in public speech and after a noun subject. 7.1 stands. |
| [`survey/`](survey/) | What else does the literature say speech does differently? | Most of the grammar holds up. Ranked candidates: *c'est quoi ?*, *faut* without *il*, no tie after *est*, softer "never" and "normal way" claims, a few "you'll hear" notes. |
| [`dont/`](dont/) | Do speakers avoid *dont* (10.4)? | Only as "whose" and "including". With the verbs 10.4 teaches it's still the usual choice; plain *que* (*ce que t'as besoin*) is the main alternative, *que j'en ai besoin* barely occurs. 10.4 stands; add *la façon dont*. |

## Data sources

- **CEFC-ORFEO** (Corpus d'Étude pour le Français Contemporain): about 4 million words of transcribed speech (3.2 million recorded in France), aligned word by word with the audio, plus written texts. Free on [ORTOLANG](https://www.ortolang.fr/market/corpora/cefc-orfeo), licence CC BY-NC-SA. Its spoken part bundles older corpora: CFPP2000 (Paris interviews), CLAPI (everyday interaction), CRFP (reference corpus of spoken French), TCOF (Lorraine), TUFS (interviews), C-ORAL-ROM, DECODA (phone calls to the Paris transport help line), FLEURON (university life), French Oral Narrative (storytelling) and work meetings. Belgian (CFPB, VALIBEL) and Swiss (OFROM) speech is also in it; we leave those out.

## Tools

[`orfeo.py`](orfeo.py) reads the CEFC-ORFEO transcripts (sentences, tokens, speaker metadata); every corpus count uses it. The audio checks use a phone recognizer, [Cnam-LMSSC/wav2vec2-french-phonemizer-v2](https://huggingface.co/Cnam-LMSSC/wav2vec2-french-phonemizer-v2) (MIT licence), and espeak-ng for expected pronunciations. Install into a virtualenv:

```sh
python3 -m venv venv
venv/bin/pip install --index-url https://download.pytorch.org/whl/cpu torch torchaudio
venv/bin/pip install transformers numpy soundfile phonemizer espeakng-loader
```

## Changes made to the grammar

Each change rests on primary sources read in full, or on our own hand-checked corpus counts. The survey's proposals were checked against their primary sources first, in [`survey/checks/`](survey/checks/).

- 5.4, "More: agreement with avoir": the agreement is optional (*la lettre que j'ai écrit* is at least as common); A5 to match ([participles](participles/)).
- 5.4: a "you'll hear" note for *j'ai été* = *je suis allé* ([check](survey/checks/misc.md)).
- 6.4, with 5.1, 5.6 and A6: the futur simple is about four futures in ten, the usual future of *être, avoir, pouvoir, savoir, falloir*, and common in negatives with *jamais, rien, plus*; "promises and predictions" dropped; *il y aura*, *il faudra* added to the fixed phrases ([futur](futur/)).
- 11.5: *on va dire* ("let's say") ([futur](futur/)).
- 6.5: *que ce soit* and *qu'il y ait* as the commonest subjunctives ([subjunctive](subjunctive/)).
- 6.3 and 5.2: verbs with *è* in the *je* form keep it in the conditionnel (*j'achèterais*). A correction, not a finding about variation ([survey](survey/), section 11).
- 7.1, "More: ne": *ne* survives mostly after a noun subject ([ne](ne/)).
- 8.2: *comment* and *pourquoi* usually go first; 8.3: *c'est quoi ?* for "what is it?"; 8.4: two recognition notes ([check](survey/checks/questions.md)).
- 1.7 and the README notation: *faut* without *il* is a relaxed form, like *y a*; examples converted throughout ([check](survey/checks/sounds.md)).
- 1.6: some ties are optional (after *est* before a participle, after *quand*); *la porte est ouverte* lost its tie ([check](survey/checks/sounds.md)).
- 9.1: both orders are normal; topic first is very common in relaxed talk, plain order in careful talk ([check](survey/checks/misc.md)).
- 10.6: *que* is almost always kept, with a "you'll hear" line for *je crois c'est fermé* ([check](survey/checks/misc.md)).
- 10.4: *la façon dont*; a "you'll hear" note for *que* without *de* ([dont](dont/)).
- 3.3: *tu* for people in general ([check](survey/checks/misc.md)).
- A10: *dont* meaning "whose" is mainly written ([dont](dont/), [check](survey/checks/misc.md)).

**Not made**, because the primary sources didn't support them:

- Dropping the ties after *est* before a participle (*il est‿allé*): speakers make that link about three times in four. The survey's 44% counted *est* before any word ([check](survey/checks/sounds.md)).
- *dont* meaning "including" as mainly written: no published study counts it; only our small sample ([check](survey/checks/misc.md)).
- Framing topic-first by age: the situation matters as much as age ([check](survey/checks/misc.md)).

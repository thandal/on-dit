# ils with the short stem

**Question.** Section 4.2 teaches that two-stem verbs use the long stem for ils: *ils partent*, *ils prennent*, *ils peuvent*. Do people in France actually say that, or do they often level it to the short stem, *ils part*, *ils prend*, *ils peut*?

**Answer.** They say the long stem. In about 2,300 cases of ils/elles + a two-stem verb in transcribed conversation recorded in France, the transcript shows the short stem 16 times (0.7%), and most of those are slips the speaker corrects (*ils vit… ils vivent*). An audio check finds no hidden *ils part* behind the transcripts. At most a few percent of plural verbs lose the stem consonant, and that looks like fast-speech reduction rather than a different form (see [Audio](#audio)). The short stem with ils is a feature of children, learners, and French in minority settings outside France, not of adult speech in France. One place where speakers in France do sometimes drop the plural is after *qui* with a plural antecedent (*ceux qui veut*, "the ones who wants"), in up to about 3% of cases.

**For the grammar.** 4.2 stands as written. Nothing here is common enough for a "you'll hear" note.

## Data

The spoken part of [CEFC-ORFEO](https://www.ortolang.fr/market/corpora/cefc-orfeo) recorded in France: CFPP2000, CLAPI, C-ORAL-ROM, CRFP, DECODA, FLEURON, French Oral Narrative, work meetings, TCOF and TUFS. About 3.2 million words; the hits below come from about 740 different speakers. Every word is tagged (lemma, part of speech) and time-aligned to the audio. Belgian and Swiss recordings are left out.

## Transcripts

[`extract.py`](extract.py) finds every subject pronoun followed (after any *ne* or object pronouns) by a present-tense verb from [`verbs.py`](verbs.py): the verbs of 4.2, plus *dire* and *savoir*, plus a few others with the same pattern (*servir, sentir, réussir, vendre, perdre, descendre, rendre, tenir, devenir, revenir, apprendre*…). It sorts each by whether the transcript spells the verb with the ils form or a singular form.

| ils / elles + | ils form | singular form | singular |
| --- | ---: | ---: | ---: |
| two-stem verb (4.2) | 2,281 | 16 | 0.7% |
| être, avoir, aller, faire | 9,007 | 16 | 0.2% |

Per verb: [`results/transcript_counts.csv`](results/transcript_counts.csv). The 32 singular hits: [`results/ils_short_in_transcripts.csv`](results/ils_short_in_transcripts.csv). By hand:

- Self-corrections: *ils vit ils vivent*, *ils dit ils croivent*, *ils vont ils peut pas*.
- *ils a* + another verb (*ils a connaissent*, *ils a voient*): a hesitation or mishearing, not a verb form.
- A CFPP interviewer, once: *ils vient en pour l'instant*.
- One speaker uses it consistently: *ils nous apprend la culture* three times (CRFP).
- A handful of one-offs: *ils sait les gérer*, *ils veut faire*, *ils attends*.

All 14 speakers are listed with French as their first language.

### After qui

[`relatives.py`](relatives.py) does the same for a plural antecedent + *qui* + verb (*ceux qui*, *les gens qui*, *des mots qui*…). This is the one context where the literature reports singular agreement in informal French generally ([King & LeBlanc](https://journals.lib.unb.ca/index.php/la/article/view/22486)).

| plural antecedent + qui + | plural form | singular form | singular |
| --- | ---: | ---: | ---: |
| two-stem verb | 403 | 13 | 3.1% |
| être, avoir, aller, faire | 1,481 | 40 | 2.6% |

That's an upper bound. The heuristic still picks up some phrases whose head is really singular (*de mes garçons qui vient*, probably "un de mes garçons"), and spoken *qui* and *qu'il* sound the same, so *des trucs qui comprend mal* is probably *des trucs qu'il comprend mal*. Clear cases exist, though: *ceux qui veut dormir*, *y a des mots qui sort*, *des gens qui dit*, *c'est les doubleurs qui fait*.

## Audio

The worry with transcripts: a transcriber who hears "i par" and knows the subject is plural may well write *ils partent*. If transcribers wrote the standard form whatever was said, short stems would be invisible in the text.

[`score_audio.py`](score_audio.py) checks the recordings. For each token it downloads just the few seconds around the verb (an HTTP range request on the corpus WAV) and asks a French phone recognizer ([Cnam-LMSSC/wav2vec2-french-phonemizer-v2](https://huggingface.co/Cnam-LMSSC/wav2vec2-french-phonemizer-v2)) which of two transcriptions fits the audio better, the long-stem one or the short-stem one. Everything else in the window is the same in both. Words are phonemized one at a time by espeak-ng, so no optional liaison is added to one side only.

Conversational recordings are noisy (overlapping speakers, laughter, fast speech), and when the recognizer can't make out a stretch, the shorter candidate tends to win by default. So two controls are scored the same way:

- **il (short only):** *il/elle/on* + the same verbs, where only the short stem is possible. Shows how often the method wrongly prefers a long stem.
- **control (consonant said):** *il/elle/on* + a one-form verb ending in a consonant that is always said (*il reste*, *il pense*, *il travaille*), against the same word minus that consonant. Shows how often the method misses a consonant that is really there.

Clips are also filtered by how well the recognizer heard the whole window (phone error rate, PER, against the better of the two transcriptions). Tokens whose next word starts with the stem's consonant (*ils mettent tout*) are left out. Word boundaries are ignored when scoring, because French carries a final consonant over to a following vowel and the recognizer hears it there (*ils connaissent la* comes out as "kɔnɛ|sa").

3,573 clips were scored: 2,114 ils/elles, 992 il (short only), 467 control. 134 are left out of the tables because the next word starts with the stem's consonant. DECODA's audio couldn't be fetched (the server returns errors for its file names).

**How often the short stem fits the audio better** (model 1, [`results/audio_summary.csv`](results/audio_summary.csv)):

| set | all clips | PER ≤ 0.3 | PER ≤ 0.2 |
| --- | ---: | ---: | ---: |
| ils + verb, written long | 52% of 1,945 | 18% of 239 | 15% of 92 |
| il + verb (short only) | 95% of 925 | 96% of 170 | 98% of 81 |
| control: consonant said | 40% of 429 | 5% of 92 | 3% of 38 |

On the full set the recognizer is too unreliable to say anything: it misses 40% of consonants that are really there. On clean clips it's good, and two things stand out:

1. **There is no hidden *ils part*.** If transcribers had been writing *ils partent* for what was really "i par", those clips would score like the short-only control, around 95% short. They score around 18%.
2. **The remaining gap is small and depends on the model.** Clean plural clips prefer the short stem more often than the control (18% against 5%). A second, independent recognizer ([`cross_check.py`](cross_check.py), facebook/wav2vec2-xlsr-53-espeak-cv-ft) doesn't confirm it:

| clean clips (PER ≤ 0.3) | n | model 1 short | model 2 short | both |
| --- | ---: | ---: | ---: | ---: |
| ils + verb, written long | 239 | 18% | 18% | 8% |
| control: consonant said | 92 | 5% | 20% | 4% |
| il + verb (short only) | 170 | 96% | 94% | 90% |

Model 2 misses real consonants as often as it prefers the short stem after ils. Where both models agree, it's 8% against 4%. So at most a few percent of plural verbs come out without their stem consonant. In the clips flagged, that mostly looks like fast-speech reduction before another consonant (*ils doivent les conserver* heard as "dwa le", *ils ne peuvent pas* as "pø pa"), not a different form. [`results/listen.csv`](results/listen.csv) lists the 45 clean plural clips where model 1 prefers the short stem, with file and time, for checking by ear.

## Literature

No study I could find measures this in France. What exists:

- **Ontario.** Mougeon & Beniak document *ils prend pas l'autobus*-type forms, mostly among speakers for whom French isn't the dominant language ("restricted" speakers) ([summary](https://uoh.concordia.ca/sociolinguistique/module3/module3_66.html); Mougeon & Beniak 1991, *Linguistic Consequences of Language Contact and Restriction*, ch. 5; Beniak & Mougeon 1995, [*Présence francophone* 46](https://icrml.ca/en/research-and-publications/references/item/79935-le-non-accord-entre-sujet-et-verbe-en-francais-ontarien-un-cas-de-simplification)).
- **Newfoundland and Acadian French.** King finds default singular agreement in subject relatives with a plural head ([King 1994, *Language Variation and Change* 6:3](https://doi.org/10.1017/S0954394500001678)), and King & LeBlanc note the same tendency in informal French generally.
- **Learners and children.** *ils prend* is a standard error even for advanced adult learners ([Schlyter, in Kail & Hickmann](https://benjamins.com/catalog/lald.52.17sch); ["Les copains *dit au revoir"](https://doi.org/10.3390/languages6010007)).
- **France.** Variationist work on agreement in France is about collective nouns, *la foule est / sont* ([Tristram 2015](https://benjamins.com/catalog/rro.50.2.02tri)), not about ils. The non-standard pressure in France that is well known runs the other way: *ils croivent* for *ils croient* adds a long stem where the standard has none.

## Rerunning

```sh
sh fetch.sh data                                  # transcripts, ~140 MB zipped
python3 extract.py data/cefc data/out             # tokens.csv, transcript counts
python3 relatives.py data/cefc
venv/bin/python score_audio.py data/out/tokens.csv data/out/scores.csv data/clips
python3 summarize.py data/out/scores.csv results
venv/bin/python cross_check.py data/out/scores.csv data/clips data/out/cross_check.csv
```

`score_audio.py` and `cross_check.py` need the packages listed in [`../README.md`](../README.md). The first downloads about 3,500 short clips (into `data/clips`, reused on later runs) and takes about 20 minutes on a 4-core CPU.

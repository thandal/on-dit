# On dit

*A grammar of spoken French.*

A learner's grammar of contemporary spoken French, written from the sound up. It teaches what people actually say, not the written language read aloud.

Few existing resources focus only on spoken French. The closest is Rodney Ball's *Colloquial French Grammar*; Blanche-Benveniste and Gadet cover it academically. None of them starts from sound, and that is where most of the simplification lies.

## Scope

- **Variety:** contemporary France French.
- **Register:** neutral informal, the everyday speech of educated adults (*je sais pas*, *on y va*, *t'es où ?*). Slang appears only in occasional "you'll hear" notes.
- **Audience:** learners who want to follow and take part in real conversation.

## Principles

1. **Sound comes first.** Rules describe what you hear and say.
2. **Teach the spoken forms directly.** Chapters never explain speech as a simplification of writing. All comparison with written French goes in the appendix, which each chapter links to.
3. **One default per job.** Teach the most common way to say something. List other forms briefly, for recognition only.
4. **Speech has its own structures.** Relaxed forms, linking, dislocation, clefts and discourse words are core grammar here.
5. **Recognize more than you produce.**

## Notation: the spoken spelling

The goal is that every example can be read aloud correctly using a one-page set of reading rules (chapter 1), without needing to know French grammar, and that each spoken form has exactly one spelling.

| Mark | Meaning | Example |
| --- | --- | --- |
| no mark | The word is read by the rules, and that is also its standard spelling. | `je parle`, `vous parlez`, `qu'on parte` |
| orange | Written differently from its standard spelling: either forms that sound the same are written once, or the rules can't predict the standard spelling's sound. Tap it to see the standard spelling. | `tu parle` (*tu parles*), `il peu` (*il peut*), `ils parte` (*ils partent*), `chui` (*je suis*) |
| `‿` | Linked: the first word's final consonant is said at the start of the next (liaison). | `ils‿ont`, `on‿y va`, `vous‿avez` |

Orange is shown with a dotted underline too, so the mark survives without colour.

Guidelines:

- **One spelling per sound.** When standard spelling writes one sound several ways, write it one way:
  - **Verbs:** spell the shared form as the reading rules say it, with no silent letters: *peu* (peux, peut), *veu*, *fè* (fais, fait), *sè*, *di*, *par* (pars, part), *pren*, *è* (es, est: *c'è*, *il è*), *parlè* (parlais, parlait, parlaient), *voudrè* (voudrais, voudrait). Where one standard spelling already reads right with no silent letters, use it for every person: *parle* (parle, parles, parlent), *fini*, *va*, *a*.
  - **Nouns, adjectives, participles and the determiners quel, leur and tout:** use the singular, and the masculine when the feminine sounds the same: *les livre*, *elle è fatigué*, *des voiture rouge*, *quel heure*. Only when they really sound the same: *petite*, *des journaux* stay. Don't merge different words or stem alternants (*beau / bel / belle*).
  - **Pronouns and articles keep their spelling:** *ils parle*, *les livre*, *celles*, *les miens*.
  - **In a table cell that covers several persons,** write the bare form with no pronoun (*voi* under "je, tu, il, on, ils"); tapping it lists each person's standard spelling. A cell for one person keeps its pronoun, so linking stays visible (*ils‿écrive*, *vous‿avez*). Don't make a cell orange when every person it covers has the same standard spelling (*a* for il, elle, on).
  - **Where linking makes an ending heard, it isn't silent:** *les petits‿enfants* keeps its s.
- **Respell where the rules can't predict the sound:** long stems (*ils parte*, *ils vienne*), relaxed forms, irregular words and some numbers, below.
- **Respell these relaxed forms:** *chui, chais, t'è, t'a, t'avè, y a, y avè, y en‿a, pasque*.
- **Don't respell regular reductions.** These are covered by rules instead: dropping the light *e* (*j'veu*, *p'tit*) and *il/ils* sounding like "i" before a consonant.
- **Use a fixed list of irregular words, always orange:** *fam (femme), messieu (monsieur), u (eu), pluss (plus, "more" as an amount), touss (tous), fiss (fils), segon (second), ièr (hier), ivèr (hiver), vil (ville), mil (mille), tranquil (tranquille)*.
- **Respell numbers where they differ from the rules:** cinq and sept always (*sink, sète*), six, huit and dix when said alone (*siss, uite, diss*), soixante (*soissante*), vingt in 22–29 (*vinte-deux*), and the ordinals and -aine forms that spelling misleads (*deuzième, sizième, sètième, dizième, vintième, vintaine*). See chapter 12.
- **Show linking with the tie only, never by respelling.** Mark all obligatory liaisons plus a few very common optional ones.

## Presentation

The grammar is a small static site in `grammaire/`, published as an artifact. Open `grammaire/index.html` in a browser to read it locally.

| File | Contents |
| --- | --- |
| `index.html` | Title page: how this grammar works, and the outline |
| `01-sons.html` | Chapter 1: Sounds and spelling |
| `02-noms.html` | Chapter 2: Nouns, articles, gender and number |
| `03-pronoms.html` | Chapter 3: Pronouns |
| `04-present.html` | Chapter 4: Verbs: the present |
| `05-passe-futur.html` | Chapter 5: Verbs: the everyday past and future |
| `06-autres-temps.html` | Chapter 6: Verbs: other common forms |
| `07-negation.html` | Chapter 7: Negation |
| `08-questions.html` | Chapter 8: Questions |
| `09-forme.html` | Chapter 9: Sentence shape |
| `10-relier.html` | Chapter 10: Joining ideas |
| `11-mots.html` | Chapter 11: Discourse words |
| `12-quotidien.html` | Chapter 12: Everyday frames |
| `13-lieu-temps.html` | Chapter 13: Place and time |
| `annexe.html` | Appendix: Coming from written French (A0, A1, A2…) |
| `listes.html` | Appendix: useful lists: être verbs, reflexive verbs, verbs + à / de / infinitive, subjunctive triggers, participles, adjectives before the noun, avoir and faire expressions, everyday informal words |
| `on-dit.css` | Shared styles |
| `on-dit.js` | Shared script: contents and previous/next links, orange words, Written forms switch |

- **Written forms switch** (top bar): shows or hides the standard spelling. When on, it appears above every orange word, and the "Written" columns appear in tables. The setting is remembered per browser, so it carries from page to page.
- **Tap to reveal:** tapping an orange word shows its standard spelling. In a table cell that covers several persons, it shows each person's spelling.
- **Key examples** have three lines: what's said, what's written (shown only with the switch on), and what it means plus which form it is.
- **Practice** sits at the end of the section it drills, folded away so the chapter reads straight through. Each item has an "answer" chip; tapping it shows the answer in place.
- **Each chapter** ends with a link to its appendix section. Each appendix section links back to its chapter.

### Adding a chapter

1. Copy an existing chapter page and name it `NN-slug.html`, with a short French slug (`02-noms.html`, `03-pronoms.html`).
2. Set `data-page` on `<body>` and the `<title>`.
3. Add the page to `PAGES` at the top of `on-dit.js`, in reading order. The contents rail and the previous/next links are built from that list.
4. Link it from the outline in `index.html` and update its status there and in the table below.
5. Add its appendix section to `annexe.html` (`id="aN"`), with a link back to the chapter.
6. Put any reference list worth looking up (verbs that take a preposition, irregular forms…) in `listes.html`, and link the section and the list to each other.

Section headings follow one pattern: a section about particular words gives the French first, then its meaning (`9.3 quand, si, avant de: when, if, before`); a section about a concept has a plain English heading in sentence case (`9.6 Reporting what people say`). Numbered section headings take an id of the form `s4-1`; they and any `h2` with an id appear in the contents rail under the current page.

### Authoring syntax

In the HTML source, an orange word is written as `{spoken|written}`, for example `ils {parte|partent}`. When one token stands for several persons, list each person's spelling in the written part, separated by ` · `: `{par|je pars · tu pars · il part · on part}`. `on-dit.js` turns each one into a `<ruby>` annotation. Write ties (`‿`) directly. Put French examples (anything a reader would say) in `<span class="fr">`, wherever they appear, including inside an English table cell; French used only as a label (a row header like *je, tu*, or a term like *passé composé*) stays plain. Put standard-spelling-only text in `<span class="wf">`, and spoken table cells in `<td class="say">`. Give written-only table columns `class="w"`. Mark a common mistake with `<span class="no">` (shown in red after a ✗, never taught as a form to use). Put detail that would interrupt the main line in `<details class="more"><summary>More: …</summary>…</details>`. Put a section's exercises in `<details class="practice"><summary>Practice: …</summary>…</details>` at the end of the section, and each answer at the end of its item in `<span class="a">…</span>`.

## Chapter plan and status

| # | Chapter | Status |
| --- | --- | --- |
| 1 | Sounds and spelling | Reading rules drafted |
| 2 | Nouns, articles, gender and number | Drafted |
| 3 | Pronouns | Drafted |
| 4 | Verbs: the present | Drafted |
| 5 | Verbs: the everyday past and future | Drafted |
| 6 | Verbs: other common forms | Drafted |
| 7 | Negation | Drafted |
| 8 | Questions | Drafted |
| 9 | Sentence shape | Drafted |
| 10 | Joining ideas | Drafted |
| 11 | Discourse words | Drafted |
| 12 | Everyday frames | Drafted |
| 13 | Place and time | Drafted |

Chapters 2 to 13 have practice and an appendix section. Chapter 1 has neither yet.

## Next steps

- Chapter 1: cover linking and relaxed forms in more depth, and add practice.
- Chapter 1: decide how to handle -er words read as èr (hiver, super) and -ied (pied). For now they're respelled or avoided.
- Review the whole grammar with a native speaker, who should know the one-spelling-per-sound notation is deliberate. Chapters 6 to 13 and sections 2.9, 3.8–3.11 and 4.6 haven't had any review yet.

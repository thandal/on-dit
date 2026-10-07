# On dit

*A grammar of spoken French.*

*On dit* means "people say", which is the project's whole claim: it teaches what's said. It also starts with *on*, the spoken default for "we". The grammar is written in English because the explanations need a neutral language to describe how speech departs from the written standard; the name is French.

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

The goal is that every example can be read aloud correctly using a one-page set of reading rules (chapter 1), without needing to know French grammar.

| Mark | Meaning | Example |
| --- | --- | --- |
| no mark | The word is read by the rules, and that is also its standard spelling. | `je pars`, `vous parlez`, `qu'on parte` |
| `*` | Respelled with ordinary French letters because the rules can't predict its sound. | `ils parte*` (*ils partent*), `chui*` (*je suis*) |
| `‿` | Linked: the first word's final consonant is said at the start of the next (liaison). | `ils‿ont`, `on‿y va`, `vous‿avez` |

Guidelines:

- **Respell as little as possible.** Keep standard spelling wherever the reading rules work. This keeps stars rare, so each one signals a place where writing misleads (mostly *ils* verb endings and relaxed forms).
- **Respell these relaxed forms:** *chui, chais, t'es, t'as, t'avais, y a, y avait, pasque*.
- **Don't respell regular reductions.** These are covered by rules instead: dropping the light *e* (*j'veux*, *p'tit*) and *il/ils* sounding like "i" before a consonant.
- **Use a fixed list of irregular words, always starred:** *fam\* (femme), messieu\* (monsieur), u\* (eu), pluss\* (plus, "more"), touss\* (tous), fiss\* (fils), segon\* (second)*.
- **Show linking with the tie only, never by respelling.** Mark all obligatory liaisons plus a few very common optional ones.

## Presentation

The grammar is a small static site in `grammaire/`, published as an artifact. Open `grammaire/index.html` in a browser to read it locally.

| File | Contents |
| --- | --- |
| `index.html` | Title page: how this grammar works, and the outline |
| `01-sons.html` | Chapter 1: Sounds and spelling |
| `04-present.html` | Chapter 4: The present, with its exercises |
| `05-passe-futur.html` | Chapter 5: Past, future and possibility, with its exercises |
| `annexe.html` | Appendix: Coming from written French (A0, A1, A4, A5…) |
| `on-dit.css` | Shared styles |
| `on-dit.js` | Shared script: contents and previous/next links, starred words, Written forms switch |

- **Written forms switch** (top bar): shows or hides the standard spelling. When on, it appears above every starred word, and the "Written" columns appear in tables. The setting is remembered per browser, so it carries from page to page.
- **Tap to reveal:** tapping a single starred word shows just its written form.
- **Key examples** have three lines: what's said, what's written (shown only with the switch on), and what it means plus which form it is.
- **Each chapter** ends with its exercises (answers in a collapsible block) and a link to its appendix section. Each appendix section links back to its chapter.

### Adding a chapter

1. Copy an existing chapter page and name it `NN-slug.html`, with a short French slug (`02-noms.html`, `03-pronoms.html`).
2. Set `data-page` on `<body>` and the `<title>`.
3. Add the page to `PAGES` at the top of `on-dit.js`, in reading order. The contents rail and the previous/next links are built from that list.
4. Link it from the outline in `index.html` and update its status there and in the table below.
5. Add its appendix section to `annexe.html` (`id="aN"`), with a link back to the chapter.

Numbered section headings take an id of the form `s4-1`; they and any `h2` with an id appear in the contents rail under the current page.

### Authoring syntax

In the HTML source, a starred word is written as `{spoken*|written}`, for example `ils {parte*|partent}`. `on-dit.js` turns each one into a `<ruby>` annotation. Write ties (`‿`) directly. Put French in running text in `<span class="fr">`, standard-spelling-only text in `<span class="wf">`, and spoken table cells in `<td class="say">`. Give written-only table columns `class="w"`.

## Chapter plan and status

| # | Chapter | Status |
| --- | --- | --- |
| 1 | Sounds and spelling | Reading rules drafted |
| 2 | Nouns, articles, gender and number | Planned |
| 3 | Pronouns | Planned |
| 4 | Verbs I: the present | Drafted |
| 5 | Verbs II: past, future and possibility | Drafted |
| 6 | Negation | Planned |
| 7 | Questions | Planned |
| 8 | Sentence shape | Planned |
| 9 | Joining ideas | Planned |
| 10 | Discourse words | Planned |
| 11 | Everyday frames | Planned |

Chapters 4 and 5 each end with exercises and an answer key.

## Next steps

- Finish chapter 1 (linking and relaxed forms in more depth).
- Draft chapters 2 and 3, which chapter 4 already refers to.
- Add exercises and an appendix section for each new chapter.

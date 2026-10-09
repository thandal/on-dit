# Working on On dit

The README covers the project's goals, notation, file layout and authoring syntax. Read it first.

## Process

- Work directly on `main`. No feature branches, no pull requests.
- After changing anything in `grammaire/`, republish it to the preview artifact before committing:
  - URL: https://claude.ai/artifact/EypYPVNf24W89bMXBW8xH1
  - Publish `grammaire/index.html` with `url` set to the link above, and pass the other pages, `on-dit.css` and `on-dit.js` through `files` under their bare names (`04-present.html`, …). Include any new chapter page.
- Commit and push to `main` when a change is done. The user reviews the preview and asks for follow-ups.

## Writing

- Keep prose about the grammar itself. No paragraphs explaining the project to itself (what the name means, why it's in English).
- The site has no project status (what's drafted, what's planned). Status lives only in the README.
- Assume no prior French. When a word or example's meaning matters to the point, say what it means, even for common words (nous = "we", pas = "not").
- Err on the side of explicit. Never leave a form for the reader to work out: when you give a verb's forms, give every person, including vous and ils, and say which ones sound alike.
- Cross-link generously. When prose mentions a concept taught elsewhere (a section, a list in `listes.html`, a reading rule), link it there, at least on its first mention in each section. Section numbers like (4.2) are always links.
- Follow the notation rules in the README: one spelling per sound, every word written differently from its standard spelling marked orange (`{spoken|written}`), and liaison shown only with ‿.
